# Especificación — Catálogo de personajes y voces (MVP)

**Identificador:** 001-catalogo-voces-mvp
**Estado:** Implementado
**Versión:** 1.0.0
**Fecha:** 2026-10-25
**Origen:** Necesidad de la academia Hokori Dub de sustituir hojas de cálculo y
mensajes sueltos por un catálogo consultable de voces, personajes y pruebas.
**Fuente funcional:** [`README.md`](../../README.md)
**Constitución:** [`docs/constitution.md`](../../docs/constitution.md)

## 1. Contexto

La academia forma actores de voz y participa en castings de animación,
videojuegos, audiolibros y doblaje. La coordinación mantiene tres tipos de
información que hoy están dispersos:

- **Voces:** quién estudia o egresó, qué registro y extensión tiene, qué timbres
  domina, qué idiomas y acentos maneja y en qué estado se encuentra.
- **Personajes:** qué roles están en producción, de qué obra y tipo, qué edad y
  características vocales requieren y cuánta dificultad implican.
- **Pruebas:** qué audios ha grabado cada voz para cada personaje, cuándo, de qué
  tipo, con qué valoración y dónde está el enlace.

Sin un registro común, el director de casting no puede comparar candidaturas con
criterios explícitos ni justificar por qué una voz es adecuada para un rol. El
MVP resuelve ese problema con una herramienta local, sin servidores ni cuentas,
que calcula una afinidad explicable y conserva la evidencia del portafolio.

**Principio rector:** el sistema es un catálogo de apoyo a la decisión. La
afinidad orienta, no sustituye la audición ni el criterio profesional.

## 2. Usuarios

| Usuario | Necesidad | Frecuencia |
| --- | --- | --- |
| **Coordinador de la academia** | Mantener el catálogo actualizado y obtener rankings para proponer candidaturas. | Diaria o semanal |
| **Director de casting** | Consultar voces compatibles y el portafolio que respalda cada candidatura. | Por cada proyecto |
| **Actor de voz / estudiante** | Ser representado correctamente en el catálogo; no opera el sistema. | Indirecta |

El MVP asume **un único operador** (la coordinación) y un archivo de datos local.
No hay concurrencia, autenticación ni auditoría por usuario.

## 3. Historias de usuario

### HU-01 — Registrar una voz

**Como** coordinador, **quiero** dar de alta una voz con su perfil vocal,
idiomas y datos de contacto, **para** incorporarla al catálogo y poder
consultarla y proponerla en castings.

**Criterios de aceptación**

- Dado un nombre y un perfil válidos, cuando confirmo el alta, entonces la voz
  queda guardada con identificador único, estado `activa` y fechas de creación y
  modificación.
- Dado un nombre vacío, un registro desconocido, una extensión fuera de C2–C7 o
  invertida, o más de 3 timbres, cuando intento guardar, entonces el sistema
  rechaza la operación con un mensaje en español y no escribe el archivo.
- Dado un mismo idioma repetido con distinta capitalización o tilde, cuando
  intento guardar, entonces el sistema lo rechaza como duplicado.

### HU-02 — Mantener el perfil de una voz

**Como** coordinador, **quiero** editar los datos y el perfil de una voz activa,
**para** reflejar cambios de registro, extensión, disponibilidad o contacto.

**Criterios de aceptación**

- Dado un identificador existente y cambios válidos, cuando guardo, entonces solo
  se modifican los campos indicados y se actualiza `updated_at`.
- Dado un identificador inexistente o archivado, cuando intento editar, entonces
  el sistema responde «no encontrado» y no modifica nada.
- Dado un cambio de estado a `en_pausa` o `egresada`, cuando guardo, entonces la
  voz sigue visible en el catálogo con ese estado.

### HU-03 — Registrar un personaje

**Como** coordinador, **quiero** registrar un personaje con su obra, tipo,
descripción y requisitos vocales, **para** definir qué perfil debe buscar cuando
abre un casting.

**Criterios de aceptación**

- Dados nombre, obra, tipo, descripción y edad válidos, cuando confirmo, entonces
  el personaje queda guardado como activo con dificultad por defecto 3.
- Dado un tipo fuera de `animacion`, `videojuego`, `audiolibro` o `doblaje`,
  cuando intento guardar, entonces el sistema rechaza la operación.
- Dado un registro requerido, cuando lo indico, entonces queda guardado como
  criterio de compatibilidad; también puedo no exigir ninguno.

### HU-04 — Registrar una prueba

**Como** coordinador, **quiero** registrar una prueba de una voz sobre un
personaje con enlace, duración, valoración y comentario, **para** construir el
portafolio y respaldar futuras decisiones de casting.

**Criterios de aceptación**

- Dadas una voz activa y un personaje activo, cuando registro una prueba con
  datos válidos, entonces queda asociada a ambos con identificador único y fecha.
- Dado un enlace que no empieza por `http://` o `https://`, una duración fuera de
  1–3600 o una valoración fuera de 1–5, cuando intento guardar, entonces el
  sistema rechaza la operación.
- Dada una voz o un personaje archivados, cuando intento registrar la prueba,
  entonces el sistema responde «no encontrado» y no crea el registro.

### HU-05 — Consultar el catálogo y los portafolios

**Como** director de casting, **quiero** buscar y filtrar voces y personajes y
ver el detalle de cada uno, **para** encontrar candidaturas y revisar su
evidencia sin recorrer hojas de cálculo.

**Criterios de aceptación**

- Dado un texto de búsqueda, cuando listo voces o personajes, entonces se
  incluyen las coincidencias sin distinguir mayúsculas, tildes ni ñ.
- Dados filtros de registro, timbre, estado o idioma, cuando listo voces,
  entonces solo aparecen las que cumplen todos los filtros.
- Dado un catálogo sin registros o un filtro sin coincidencias, cuando listo,
  entonces veo un mensaje informativo y no se crea ni modifica el archivo.
- Dado el detalle de una voz, cuando lo consulto, entonces veo su perfil, contacto
  y pruebas ordenadas de la más reciente a la más antigua.

### HU-06 — Encontrar voces compatibles

**Como** director de casting, **quiero** obtener un ranking de voces activas
compatibles con un personaje, con su afinidad y nivel, **para** priorizar a quién
llamar a audición y explicar la recomendación.

**Criterios de aceptación**

- Dado un personaje activo con requisitos, cuando pido compatibles, entonces
  obtengo voces activas ordenadas por afinidad descendente con desempate por
  nombre y luego por identificador.
- Dado un filtro de afinidad mínima o un límite, cuando los indico, entonces el
  resultado respeta ambos; un límite menor que 1 o una afinidad fuera de 0–100 se
  rechazan.
- Dado un personaje archivado o inexistente, cuando pido compatibles, entonces el
  sistema responde «no encontrado».
- Dado que una voz no coincide en registro ni comparte timbres, cuando se calcula
  la afinidad, entonces el resultado refleja solo el solapamiento de edades y
  nunca sale del rango 0–100.

### HU-07 — Archivar sin perder histórico

**Como** coordinador, **quiero** archivar voces y personajes con confirmación
explícita, **para** retirarlos de las consultas sin destruir las pruebas que
respaldan su trayectoria.

**Criterios de aceptación**

- Dado un registro activo, cuando archivo sin `--confirmar`, entonces el sistema
  pide confirmación y no modifica nada.
- Dado un registro activo, cuando archivo con `--confirmar`, entonces deja de
  aparecer en listados, detalles y rankings, se registra `archived_at` y se
  conserva su historial.
- Dado un registro archivado, cuando intento editarlo o registrar pruebas sobre
  él, entonces el sistema responde «no encontrado».
- Dado un catálogo con registros archivados, cuando lo guardo y lo vuelvo a
  cargar, entonces el estado archivado y las pruebas se conservan.

## 4. Requisitos funcionales en formato EARS

Los identificadores coinciden con el README. «El sistema» designa la CLI y su
núcleo.

| ID | Requisito (EARS) |
| --- | --- |
| **RF-01** | Cuando el coordinador proporciona un nombre, un perfil vocal y al menos un idioma, el sistema deberá crear una voz activa con identificador único y fechas de creación y modificación. |
| **RF-02** | Cuando se crea o edita una voz, el sistema deberá validar registro, extensión, timbres, edad, idiomas y acentos según los catálogos y límites de la sección 6. |
| **RF-03** | Cuando el coordinador solicita editar una voz activa con cambios válidos, el sistema deberá aplicar solo esos cambios y actualizar la fecha de modificación. |
| **RF-04** | Cuando el coordinador proporciona nombre, obra, tipo, descripción y requisitos válidos, el sistema deberá crear un personaje activo con identificador único. |
| **RF-05** | Cuando se crea o edita un personaje, el sistema deberá validar su edad, registro opcional, timbres y dificultad según la sección 6. |
| **RF-06** | Cuando el coordinador solicita editar un personaje activo, el sistema deberá aplicar los cambios indicados, incluida la eliminación del registro requerido, y actualizar su fecha de modificación. |
| **RF-07** | Cuando el coordinador registra una prueba sobre una voz y un personaje activos, el sistema deberá guardarla con tipo, fecha, enlace, duración, valoración y comentario, usando el valor actual como fecha si no se indica otra. |
| **RF-08** | Cuando se crea o edita una prueba, el sistema deberá validar enlace, duración, valoración y comentario según la sección 6. |
| **RF-09** | Cuando el coordinador edita una prueba existente, el sistema deberá conservar su identificador y su fecha de creación y actualizar su fecha de modificación. |
| **RF-10** | Cuando el coordinador consulta el detalle de una voz, el sistema deberá mostrar su perfil, contacto y pruebas ordenadas de la más reciente a la más antigua con el personaje asociado. |
| **RF-11** | Cuando el coordinador lista voces o personajes, el sistema deberá mostrar solo los activos en una tabla legible y un mensaje informativo si no hay registros o no hay coincidencias. |
| **RF-12** | Cuando el coordinador busca por texto, el sistema deberá comparar subcadenas normalizadas sin distinguir mayúsculas, tildes ni ñ en nombre, nombre artístico, obra, descripción y notas. |
| **RF-13** | Cuando el coordinador aplica filtros, el sistema deberá filtrar voces por registro, timbre, estado e idioma y personajes por tipo y registro requerido. |
| **RF-14** | Cuando el coordinador indica un orden, el sistema deberá ordenar voces por nombre, edad mínima o última actividad y personajes por nombre, actividad o dificultad. |
| **RF-15** | Cuando el coordinador consulta el detalle de un personaje, el sistema deberá mostrar su descripción, requisitos y cantidad de pruebas registradas. |
| **RF-16** | Cuando se evalúa una pareja voz-personaje, el sistema deberá calcular una afinidad entera de 0 a 100 con la fórmula de RN-05 y clasificarla como alta, media o baja. |
| **RF-17** | Cuando el coordinador solicita voces compatibles con un personaje activo, el sistema deberá devolver las voces activas ordenadas por afinidad descendente, aplicando los filtros opcionales de afinidad mínima y límite. |
| **RF-18** | Cuando el coordinador archiva con confirmación explícita, el sistema deberá ocultar el registro de consultas y rankings, impedir operaciones sobre él y conservar sus pruebas. |
| **RF-19** | Cuando el catálogo cambia, el sistema deberá guardarlo completo en un archivo JSON versionado mediante reemplazo atómico. |
| **RF-20** | Cuando el sistema inicia, deberá cargar el catálogo desde el archivo configurado; si no existe, deberá partir de un catálogo vacío, y si es inválido, deberá informar el error sin sobrescribirlo. |

## 5. Trazabilidad con el README

| README | Historia(s) | Módulo principal | Prueba principal |
| --- | --- | --- | --- |
| RF-01 | HU-01 | `catalog.add_voice` | `test_catalog.py::test_add_voice_*` |
| RF-02 | HU-01, HU-02 | `models.VoiceProfile`, `models.Voice` | `test_models.py` |
| RF-03 | HU-02 | `catalog.edit_voice` | `test_catalog.py::test_edit_voice_*` |
| RF-04 | HU-03 | `catalog.add_character` | `test_catalog.py::test_add_character_*` |
| RF-05 | HU-03 | `models.VoiceRequirements`, `models.Character` | `test_models.py` |
| RF-06 | HU-03 | `catalog.edit_character` | `test_catalog.py::test_edit_character_*` |
| RF-07 | HU-04 | `catalog.add_recording` | `test_catalog.py::test_add_recording_*` |
| RF-08 | HU-04 | `models.Recording` | `test_models.py` |
| RF-09 | HU-04 | `catalog.edit_recording` | `test_catalog.py::test_edit_recording_*` |
| RF-10 | HU-05 | `catalog.portfolio` | `test_catalog.py::test_portfolio_*` |
| RF-11 | HU-05 | `catalog.voice_view`, `catalog.character_view` | `test_cli.py` |
| RF-12 | HU-05 | `text.normalize`, `text.contains` | `test_text.py` |
| RF-13 | HU-05 | `catalog.voice_view`, `catalog.character_view` | `test_catalog.py` |
| RF-14 | HU-05 | `catalog.sort_voices`, `catalog.sort_characters` | `test_catalog.py` |
| RF-15 | HU-05 | `catalog.character_view`, CLI `ver` | `test_cli.py::test_cli_personaje_ver` |
| RF-16 | HU-06 | `matching.affinity` | `test_matching.py` |
| RF-17 | HU-06 | `matching.compatible_voices` | `test_matching.py` |
| RF-18 | HU-07 | `catalog.archive_voice`, `catalog.archive_character` | `test_catalog.py` |
| RF-19 | HU-04, HU-07 | `storage.save_catalog` | `test_storage.py` |
| RF-20 | HU-05, HU-07 | `storage.load_catalog` | `test_storage.py` |

## 6. Datos, catálogos y límites

### Voz y perfil vocal

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | string | Único, generado por el sistema. |
| `name` | string | Obligatorio, 1–120 caracteres tras recortar. |
| `stage_name` | string \| null | Hasta 120 caracteres. |
| `contact` | string \| null | Hasta 120 caracteres. |
| `register` | string | Uno de `soprano`, `mezzosoprano`, `contralto`, `tenor`, `baritono`, `bajo`. |
| `midi_min`, `midi_max` | int | Entre 36 (C2) y 96 (C7), con `midi_min <= midi_max`. |
| `timbres` | string[] | 0–3, únicos, del catálogo `dulce`, `nasal`, `rasposo`, `metalico`, `calido`, `brillante`, `opaco`, `infantil`. |
| `age_min`, `age_max` | int | Entre 5 y 90, con `age_min <= age_max`. |
| `languages` | string[] | 1–5, no vacíos, sin duplicados normalizados. |
| `accents` | string[] | 0–5, no vacíos, sin duplicados normalizados. |
| `status` | string | `activa`, `en_pausa` o `egresada`. |
| `notes` | string \| null | Hasta 500 caracteres. |
| `created_at`, `updated_at` | string | UTC ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`). |
| `archived_at` | string \| null | Se setea al archivar. |

### Personaje y requisitos

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | string | Único, generado por el sistema. |
| `name` | string | Obligatorio, 1–150 caracteres. |
| `work` | string | Obligatorio, 1–150 caracteres. |
| `kind` | string | `animacion`, `videojuego`, `audiolibro` o `doblaje`. |
| `description` | string | Obligatoria, 1–1000 caracteres. |
| `age_min`, `age_max` | int | Entre 5 y 90, con `age_min <= age_max`. |
| `register` | string \| null | Opcional, del catálogo de registros. |
| `timbres` | string[] | 0–3, únicos, del catálogo de timbres. |
| `difficulty` | int | 1–5; por defecto 3. |
| `created_at`, `updated_at`, `archived_at` | string \| null | Igual que en la voz. |

### Prueba

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | string | Único en todo el catálogo. |
| `voice_id` | string | Referencia a una voz existente (activa al crear). |
| `character_id` | string | Referencia a un personaje existente (activo al crear). |
| `kind` | string | `demo`, `audicion` o `practica`. |
| `recorded_at` | string | UTC ISO 8601; por defecto la fecha actual. |
| `link` | string \| null | Debe empezar por `http://` o `https://`; hasta 500 caracteres. |
| `duration_seconds` | int \| null | 1–3600. |
| `rating` | int \| null | 1–5. |
| `comment` | string \| null | Hasta 500 caracteres. |
| `created_at`, `updated_at` | string | UTC ISO 8601. |

### Archivo de datos

```json
{
  "schema_version": 1,
  "voices": [
    {
      "id": "v-0001",
      "name": "Valeria López",
      "stage_name": "Vale",
      "contact": "valeria@example.com",
      "profile": {
        "register": "mezzosoprano",
        "midi_min": 55,
        "midi_max": 79,
        "timbres": ["dulce", "calido"],
        "age_min": 18,
        "age_max": 32,
        "accents": ["neutro", "colombiano"]
      },
      "languages": ["es", "en"],
      "status": "activa",
      "notes": null,
      "created_at": "2026-09-01T09:00:00Z",
      "updated_at": "2026-09-01T09:00:00Z",
      "archived_at": null,
      "recordings": []
    }
  ],
  "characters": []
}
```

## 7. Requisitos no funcionales

| ID | Requisito y verificación |
| --- | --- |
| **RNF-01** | Interfaz y mensajes en español, centralizados en `messages.py`. Verificación: prueba de arquitectura de claves y revisión de literales. |
| **RNF-02** | Python ≥ 3.11, sin dependencias de ejecución. Verificación: `pyproject.toml` y prueba que solo permite stdlib. |
| **RNF-03** | Funcionamiento local y sin red. Verificación: no hay clientes HTTP ni sockets en el paquete. |
| **RNF-04** | Determinismo: IDs y reloj inyectados, orden estable. Verificación: pruebas con reloj fijo y desempates explícitos. |
| **RNF-05** | Escritura atómica sin residuos. Verificación: pruebas de fallo de `os.replace` y de directorio. |
| **RNF-06** | Multiplataforma. Verificación: `pathlib`, UTF-8 explícito y pruebas en Windows/Linux/macOS. |

## 8. Casos límite y comportamiento esperado

| Caso | Comportamiento esperado |
| --- | --- |
| Archivo de datos inexistente | Se trabaja con catálogo vacío; no se crea hasta el primer cambio exitoso. |
| Archivo vacío o JSON mal formado | Error de almacenamiento (código 1), mensaje en español y archivo intacto. |
| `schema_version` distinta de 1 | Error de almacenamiento; no se intenta migrar ni sobrescribir. |
| IDs duplicados en el archivo | Error de almacenamiento; no se carga parcialmente. |
| Prueba que referencia un personaje inexistente | Error de almacenamiento; no se carga. |
| Extensión `C5-C3` o nota fuera de C2–C7 | Error de validación (código 2). |
| Edad de voz o personaje fuera de 5–90 | Error de validación. |
| Timbre repetido o desconocido | Error de validación. |
| Idioma repetido con mayúsculas/tildes distintas | Error de validación por duplicado normalizado. |
| Nombre artístico o contacto vacío | Se guarda como ausente (`null`), no como cadena vacía. |
| Voz sin timbres o personaje sin timbres | Válido; el componente de timbre aporta 30 en la afinidad. |
| Personaje sin registro requerido | Válido; el componente de registro aporta 30. |
| Afinidad con edades disjuntas y sin coincidencias | 0; el ranking puede quedar vacío según el filtro. |
| Empate de afinidad | Desempata nombre normalizado y luego identificador. |
| Listar sin registros | Mensaje informativo, código 0, sin crear archivo. |
| Archivar sin `--confirmar` | Error de confirmación (código 2) y sin cambios. |
| Archivar dos veces | La segunda operación responde «no encontrado». |
| Editar un campo con el mismo valor | Se acepta y actualiza `updated_at`. |
| `--registro ninguno` al editar personaje | Se elimina el requisito de registro. |
| Enlace sin esquema `http`/`https` | Error de validación. |
| Duración o valoración con decimales | Error de argumento o validación; se exigen enteros. |
| Ruta de datos en un directorio inexistente | Error de almacenamiento al guardar, con mensaje claro. |
| Caracteres acentuados o ñ en textos | Se conservan al guardar (UTF-8) y se normalizan solo para buscar. |

## 9. Fuera de alcance

Se detalla en el README, sección 2. En esta iteración no se implementan:
autenticación ni roles, servidor o interfaz gráfica, adjuntos de audio,
reproducción, calendario, pagos, notificaciones, importación/exportación,
búsqueda difusa ni sincronización.

## 10. Criterios de finalización

El MVP se considera terminado cuando:

- [x] Los RF-01 a RF-20 están implementados y trazados a módulos y pruebas.
- [x] Los RNF-01 a RNF-06 se cumplen y están verificados por pruebas.
- [x] La CLI permite el ciclo completo: alta de voz, alta de personaje, registro
      de prueba, consulta, ranking y archivado.
- [x] La persistencia funciona con archivo nuevo, existente, inválido e
      inexistente, sin pérdida de datos.
- [x] `python -m pytest` pasa completo en verde.
- [x] El README, la constitución, esta spec, el plan y las tareas están
      actualizados y son coherentes entre sí.
- [x] Existe un catálogo de ejemplo cargable en `data/catalogo.json`.

## 11. Preguntas abiertas

| ID | Pregunta | Estado |
| --- | --- | --- |
| PA-01 | ¿La ponderación 40/30/30 refleja el criterio real de la academia? | **Decisión asumida:** se implementa RN-05 y se valida con la coordinación tras el MVP. |
| PA-02 | ¿Los seis registros clásicos cubren todas las voces de la academia? | **Decisión asumida:** catálogo cerrado de seis; se ampliará si aparece una necesidad real. |
| PA-03 | ¿Se requiere más de un usuario con permisos? | **Pendiente:** fuera del MVP; hoy hay un único operador. |
| PA-04 | ¿Debe conservarse el historial de versiones de cada prueba? | **Pendiente:** hoy se conserva solo la última versión con `updated_at`. |
| PA-05 | ¿Se adjuntarán archivos de audio en lugar de enlaces? | **Pendiente:** hoy solo enlaces `http`/`https`. |
| PA-06 | ¿La afinidad debe considerar idioma, acento o tesitura frente al rol? | **Pendiente:** hoy considera edad, registro y timbre. |

> Cualquier respuesta que cambie el alcance debe reflejarse primero en el README
> y luego en esta spec, el plan y las tareas, según el Principio 2.
