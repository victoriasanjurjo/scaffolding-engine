# Registro de Decisiones de Arquitectura (ADR) - md-scaffold

---

## ADR 001: Adopción de Jinja2 y PyYAML para Templating Dinámico

- **Estado:** Aceptado.
- **Contexto:** Las especificaciones de proyectos en Markdown a menudo necesitan parametrizar nombres de paquetes, versiones, banderas de configuración condicionales (ej. Docker, tests, bases de datos) y opciones de entorno.
- **Decisión:** Integrar `jinja2` para renderizar tanto rutas relativas como contenidos de archivo, y `pyyaml` para extraer variables declaradas en frontmatter o bloques de configuración.
- **Justificación:**
  - Sintaxis declarativa estándar de la industria (`{{ var }}`, `{% if ... %}`).
  - Permite parametrización flexible desde el propio Markdown y desde argumentos de CLI (`--var clave=valor`).
  - Permite condicionales tanto en el árbol de carpetas como dentro del código fuente.

---

## ADR 002: Jerarquía de Precedencia de Variables

- **Estado:** Aceptado.
- **Contexto:** Las variables pueden definirse en múltiples capas (YAML frontmatter inicial, bloques ```yaml en el cuerpo del documento, y parámetros de CLI).
- **Decisión:** Establecer el siguiente orden de precedencia (de menor a mayor):
  1. Frontmatter YAML inicial.
  2. Bloques ```yaml embebidos.
  3. Banderas `--var` pasadas por línea de comandos (tienen máxima prioridad).
- **Justificación:** Permite que una especificación Markdown tenga valores predeterminados sensatos, pero que el usuario pueda anularlos dinámicamente en el momento de la ejecución sin tener que editar el archivo Markdown.

---

## ADR 003: Mitigación de Vulnerabilidades Path Traversal

- **Estado:** Aceptado.
- **Contexto:** Los archivos Markdown pueden provenir de fuentes remotas o externas y contener rutas manipuladas con secuencias `../` para escribir en ubicaciones sensibles del sistema operativo.
- **Decisión:** Implementar validación defensiva en `ScaffoldBuilder.validate_safe_path()` verificando componentes `..` y resolviendo rutas relativas contra el directorio destino con `relative_to()`.
- **Justificación:** Protección contra escrituras arbitrarias fuera del directorio de trabajo.
