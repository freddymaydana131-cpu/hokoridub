# Plan técnico — Catálogo de personajes y voces (MVP)

**Identificador:** 001-catalogo-voces-mvp
**Spec:** [`spec.md`](spec.md)
**Estado:** Implementado
**Versión:** 1.0.0
**Fecha:** 2026-10-25

## 1. Conformidad con la constitución

| Principio | Cómo lo cumple este plan | Verificación |
| --- | --- | --- |
| 1. Stack simple | Python ≥ 3.11, solo stdlib en ejecución; `pytest` como dependencia de desarrollo. | `pyproject.toml` con `dependencies = []`; `test_architecture.py`. |
| 2. La spec manda | Cada módulo, comando y campo cita su RF/RN; la trazabilidad RF→módulo→prueba está en la sección 8. | `test_principio2_*` y revisión de la tabla. |
| 3. Lógica separada de la interfaz | Núcleo puro (`models`, `matching`, `catalog`, `text`, `notes`) sin `argparse`, `sys` ni `print`; `cli.py` solo adapta y presenta. | Prueba de imports y de salida; `test_architecture.py`. |
| 4. Pruebas obligatorias | Suite unitaria, de CLI, de persistencia y de arquitectura; RF-01..RF-20 cubiertos. | `python -m pytest`; `test_principio4_*`. |
| 5. Persistencia aislada | Solo `storage.py` importa `json` y abre archivos; escritura atómica y esquema versionado. | `test_storage.py` y prueba de arquitectura. |
| 6. Idioma | Textos en `messages.py`, documentación en español, identificadores en inglés. | `test_principio6_*` y revisión. |

## 2. Estructura del proyecto

```text
hokoridub/
├── README.md                     # spec funcional y guía de uso
├── pyproject.toml                # metadatos, script y configuración de pytest
├── requirements-dev.txt          # pytest
├── docs/
│   └── constitution.md           # principios innegociables
├── specs/001-catalogo-voces-mvp/
│   ├── spec.md                   # especificación detallada
│   ├── plan.md                   # este documento
│   └── tasks.md                  # desglose de tareas
├── data/
│   └── catalogo.json             # catálogo de ejemplo
├── hokoridub/
│   ├── __init__.py               # versión del paquete
│   ├── __main__.py               # python -m hokoridub
│   ├── errors.py                 # jerarquía de errores de aplicación
│   ├── messages.py               # todos los textos de usuario
│   ├── text.py                   # normalización para búsquedas
│   ├── notes.py                  # conversión de notas y extensiones
│   ├── models.py                 # entidades, catálogos y validaciones
│   ├── matching.py               # afinidad y ranking
│   ├── catalog.py                # reglas del catálogo
│   ├── storage.py                # JSON versionado y escritura atómica
│   └── cli.py                    # argparse, presentación y códigos de salida
└── tests/
    ├── factories.py              # datos de prueba deterministas
    ├── test_text.py
    ├── test_notes.py
    ├── test_models.py
    ├── test_matching.py
    ├── test_catalog.py
    ├── test_storage.py
    ├── test_cli.py
    ├── test_sample_data.py
    └── test_architecture.py
```

### Dependencias entre módulos

```text
cli ──► catalog ──► models
 │        │           ▲
 │        ├──► matching ──┘
 │        ├──► notes
 │        └──► text
 ├──► storage ──► models
 ├──► messages
 └──► errors
```

Regla: las flechas apuntan siempre hacia el núcleo. `models` no depende de nada
del paquete salvo `messages` y `errors`; `cli` es la única hoja que conoce
`argparse` y la salida estándar.

## 3. Modelo de datos

El detalle de tipos y reglas está en `spec.md`, sección 6. Esta tabla resume la
correspondencia con el JSON persistido y su origen.

| Entidad | Campo | Tipo JSON | Regla | Fuente |
| --- | --- | --- | --- | --- |
| Voz | `id` | string | Único, no vacío | RF-01, RN-06 |
| Voz | `name` | string | 1–120, obligatorio | RF-01, RN-01 |
| Voz | `stage_name` | string \| null | ≤ 120 | RF-01 |
| Voz | `contact` | string \| null | ≤ 120 | RF-01 |
| Voz | `profile.register` | string | Catálogo de 6 registros | RF-02 |
| Voz | `profile.midi_min/max` | int | 36–96, ordenados | RF-02 |
| Voz | `profile.timbres` | string[] | ≤ 3, catálogo, sin duplicados | RF-02 |
| Voz | `profile.age_min/max` | int | 5–90, ordenados | RF-02 |
| Voz | `profile.accents` | string[] | ≤ 5, sin duplicados | RF-02 |
| Voz | `languages` | string[] | 1–5, sin duplicados | RF-02 |
| Voz | `status` | string | `activa`, `en_pausa`, `egresada` | RF-02 |
| Voz | `notes` | string \| null | ≤ 500 | RF-01 |
| Voz | `created_at`, `updated_at` | string | UTC ISO 8601 | RF-01, RF-03 |
| Voz | `archived_at` | string \| null | Se setea al archivar | RF-18 |
| Voz | `recordings` | object[] | Pruebas anidadas | RF-07, RF-19 |
| Personaje | `id` | string | Único | RF-04, RN-06 |
| Personaje | `name` | string | 1–150, obligatorio | RF-04, RN-01 |
| Personaje | `work` | string | 1–150, obligatorio | RF-04 |
| Personaje | `kind` | string | 4 tipos | RF-04 |
| Personaje | `description` | string | 1–1000, obligatoria | RF-04 |
| Personaje | `requirements.age_min/max` | int | 5–90, ordenados | RF-05 |
| Personaje | `requirements.register` | string \| null | Opcional, catálogo | RF-05 |
| Personaje | `requirements.timbres` | string[] | ≤ 3, catálogo | RF-05 |
| Personaje | `requirements.difficulty` | int | 1–5, por defecto 3 | RF-05 |
| Personaje | `created_at`, `updated_at` | string | UTC ISO 8601 | RF-04, RF-06 |
| Personaje | `archived_at` | string \| null | Se setea al archivar | RF-18 |
| Prueba | `id` | string | Único en todo el catálogo | RF-07, RN-06 |
| Prueba | `character_id` | string | Personaje existente | RF-07 |
| Prueba | `kind` | string | `demo`, `audicion`, `practica` | RF-07 |
| Prueba | `recorded_at` | string | UTC ISO 8601 | RF-07 |
| Prueba | `link` | string \| null | `http(s)://`, ≤ 500 | RF-08 |
| Prueba | `duration_seconds` | int \| null | 1–3600 | RF-08, RN-04 |
| Prueba | `rating` | int \| null | 1–5 | RF-08, RN-04 |
| Prueba | `comment` | string \| null | ≤ 500 | RF-08 |
| Prueba | `created_at`, `updated_at` | string | UTC ISO 8601 | RF-09 |

**Decisiones de modelado**

- Las pruebas se anidan dentro de la voz propietaria (`voice.recordings`) y
  referencian al personaje por `character_id`. Evita duplicar la relación y hace
  que el portafolio se lea sin índices adicionales.
- Los objetos son `dataclasses(frozen=True)`; las mutaciones se hacen creando
  reemplazos con `dataclasses.replace`. El `Catalog` es la única estructura
  mutable y actúa como agregado raíz.
- Las fechas y los IDs nunca se generan en el núcleo: se inyectan (`now`,
  `new_id`) para que las pruebas sean deterministas (RNF-04). La CLI usa
  `uuid4` y el reloj UTC.

## 4. Algoritmos

### 4.1 Afinidad (RF-16, RN-05)

```text
function affinity(voice, character):
    age_a = [voice.age_min, voice.age_max]
    age_b = [character.age_min, character.age_max]
    intersection = max(0, min(age_a.max, age_b.max) - max(age_a.min, age_b.min) + 1)
    union = (age_a.max - age_a.min + 1) + (age_b.max - age_b.min + 1) - intersection
    age_score = 40 * intersection / union

    register_score = 30 if character.register is null or character.register == voice.register else 0

    if character.timbres is empty:
        timbre_score = 30
    else:
        covered = count(t in voice.timbres for t in character.timbres)
        timbre_score = 30 * covered / len(character.timbres)

    return clamp(floor(age_score + register_score + timbre_score), 0, 100)

function level(score):
    if score >= 80: return "alta"
    if score >= 50: return "media"
    return "baja"
```

Se trunca con `floor` para que el resultado sea un entero comprensible y nunca
supere 100. Los rangos de edad son inclusivos y se comparan año a año, de modo
que dos rangos idénticos aportan 40 exactos.

### 4.2 Ranking de compatibles (RF-17)

```text
function compatible_voices(catalog, character_id, min_affinity=0, limit=null):
    validate 0 <= min_affinity <= 100
    validate limit is null or limit >= 1
    character = require_active_character(catalog, character_id)   # error si no existe/archivado
    rows = []
    for voice in catalog.voices:
        if voice.archived_at is not null: continue
        score = affinity(voice, character)
        if score < min_affinity: continue
        rows.append((voice, score))
    sort rows by (-score, normalize(voice.name), voice.id)
    return rows[:limit] if limit else rows
```

El desempate por nombre normalizado y luego por ID garantiza un orden estable y
reproducible incluso con afinidades iguales.

### 4.3 Archivado lógico (RF-18, RN-02, RN-03)

```text
function archive_voice(catalog, voice_id, confirmed, now):
    voice = find_voice(catalog, voice_id)             # incluye archivadas
    if voice is null: raise NotFound
    if not confirmed: raise ConfirmationRequired
    if voice.archived_at is not null: raise NotFound
    voice.archived_at = now
    voice.updated_at = now
    # las pruebas permanecen intactas dentro de la voz
```

Las consultas (`active_voices`, `require_active_voice`, `voice_view`,
`portfolio` desde la CLI, `compatible_voices`, `recording_rows`) filtran por
`archived_at is null`. El mismo patrón se aplica a personajes. Editar o registrar
pruebas sobre un registro archivado produce `NotFoundError`, de modo que la
respuesta no revela si existió.

### 4.4 Búsqueda normalizada (RF-12)

```text
function normalize(text):
    decomposed = NFD(lowercase(trim(text)))
    without_marks = remove combining marks
    return collapse_whitespace(without_marks)

function contains(haystack, needle):
    return normalize(needle) in normalize(haystack)
```

La ñ se despliega a `n` porque NFD separa la virgulilla; es una decisión
deliberada para que «Núñez» se encuentre escribiendo «nunez». Se aplica a nombre,
nombre artístico, obra, descripción y notas; los filtros de idioma y acento usan
la misma normalización para comparar.

### 4.5 Última actividad y orden (RF-14)

```text
function last_activity(voice):
    dates = [voice.created_at, voice.updated_at]
    for r in voice.recordings:
        dates += [r.recorded_at, r.created_at, r.updated_at]
    return max(dates)
```

`sort_voices(order)`:

- `nombre`: por nombre normalizado ascendente, desempate por ID.
- `edad`: por `age_min` ascendente, desempate por nombre y ID.
- `actividad`: por `last_activity` descendente, desempate por nombre y ID.

`sort_characters(order)`:

- `nombre`: normalizado ascendente.
- `actividad`: por `updated_at` descendente.
- `dificultad`: por dificultad descendente (los roles más exigentes primero).

### 4.6 Persistencia atómica (RF-19, RF-20, RNF-05)

```text
function save_catalog(catalog, path):
    data = catalog_to_dict(catalog)                 # schema_version = 1
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    directory = parent(path) or "."
    fd, temp = mkstemp(prefix=".catalogo-", suffix=".tmp", dir=directory)
    try:
        write(fd, text.encode("utf-8"))
        flush(fd); fsync(fd); close(fd)
        os.replace(temp, path)
    except:
        close_if_open(fd); remove_if_exists(temp)
        raise StorageError

function load_catalog(path):
    if not exists(path): return empty Catalog
    try:
        raw = read_utf8(path); data = json.loads(raw)
    except OSError/JSONDecodeError: raise StorageError
    if data.schema_version != 1: raise StorageError
    validate structure, types, unique IDs, character references
    return Catalog(...)
```

El temporal se crea en el **mismo directorio** que el destino para que
`os.replace` sea atómico en el mismo sistema de archivos. Un fallo de validación
nunca llega a escribir: la CLI carga primero, opera en memoria y guarda al final.

## 5. Decisiones técnicas

| ID | Decisión | Justificación | Alternativa descartada |
| --- | --- | --- | --- |
| **D1** | CLI con `argparse` y subcomandos `voz`, `personaje`, `prueba`, `compatibles`. | Es la interfaz pedida, no requiere dependencias y es fácil de descubrir con `--help`. | Interfaz web o TUI: añade servidor, dependencias y complejidad de despliegue sin aportar al MVP. |
| **D2** | Un único JSON con `schema_version` y pruebas anidadas en la voz. | Fácil de inspeccionar, respaldar y versionar; el volumen esperado es de cientos de registros. | SQLite: más robusto en concurrencia, pero innecesario para un operador y oculta el formato. Archivos separados: complican la atomicidad y las referencias. |
| **D3** | Afinidad 40/30/30 con truncado y niveles 80/50. | Hace explícita y explicable la recomendación; el desglose permite ajustar pesos sin cambiar la interfaz. | Modelo de puntuación aprendido o ponderación por idioma/acento: sin datos históricos que lo justifiquen. |
| **D4** | IDs y reloj inyectados en el núcleo; `uuid4` y UTC solo en la CLI. | Pruebas deterministas y núcleo reutilizable; los IDs no dependen del entorno. | Generar IDs dentro de `add_voice`: acopla la lógica a la aleatoriedad y dificulta las pruebas. |
| **D5** | Archivado lógico con `archived_at` y confirmación obligatoria. | Conserva el histórico de pruebas, que es el valor del portafolio, y evita borrados accidentales. | Borrado físico: destruye evidencia; borrado en cascada: pierde el histórico del personaje. |
| **D6** | Solo `storage.py` conoce JSON y disco; escritura con temporal + `fsync` + `os.replace`. | Aísla el formato, permite migrar el esquema y evita archivos parciales. | Escritura directa sobre el archivo: un fallo a mitad deja el catálogo corrupto. |

## 6. Contrato de la CLI

```text
hokoridub [--datos RUTA] <comando> ...

Global:
  --datos RUTA                 Archivo JSON (prioridad sobre HOKORIDUB_ARCHIVO)

voz agregar --nombre N --registro R --extension C3-C5 --edad 18-35
            [--idiomas es,en] [--timbres dulce,calido] [--acentos neutro]
            [--artistico T] [--contacto T] [--notas T] [--estado activa|en_pausa|egresada]
voz listar  [--buscar T] [--registro R] [--timbre T] [--estado E] [--idioma I]
            [--orden nombre|edad|actividad]
voz ver ID
voz editar ID [mismos campos opcionales que agregar]
voz archivar ID --confirmar

personaje agregar --nombre N --obra O --tipo animacion|videojuego|audiolibro|doblaje
                  --descripcion D --edad 8-14 [--registro R]
                  [--timbres a,b] [--dificultad 1-5]
personaje listar [--buscar T] [--tipo T] [--registro R] [--orden nombre|actividad|dificultad]
personaje ver ID
personaje editar ID [campos opcionales; --registro ninguno limpia]
personaje archivar ID --confirmar

prueba agregar --voz ID --personaje ID --tipo demo|audicion|practica
               [--enlace URL] [--duracion 1-3600] [--valoracion 1-5] [--comentario T]
prueba editar --voz ID --id ID [--tipo T] [--enlace URL] [--duracion N]
              [--valoracion N] [--comentario T]
prueba listar [--voz ID] [--personaje ID] [--tipo T]

compatibles PERSONAJE [--limite N] [--min-afinidad 0-100]
```

**Comportamiento transversal**

- La opción global `--datos` debe ir antes del subcomando.
- Ruta de datos: `--datos` > `HOKORIDUB_ARCHIVO` > `catalogo.json` del directorio
  actual.
- Códigos de salida: `0` éxito, `2` validación/no encontrado/confirmación/
  argumentos, `1` almacenamiento.
- Los errores se imprimen como `Error: <mensaje>` en la salida de error.
- Las tablas se alinean con anchos calculados a partir del contenido; los textos
  completos se conservan en el dato y se muestran en el detalle.
- `voz ver` incluye perfil, contacto, estado y portafolio; `personaje ver`
  incluye descripción, requisitos y cantidad de pruebas.

## 7. Estrategia de pruebas

| Nivel | Archivo | Qué cubre |
| --- | --- | --- |
| Unidad de utilidades | `test_text.py`, `test_notes.py` | Normalización, búsqueda, conversión MIDI/nota, formato de extensión. |
| Unidad de entidades | `test_models.py` | Validaciones de perfil, voz, personaje, requisitos y prueba; límites y duplicados. |
| Unidad de dominio | `test_catalog.py` | Altas, ediciones, archivado, filtros, órdenes, portafolio, IDs duplicados y RN-03. |
| Unidad de compatibilidad | `test_matching.py` | Fórmula, truncado, niveles, orden, filtros de afinidad y límite. |
| Persistencia | `test_storage.py` | Ida y vuelta, archivo inexistente, JSON inválido, esquema, estructura, referencias, atomicidad y limpieza de temporales. |
| Extremo a extremo | `test_cli.py` | Todos los comandos, errores, códigos de salida, prioridad de ruta, tablas y mensajes. |
| Datos de ejemplo | `test_sample_data.py` | `data/catalogo.json` carga sin errores y conserva el contenido esperado. |
| Arquitectura | `test_architecture.py` | Imports permitidos, aislamiento de disco/JSON, `print` solo en CLI, claves de mensajes, stdlib y cobertura de RF-01..RF-20. |

Convenciones:

- `tests/factories.py` fija `NOW = "2026-10-25T10:00:00Z"` y construye perfiles,
  voces, personajes, pruebas y catálogos válidos.
- Los tests no dependen del reloj real ni del orden de ejecución.
- Los tests de CLI usan `tmp_path` y `capsys`; nunca tocan el catálogo del
  usuario.
- La cobertura de requisitos se verifica con una prueba que busca `RF-NN` en los
  archivos de test (Principio 2). La calidad se mide por comportamiento, no por
  un porcentaje de líneas.

## 8. Mapa de cobertura RF → módulo → prueba

| RF | Módulo(s) | Prueba(s) representativa(s) |
| --- | --- | --- |
| RF-01 | `catalog.add_voice` | `test_catalog.py::test_add_voice_creates_active_voice` |
| RF-02 | `models.VoiceProfile`, `models.Voice` | `test_models.py` (extensiones, timbres, idiomas, edades) |
| RF-03 | `catalog.edit_voice` | `test_catalog.py::test_edit_voice_updates_only_given_fields` |
| RF-04 | `catalog.add_character` | `test_catalog.py::test_add_character_creates_active_character` |
| RF-05 | `models.VoiceRequirements`, `models.Character` | `test_models.py` (requisitos y dificultad) |
| RF-06 | `catalog.edit_character` | `test_catalog.py::test_edit_character_*` |
| RF-07 | `catalog.add_recording` | `test_catalog.py::test_add_recording_*` |
| RF-08 | `models.Recording` | `test_models.py` (enlace, duración, valoración) |
| RF-09 | `catalog.edit_recording` | `test_catalog.py::test_edit_recording_preserves_creation` |
| RF-10 | `catalog.portfolio` | `test_catalog.py::test_portfolio_orders_newest_first` |
| RF-11 | `catalog.voice_view`, `catalog.character_view` | `test_cli.py` (listados y mensajes vacíos) |
| RF-12 | `text.normalize`, `text.contains` | `test_text.py` (tildes, ñ, mayúsculas) |
| RF-13 | `catalog.voice_view`, `catalog.character_view` | `test_catalog.py` (filtros combinados) |
| RF-14 | `catalog.sort_voices`, `catalog.sort_characters` | `test_catalog.py` (tres órdenes por entidad) |
| RF-15 | CLI `ver`, `catalog.character_view` | `test_cli.py::test_cli_personaje_ver` |
| RF-16 | `matching.affinity` | `test_matching.py` (fórmula y niveles) |
| RF-17 | `matching.compatible_voices` | `test_matching.py` (orden, mínimo, límite) |
| RF-18 | `catalog.archive_voice`, `catalog.archive_character` | `test_catalog.py` (confirmación, ocultamiento, histórico) |
| RF-19 | `storage.save_catalog` | `test_storage.py` (round-trip y atomicidad) |
| RF-20 | `storage.load_catalog` | `test_storage.py` (inexistente, inválido, referencias) |

## 9. Orden de implementación

1. **Base:** `pyproject.toml`, paquete, `errors`, `messages`, utilidades
   (`text`, `notes`) y sus pruebas.
2. **Modelo:** dataclasses y validaciones (`models`), con pruebas de límites.
3. **Dominio:** `catalog` (altas, ediciones, archivado, vistas y órdenes).
4. **Compatibilidad:** `matching` (afinidad y ranking).
5. **Persistencia:** `storage` (serialización, carga validada, escritura
   atómica).
6. **Interfaz:** `cli` (subcomandos, tablas, errores y códigos de salida).
7. **Cierre:** datos de ejemplo, pruebas de arquitectura, documentación y
   verificación completa.

Este orden coincide con las dependencias reales: cada fase solo usa módulos ya
probados de las anteriores.

## 10. Pendientes y supuestos

- **PA-01 a PA-06** de la spec siguen abiertos; las decisiones asumidas
  (ponderación, registros, idioma) están implementadas y documentadas.
- El MVP no migra esquemas anteriores: `schema_version != 1` es un error
  explícito. La primera migración se diseñará cuando exista una versión 2.
- El archivo de datos no está pensado para edición manual concurrente; se asume
  un único proceso a la vez.
- Los enlaces de audio no se validan más allá del esquema `http`/`https`; no se
  comprueba que respondan.
- La interfaz gráfica, los roles y los adjuntos quedan para iteraciones futuras.
