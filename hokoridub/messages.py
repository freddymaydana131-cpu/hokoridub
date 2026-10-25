"""Todos los textos dirigidos al usuario, en español (principio 6)."""

MESSAGES = {
    # Comunes
    "id_required": "El identificador es obligatorio.",
    "id_duplicate": "Ya existe un registro con el identificador «{id}».",
    "confirmation_required": "Se requiere --confirmar para archivar.",
    "order_invalid": "El orden «{value}» no es válido. Opciones: {options}.",
    "affinity_range": "La afinidad mínima debe ser un entero entre {low} y {high}.",
    "limit_range": "El límite debe ser un entero mayor o igual que 1.",
    # Voz
    "voice_name_required": "El nombre de la voz es obligatorio.",
    "voice_name_too_long": "El nombre de la voz no puede superar {limit} caracteres.",
    "stage_name_too_long": "El nombre artístico no puede superar {limit} caracteres.",
    "contact_too_long": "El contacto no puede superar {limit} caracteres.",
    "notes_too_long": "Las notas no pueden superar {limit} caracteres.",
    "languages_required": "Debes indicar al menos un idioma.",
    "languages_too_many": "No puedes indicar más de {limit} idiomas.",
    "language_invalid": "El idioma «{value}» no es válido (de 2 a 20 caracteres).",
    "language_duplicate": "El idioma «{value}» está repetido.",
    "accents_too_many": "No puedes indicar más de {limit} acentos.",
    "accent_invalid": "El acento «{value}» no es válido (de 1 a 40 caracteres).",
    "accent_duplicate": "El acento «{value}» está repetido.",
    "register_invalid": "El registro «{value}» no es válido. Opciones: {options}.",
    "status_invalid": "El estado «{value}» no es válido. Opciones: {options}.",
    "midi_range": "La extensión debe estar entre {low} y {high}.",
    "extension_order": "La nota mínima debe ser menor que la nota máxima.",
    "timbres_too_many": "No puedes indicar más de {limit} timbres.",
    "timbre_invalid": "El timbre «{value}» no es válido. Opciones: {options}.",
    "timbre_duplicate": "El timbre «{value}» está repetido.",
    "age_range": "La edad debe ser un entero entre {low} y {high} años.",
    "age_order": "La edad mínima no puede superar la edad máxima.",
    # Personaje
    "character_name_required": "El nombre del personaje es obligatorio.",
    "character_name_too_long": "El nombre del personaje no puede superar {limit} caracteres.",
    "work_required": "La obra es obligatoria.",
    "work_too_long": "La obra no puede superar {limit} caracteres.",
    "description_required": "La descripción es obligatoria.",
    "description_too_long": "La descripción no puede superar {limit} caracteres.",
    "kind_invalid": "El tipo «{value}» no es válido. Opciones: {options}.",
    "difficulty_range": "La dificultad debe ser un entero entre {low} y {high}.",
    # Prueba
    "recording_kind_invalid": "El tipo de prueba «{value}» no es válido. Opciones: {options}.",
    "link_invalid": "El enlace debe comenzar con http:// o https://.",
    "link_too_long": "El enlace no puede superar {limit} caracteres.",
    "duration_range": "La duración debe ser un entero entre {low} y {high} segundos.",
    "rating_range": "La valoración debe ser un entero entre {low} y {high}.",
    "comment_too_long": "El comentario no puede superar {limit} caracteres.",
    "recorded_at_required": "La fecha de la prueba es obligatoria.",
    # Referencias
    "voice_not_found": "La voz no está disponible.",
    "character_not_found": "El personaje no está disponible.",
    "recording_not_found": "La prueba no está disponible.",
    # Almacenamiento
    "storage_unreadable": "No se pudo leer el archivo de datos: {detail}",
    "storage_invalid_json": "El archivo de datos no contiene JSON válido.",
    "storage_schema": "La versión del archivo de datos no es compatible (se esperaba {expected}).",
    "storage_structure": "La estructura del archivo de datos no es válida.",
    "storage_duplicate": "El archivo de datos tiene identificadores repetidos.",
    "storage_reference": "El archivo de datos tiene referencias inválidas.",
    "storage_write": "No se pudo guardar el archivo de datos: {detail}",
}

# Textos de salida
ERROR_PREFIX = "Error:"
EMPTY_VOICES = "No hay voces registradas por ahora."
NO_MATCH_VOICES = "No se encontraron voces para tu búsqueda."
EMPTY_CHARACTERS = "No hay personajes registrados por ahora."
NO_MATCH_CHARACTERS = "No se encontraron personajes para tu búsqueda."
EMPTY_RECORDINGS = "No hay pruebas registradas por ahora."
NO_MATCH_RECORDINGS = "No se encontraron pruebas con esos filtros."
NO_COMPATIBLES = "No se encontraron voces compatibles con ese criterio."
ARCHIVED_SUFFIX = " (archivado)"
NO_STAGE_NAME = "—"

HEADERS_VOICES = ("ID", "NOMBRE", "REGISTRO", "EDAD", "ESTADO", "PRUEBAS", "ÚLTIMA ACTIVIDAD")
HEADERS_CHARACTERS = ("ID", "NOMBRE", "OBRA", "TIPO", "REGISTRO", "EDAD", "DIFICULTAD")
HEADERS_RECORDINGS = ("ID", "VOZ", "PERSONAJE", "TIPO", "FECHA", "VALORACIÓN")
HEADERS_COMPATIBLES = ("AFINIDAD", "NIVEL", "VOZ", "REGISTRO", "EDAD")
HEADERS_PORTFOLIO = ("ID", "PERSONAJE", "TIPO", "FECHA", "VALORACIÓN")

LABELS = {
    "id": "ID",
    "name": "Nombre",
    "stage_name": "Nombre artístico",
    "contact": "Contacto",
    "register": "Registro",
    "extension": "Extensión",
    "timbres": "Timbres",
    "age": "Edad aparente",
    "languages": "Idiomas",
    "accents": "Acentos",
    "status": "Estado",
    "notes": "Notas",
    "created_at": "Alta",
    "updated_at": "Última edición",
    "last_activity": "Última actividad",
    "work": "Obra",
    "kind": "Tipo de obra",
    "description": "Descripción",
    "difficulty": "Dificultad",
    "character": "Personaje",
    "recording_kind": "Tipo de prueba",
    "recorded_at": "Fecha",
    "rating": "Valoración",
    "portfolio": "Pruebas",
    "compatibles": "Voces compatibles",
    "level": "Nivel",
    "affinity": "Afinidad",
}

LEVELS = {"alta": "alta", "media": "media", "baja": "baja"}


def msg(key: str, **kwargs) -> str:
    """Devuelve el texto español de una clave, con sustitución opcional."""
    template = MESSAGES[key]
    return template.format(**kwargs) if kwargs else template
