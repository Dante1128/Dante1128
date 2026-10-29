# Recursos visuales

- Banner, animaciones, tarjetas, botones y diagrama: SVG creados para este perfil, sin JavaScript ni recursos externos.
- Iconos de tecnologías: [Skill Icons](https://github.com/tandpfun/skill-icons), de tandpfun. Copias locales generadas con [skillicons.dev](https://skillicons.dev), tema oscuro.
- Se conserva la licencia MIT original en [skill-icons-LICENSE.txt](./skill-icons-LICENSE.txt). Las marcas pertenecen a sus respectivos titulares.
- Avatar DY y tarjetas de actividad: diseño propio. Los datos de las tarjetas se obtienen de la API GraphQL de GitHub y se guardan en `github-data.json`; el generador está en `../.github/scripts/update_profile.py`.

Los SVG usan animaciones CSS y respetan `prefers-reduced-motion`. El contenido principal permanece visible si el visor desactiva las animaciones. Para conservar la presentación, publica también `banner.svg` y la carpeta `assets` junto con el README.
