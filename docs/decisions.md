# Registro de Decisiones de Arquitectura (ADR) - md-scaffold

---

## ADR 001: Dependencia Exclusiva de la Biblioteca Estándar

- **Estado:** Aceptado.
- **Contexto:** Las herramientas de scaffolding y CLI de propósito general requieren ejecutarse de manera inmediata en cualquier entorno con Python sin demoras de instalación de dependencias pesadas.
- **Decisión:** Implementar la totalidad del motor utilizando únicamente `pathlib`, `re`, `argparse`, `sys` y `typing`.
- **Justificación:** Portabilidad instantánea, cero vulnerabilidades por cadena de suministro y máxima velocidad de arranque.

---

## ADR 002: Separación Estricta entre Parseo Sintáctico y Construcción Física

- **Estado:** Aceptado.
- **Contexto:** El parseo de especificaciones Markdown no debe acoplarse con la lógica de escritura en disco para permitir pruebas unitarias sin efectos secundarios e implementar con facilidad el modo `--dry-run`.
- **Decisión:** `ScaffoldParser` opera exclusivamente sobre cadenas de texto retornando estructuras `TreeEntry` y diccionarios en memoria. `ScaffoldBuilder` consume estas estructuras y aplica las operaciones en disco.
- **Justificación:** Alta testeabilidad, aislamiento de fallos y claridad de responsabilidades.

---

## ADR 003: Mitigación de Vulnerabilidades Path Traversal

- **Estado:** Aceptado.
- **Contexto:** Los archivos Markdown pueden provenir de fuentes remotas o externas y contener rutas manipuladas con secuencias `../` para escribir en ubicaciones sensibles del sistema operativo.
- **Decisión:** Implementar validación defensiva en `ScaffoldBuilder.validate_safe_path()` verificando componentes `..` y resolviendo rutas relativas contra el directorio destino con `relative_to()`.
- **Justificación:** Protección contra escrituras arbitrarias fuera del directorio de trabajo.
