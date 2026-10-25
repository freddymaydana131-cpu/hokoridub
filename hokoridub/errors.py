"""Errores de negocio con código estable y mensaje en español."""


class AppError(Exception):
    """Error controlado que la interfaz sabe traducir a un mensaje y un código."""

    code = "error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    """Datos inválidos según la spec."""

    code = "validation"


class NotFoundError(AppError):
    """La entidad no existe o está archivada."""

    code = "not_found"


class ConfirmationError(AppError):
    """Falta la confirmación explícita de una operación destructiva."""

    code = "confirmation_required"


class StorageError(AppError):
    """El archivo de datos no se pudo leer o escribir."""

    code = "storage_error"
