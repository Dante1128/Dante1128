import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("profile_cards", ROOT / ".github/scripts/update_profile.py")
profile_cards = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile_cards)


class ProfileCardsTests(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads((ROOT / "assets/github-data.json").read_text(encoding="utf-8"))

    def test_rejects_incomplete_or_inconsistent_calendar(self):
        profile_cards.validate_profile(self.profile)
        bad = copy.deepcopy(self.profile)
        bad["contributionsCollection"]["contributionCalendar"]["totalContributions"] += 1
        with self.assertRaisesRegex(ValueError, "does not match"):
            profile_cards.validate_profile(bad)
        bad = copy.deepcopy(self.profile)
        bad["contributionsCollection"]["contributionCalendar"]["weeks"].pop()
        with self.assertRaises(ValueError):
            profile_cards.validate_profile(bad)

    def test_calendar_keeps_every_real_day_and_count(self):
        svg = ET.fromstring(profile_cards.render_calendar(self.profile))
        ns = {"s": "http://www.w3.org/2000/svg"}
        rendered = {node.text for node in svg.findall(".//s:rect/s:title", ns)}
        expected = {
            f"{day['date']}: {day['contributionCount']} contribuciones"
            for week in self.profile["contributionsCollection"]["contributionCalendar"]["weeks"]
            for day in week["contributionDays"]
        }
        self.assertEqual(rendered, expected)

    def test_empty_language_data_and_special_characters_are_valid_svg(self):
        self.profile["repositories"] = []
        output = profile_cards.render_languages(self.profile)
        ET.fromstring(output)
        self.assertIn("Todavía no hay repositorios", output)
        self.profile["repositories"] = [{"primaryLanguage": {"name": "A&B <demo>", "color": "#A78BFA"}}]
        output = profile_cards.render_languages(self.profile)
        ET.fromstring(output)
        self.assertIn("A&amp;B &lt;demo&gt;", output)

    def test_repository_pagination_keeps_all_pages(self):
        repositories = self.profile["repositories"][:2]
        responses = []
        for index, repo in enumerate(repositories):
            user = copy.deepcopy(self.profile)
            user["repositories"] = {
                "totalCount": 2, "nodes": [repo],
                "pageInfo": {"hasNextPage": index == 0, "endCursor": f"page-{index}"},
            }
            responses.append(subprocess.CompletedProcess([], 0, json.dumps({"data": {"user": user}}), ""))
        with patch.object(profile_cards.subprocess, "run", side_effect=responses) as request:
            result = profile_cards.fetch_profile("Dante1128")
        self.assertEqual(result["repositories"], repositories)
        second_input = json.loads(request.call_args_list[1].kwargs["input"])
        self.assertEqual(second_input["variables"]["cursor"], "page-0")

    def test_all_cards_parse_as_svg(self):
        for renderer in (profile_cards.render_stats, profile_cards.render_calendar, profile_cards.render_languages):
            self.assertEqual(ET.fromstring(renderer(self.profile)).tag, "{http://www.w3.org/2000/svg}svg")


if __name__ == "__main__":
    unittest.main()
