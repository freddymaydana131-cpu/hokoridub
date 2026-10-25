# Constitución de Hokori Dub

Principios innegociables que gobiernan el diseño, la implementación y la
evolución del catálogo de personajes y voces. Toda propuesta de cambio debe
respetarlos; si un requisito los contradice, se modifica la especificación antes
que la constitución.

**Versión:** 1.0.0 · **Ratificada:** 2026-10-25 · **Última enmienda:** 2026-10-25

## Principio 1 — Stack simple y sin dependencias de ejecución

El producto se ejecuta con Python 3.11 o superior y **solo la biblioteca
estándar**. No se admiten frameworks web, ORM, bases de datos, servicios en la
nube ni dependencias de ejecución de terceros. `pytest` es la única dependencia
de desarrollo.

**Criterio verificable:** `python -m pip install -e .` no instala paquetes de
ejecución; `pyproject.toml` declara `dependencies = []`; una prueba automática
rechaza cualquier import de terceros en el paquete.

**Por qué:** el MVP lo usa una sola persona en su equipo. Cada dependencia añade
instalación, actualizaciones y superficie de fallo sin aportar valor al problema.

## Principio 2 — La especificación manda

`README.md` y `specs/001-catalogo-voces-mvp/spec.md` son la fuente de verdad
funcional. El código no puede introducir comportamientos, campos ni comandos que
no estén trazados a un requisito (RF), regla de negocio (RN) o requisito no
funcional (RNF). Ante una ambigüedad, se documenta la decisión y se actualiza la
especificación en el mismo cambio.

**Criterio verificable:** cada RF del README aparece en la tabla de trazabilidad
de la spec; cada tarea de `tasks.md` declara qué requisito cubre; una prueba
automática comprueba que los RF-01 a RF-20 tienen al menos una prueba asociada.

**Por qué:** sin esta disciplina, un MVP pequeño acumula «detalles» no
documentados que nadie puede validar ni mantener.

## Principio 3 — La lógica de negocio no conoce la interfaz

Las reglas del catálogo viven en módulos puros (`models`, `matching`, `catalog`,
`text`, `notes`) que no importan `argparse`, `sys`, `cli` ni realizan salida por
pantalla. La CLI (`cli.py`) solo traduce argumentos, llama a la lógica y formatea
resultados. Los mensajes de usuario se centralizan en `messages.py`.

**Criterio verificable:** una prueba de arquitectura inspecciona los imports de
los módulos puros y falla si alguno depende de la CLI o imprime; solo `cli.py`
puede escribir en la salida estándar.

**Por qué:** separar el núcleo permite probarlo sin simular terminal, reutilizarlo
si mañana se añade otra interfaz y cambiar los textos sin tocar reglas.

## Principio 4 — Pruebas obligatorias antes de dar algo por terminado

Ninguna funcionalidad se considera terminada sin pruebas automatizadas que
cubran su criterio de aceptación y sus casos límite. Se exige, como mínimo:
pruebas unitarias del núcleo, pruebas de la CLI de extremo a extremo, pruebas de
persistencia y pruebas de arquitectura. La suite completa debe pasar en verde.

**Criterio verificable:** `python -m pytest` termina con código 0; toda tarea
cerrada en `tasks.md` incluye «Hecho cuando» con una prueba o comando
comprobable; los RF-01 a RF-20 están cubiertos por al menos un test.

**Por qué:** el catálogo guarda información que no se puede reconstruir si se
pierde. La confianza en el archivado, la afinidad y la escritura atómica depende
de pruebas, no de revisión manual.

## Principio 5 — Persistencia aislada y segura

Todo acceso a disco y toda serialización JSON se concentran en `storage.py`.
El resto del sistema trabaja con objetos en memoria. El guardado es atómico
(archivo temporal en el mismo directorio, `fsync` y `os.replace`) y el formato
incluye `schema_version`. Un archivo inválido nunca se sobrescribe de forma
silenciosa.

**Criterio verificable:** una prueba de arquitectura comprueba que solo
`storage.py` importa `json`/`os` para archivos y que ningún otro módulo abre
rutas; las pruebas de almacenamiento simulan fallos y verifican que no queda JSON
parcial ni archivo temporal.

**Por qué:** un solo archivo JSON es fácil de inspeccionar, versionar y respaldar;
aislarlo evita que la lógica dependa del formato y permite migrar el esquema sin
reescribir las reglas.

## Principio 6 — Interfaz en español, código en inglés

La interfaz, los mensajes, la documentación y los ejemplos están en español. El
código —nombres de módulos, clases, funciones, variables y campos persistidos—
está en inglés. Los textos visibles se definen una sola vez en `messages.py` y se
componen con `msg()`.

**Criterio verificable:** una prueba comprueba que toda clave usada por `msg()`
existe en `MESSAGES`; la CLI no contiene literales de error duplicados; el README
y la spec están en español.

**Por qué:** el equipo y la academia trabajan en español, pero el código sigue
convenciones internacionales que facilitan herramientas, revisiones y futuras
colaboraciones.

## Aplicación y enmiendas

- Todo cambio se revisa contra estos seis principios antes de integrarse.
- Una enmienda requiere: motivación escrita, impacto en la spec y las tareas,
  y actualización de las pruebas de arquitectura que la verifican.
- La versión de la constitución se incrementa con cada enmienda y se registra en
  esta cabecera.
- Si un principio entra en conflicto con una petición puntual, prevalece el
  principio hasta que la enmienda se apruebe explícitamente.
