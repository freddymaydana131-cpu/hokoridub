# Tareas — Catálogo de personajes y voces (MVP)

**Identificador:** 001-catalogo-voces-mvp
**Plan:** [`plan.md`](plan.md)
**Estado:** Completado
**Fecha:** 2026-10-25
**Verificación global:** `python -m pytest` → 137 pruebas en verde.

Convenciones:

- Cada tarea está pensada para 15–30 minutos de trabajo efectivo.
- **Cubre** indica el requisito, regla, RNF o principio que satisface.
- **Hecho cuando** es un criterio observable, no una intención.
- El orden respeta las dependencias: no se empieza una tarea cuyos insumos no
  estén terminados.

## Fase 1 — Base del proyecto

- [x] **T00 — Crear el esqueleto del repositorio y el paquete.**
  Configurar `pyproject.toml` (Python ≥ 3.11, sin dependencias de ejecución,
  script `hokoridub`), `requirements-dev.txt`, `.gitignore`, `hokoridub/__init__.py`
  y `hokoridub/__main__.py`.
  **Cubre:** RNF-02, Principio 1.
  **Hecho cuando:** `python -c "import hokoridub"` funciona y `pyproject.toml`
  declara `dependencies = []`.

- [x] **T01 — Definir errores de aplicación y mensajes centralizados.**
  Crear `errors.py` con `AppError`, `ValidationError`, `NotFoundError`,
  `ConfirmationError` y `StorageError`; crear `messages.py` con `MESSAGES`,
  `msg()` y las constantes de salida.
  **Cubre:** RF-02, RNF-01, Principio 3, Principio 6.
  **Hecho cuando:** cada error tiene un código estable y ninguna otra capa
  necesita escribir literales de error.

- [x] **T02 — Implementar normalización de texto.**
  `normalize()` en minúsculas, sin diacríticos, con espacios colapsados, y
  `contains()` para búsquedas por subcadena.
  **Cubre:** RF-12, RNF-04.
  **Hecho cuando:** `test_text.py` demuestra que «NÚÑEZ», «nunez» y «  Núñez  »
  coinciden.

- [x] **T03 — Implementar conversión de notas y extensiones.**
  `note_to_midi`, `midi_to_note`, `format_range`, límites C2–C7 y validación de
  orden.
  **Cubre:** RF-02.
  **Hecho cuando:** `test_notes.py` cubre notas con sostenidos, extremos y
  extensiones invertidas.

## Fase 2 — Modelo de dominio

- [x] **T04 — Modelar el perfil vocal y la voz.**
  `VoiceProfile` y `Voice` como dataclasses inmutables, con catálogos de
  registros, timbres, estados, edades, longitudes y deduplicación normalizada de
  idiomas, acentos y timbres.
  **Cubre:** RF-01, RF-02, RN-01, RN-06.
  **Hecho cuando:** las pruebas de `test_models.py` rechazan cada límite inválido
  y aceptan los valores extremos permitidos.

- [x] **T05 — Modelar personaje y requisitos vocales.**
  `VoiceRequirements` y `Character` con edades, registro opcional, timbres,
  dificultad 1–5 y textos obligatorios.
  **Cubre:** RF-04, RF-05.
  **Hecho cuando:** un personaje sin registro requerido es válido y uno con
  registro desconocido o dificultad 0 se rechaza.

- [x] **T06 — Modelar la prueba y el catálogo raíz.**
  `Recording` con tipo, fecha, enlace, duración, valoración y comentario;
  `Catalog` mutable con búsquedas por ID.
  **Cubre:** RF-07, RF-08, RN-04.
  **Hecho cuando:** las pruebas cubren enlace inválido, duración 0/3601,
  valoración 0/6 y búsquedas por ID existente e inexistente.

## Fase 3 — Reglas del catálogo

- [x] **T07 — Implementar altas y ediciones de voces.**
  `add_voice` y `edit_voice` con fechas inyectadas, actualización parcial y
  rechazo de IDs duplicados.
  **Cubre:** RF-01, RF-03, RN-06, RNF-04.
  **Hecho cuando:** editar solo el contacto no altera el perfil ni `created_at`,
  y sí actualiza `updated_at`.

- [x] **T08 — Implementar altas y ediciones de personajes.**
  `add_character` y `edit_character`, incluida la limpieza del registro
  requerido.
  **Cubre:** RF-04, RF-06.
  **Hecho cuando:** `--registro ninguno` deja el requisito en `None` sin tocar
  los demás campos.

- [x] **T09 — Implementar pruebas y portafolio.**
  `add_recording`, `edit_recording`, `find_recording`, `portfolio` y
  `recording_rows`, conservando `created_at` al editar y ordenando de más
  reciente a más antiguo.
  **Cubre:** RF-07, RF-09, RF-10.
  **Hecho cuando:** el portafolio muestra solo pruebas de la voz consultada y la
  fecha de creación no cambia al editar.

- [x] **T10 — Implementar archivado lógico y sus restricciones.**
  `archive_voice`, `archive_character` y `require_active_*`; confirmación
  obligatoria, ocultamiento y conservación de pruebas.
  **Cubre:** RF-18, RN-02, RN-03.
  **Hecho cuando:** archivar sin confirmar no modifica nada, archivar con
  confirmar conserva las pruebas y operar sobre el registro archivado devuelve
  «no encontrado».

- [x] **T11 — Implementar vistas con búsqueda y filtros.**
  `voice_view` y `character_view` con estados `ok`, `empty`, `no_matches`;
  filtros por registro, timbre, estado, idioma, tipo y registro requerido.
  **Cubre:** RF-11, RF-12, RF-13.
  **Hecho cuando:** los filtros se combinan con AND y un catálogo sin
  coincidencias devuelve el estado correcto sin crear archivo.

- [x] **T12 — Implementar ordenamientos y última actividad.**
  `last_activity`, `sort_voices` y `sort_characters` con desempates estables.
  **Cubre:** RF-14, RNF-04.
  **Hecho cuando:** los tres órdenes de cada entidad están cubiertos y dos
  registros con la misma clave mantienen un orden reproducible.

## Fase 4 — Compatibilidad

- [x] **T13 — Calcular la afinidad.**
  Fórmula 40/30/30 con rangos inclusivos, truncado, acotado 0–100 y niveles
  alta/media/baja.
  **Cubre:** RF-16, RN-05.
  **Hecho cuando:** perfiles idénticos dan 100, edades disjuntas sin coincidencias
  dan 0 y el resultado siempre es entero.

- [x] **T14 — Construir el ranking de compatibles.**
  `compatible_voices` con personaje activo, voces activas, orden por afinidad,
  desempate por nombre e ID, filtro mínimo y límite validados.
  **Cubre:** RF-17, RN-02.
  **Hecho cuando:** un personaje archivado produce «no encontrado», un límite 0
  se rechaza y el corte del límite respeta el orden.

## Fase 5 — Persistencia

- [x] **T15 — Serializar y guardar el catálogo.**
  `catalog_to_dict` con `schema_version = 1` y `save_catalog` con temporal en el
  mismo directorio, `fsync`, `os.replace` y limpieza ante error.
  **Cubre:** RF-19, RNF-05.
  **Hecho cuando:** guardar dos veces produce el mismo JSON y un fallo simulado no
  deja archivo temporal ni destino corrupto.

- [x] **T16 — Cargar y validar el catálogo.**
  `load_catalog` con archivo inexistente → catálogo vacío; errores claros ante
  JSON inválido, esquema distinto, estructura rota, IDs duplicados o referencias
  a personajes inexistentes.
  **Cubre:** RF-20, Principio 5.
  **Hecho cuando:** un archivo inválido lanza `StorageError` y permanece intacto.

## Fase 6 — Interfaz de línea de comandos

- [x] **T17 — Crear el esqueleto de la CLI.**
  `argparse` en español, opción global `--datos`, resolución por variable de
  entorno y ruta por defecto, manejo de errores y códigos 0/1/2.
  **Cubre:** RF-11, RNF-01, RNF-06.
  **Hecho cuando:** `--datos` gana sobre `HOKORIDUB_ARCHIVO`, y los errores de
  validación salen con código 2 y prefijo `Error:`.

- [x] **T18 — Implementar los comandos de voz.**
  `voz agregar`, `listar`, `ver`, `editar` y `archivar` con sus opciones,
  tablas y detalle con portafolio.
  **Cubre:** RF-01, RF-03, RF-10, RF-11, RF-18.
  **Hecho cuando:** el ciclo completo de alta, listado, detalle, edición y
  archivado funciona sobre un archivo temporal.

- [x] **T19 — Implementar los comandos de personaje.**
  `personaje agregar`, `listar`, `ver`, `editar` y `archivar`, con requisitos,
  tipo, dificultad y limpieza de registro.
  **Cubre:** RF-04, RF-06, RF-15, RF-18.
  **Hecho cuando:** el detalle muestra descripción, requisitos y cantidad de
  pruebas; editar con `--registro ninguno` limpia el requisito.

- [x] **T20 — Implementar los comandos de prueba.**
  `prueba agregar`, `editar` y `listar`, con validación de voz/personaje activos
  y conservación de fechas.
  **Cubre:** RF-07, RF-08, RF-09.
  **Hecho cuando:** registrar una prueba sobre un archivado falla y editar una
  prueba no cambia su `created_at`.

- [x] **T21 — Implementar compatibles y la presentación de tablas.**
  `compatibles` con afinidad, nivel, mínimo y límite; tablas alineadas, mensajes
  de vacío y datos completos conservados.
  **Cubre:** RF-16, RF-17, RNF-01.
  **Hecho cuando:** la salida del ranking es legible, ordenada y los mensajes de
  «sin resultados» no crean el archivo de datos.

- [x] **T22 — Escribir las pruebas de arquitectura.**
  Verificar imports del núcleo, aislamiento de disco/JSON, `print` solo en CLI,
  claves de mensajes, uso exclusivo de stdlib y cobertura de RF-01..RF-20.
  **Cubre:** Principios 1, 3, 4, 5 y 6.
  **Hecho cuando:** `test_architecture.py` pasa y falla si se introduce una
  violación deliberada.

## Fase 7 — Documentación y cierre

- [x] **T23 — Redactar el README funcional.**
  Objetivo, alcance, actores, RF-01..RF-20, RNF, entidades, RN, puesta en marcha,
  índice SDD y decisiones asumidas.
  **Cubre:** Principio 2, Principio 6.
  **Hecho cuando:** el README permite entender el producto y ejecutar el MVP sin
  leer el código.

- [x] **T24 — Redactar la constitución.**
  Seis principios con criterio verificable, motivación y proceso de enmienda.
  **Cubre:** Principio 2, Principio 6.
  **Hecho cuando:** cada principio se puede comprobar con una prueba o un comando
  concreto.

- [x] **T25 — Redactar la especificación detallada.**
  Contexto, usuarios, siete historias de usuario, RF en EARS, trazabilidad,
  modelo de datos, RNF, casos límite, fuera de alcance, criterios de finalización
  y preguntas abiertas.
  **Cubre:** Principio 2.
  **Hecho cuando:** cada RF del README aparece en la tabla de trazabilidad y cada
  caso límite tiene comportamiento esperado.

- [x] **T26 — Redactar plan y tareas, añadir datos de ejemplo y verificar todo.**
  Plan técnico con decisiones, algoritmos y mapa de cobertura; este desglose de
  tareas; `data/catalogo.json` cargable; prueba de los datos de ejemplo; suite
  completa.
  **Cubre:** Principios 1 a 6.
  **Hecho cuando:** `python -m pytest` pasa completo y
  `python -m hokoridub --datos data/catalogo.json compatibles c-0002` devuelve un
  ranking coherente.

## Resumen

| Fase | Tareas | Estado |
| --- | --- | --- |
| 1. Base | T00–T03 | Completada |
| 2. Modelo | T04–T06 | Completada |
| 3. Reglas del catálogo | T07–T12 | Completada |
| 4. Compatibilidad | T13–T14 | Completada |
| 5. Persistencia | T15–T16 | Completada |
| 6. CLI | T17–T21 | Completada |
| 7. Documentación y cierre | T22–T26 | Completada |

**Comando de verificación final:**

```powershell
python -m pytest
python -m hokoridub --datos data/catalogo.json voz listar
python -m hokoridub --datos data/catalogo.json compatibles c-0002 --min-afinidad 50
```
