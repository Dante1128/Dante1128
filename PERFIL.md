# Completar el perfil de GitHub

La foto y la biografía se configuran en GitHub, aparte del README. Estos recursos están preparados para mantener el estilo violeta y cian del perfil.

## Avatar

![Avatar de Dante Yupanqui](./assets/avatar-dante.png)

Sube [avatar-dante.png](./assets/avatar-dante.png) como foto de perfil. Es un monograma con tus iniciales, preparado en formato PNG de 1024 × 1024 y con margen para el recorte circular. El archivo [avatar-dante.svg](./assets/avatar-dante.svg) es la versión vectorial editable.

En [la configuración del perfil](https://github.com/settings/profile), usa **Profile picture → Edit → Upload a photo**, ajusta el recorte y guarda con **Set new profile picture**.

## Datos listos para copiar

| Campo | Contenido |
| :--- | :--- |
| Name | Dante Yupanqui |
| Location | La Paz, Bolivia |
| Social accounts | https://www.linkedin.com/in/dante-yupanqui/ |

**Bio** (128/160 caracteres):

```text
Full Stack Developer | Backend, IA y automatización. Laravel · Vue · Python. Construyo soluciones que conectan software y datos.
```

Abre [Edit profile](https://github.com/settings/profile), copia los campos y pulsa **Update profile**.

Estado opcional, desde **Set status**:

```text
🚀 Construyendo con código e IA
```

## Calendario y logros

El calendario de contribuciones, la actividad y los logros de tus capturas los genera GitHub a partir de tu actividad. El README no controla sus colores, disposición ni cifras.

Puedes destacar proyectos públicos en la sección **Pinned** del perfil. Si quieres mostrar actividad privada anonimizada en el calendario, GitHub ofrece una opción de visibilidad; úsala solo si te interesa compartir esos recuentos.

## Estadísticas personalizadas del README

El README incluye tres tarjetas con datos reales: resumen del perfil, calendario de contribuciones visibles y distribución de repositorios públicos propios por lenguaje principal. Las cifras de repositorios y estrellas excluyen forks. La distribución de lenguajes cuenta repositorios, no líneas de código ni nivel de dominio.

Los archivos `assets/github-*.svg` ya tienen una primera versión generada. El workflow [.github/workflows/profile-stats.yml](./.github/workflows/profile-stats.yml) los actualizará diariamente a las **06:23 de Bolivia** (10:23 UTC), una vez publicado en la rama `main` y habilitado GitHub Actions. La hora es aproximada porque GitHub puede retrasar las ejecuciones programadas.

También puedes ejecutar **Actions → Actualizar estadísticas del perfil → Run workflow**. Usa el token automático del repositorio, sin crear un token personal. Si la rama está protegida contra escrituras del bot, tendrás que permitir el mecanismo de actualización que decidas usar.

Para regenerar localmente con una sesión de GitHub CLI conectada:

```powershell
python .github/scripts/update_profile.py
```

Para renderizar los últimos datos guardados sin conexión:

```powershell
python .github/scripts/update_profile.py --snapshot assets/github-data.json
```

Si una consulta falla, el generador no reemplaza las tarjetas por cifras vacías.

La foto, la biografía y las preferencias de la cuenta siguen pendientes de aplicar: la sesión de GitHub CLI no dispone del permiso `user` para editar el perfil y el control de Chrome no fue autorizado. El README, las tarjetas, el avatar y los datos de esta guía sí están preparados localmente.

## Documentación

- [Personalizar el perfil](https://docs.github.com/en/account-and-profile/tutorials/personalize-your-profile)
- [Contribuciones del perfil](https://docs.github.com/en/account-and-profile/concepts/contributions-on-your-profile)
