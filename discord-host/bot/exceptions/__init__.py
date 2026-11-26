class MiyoraError(Exception):
    """Erro base do Miyora."""


class MiyoraConfigurationError(MiyoraError):
    """Configuração ausente ou inválida."""
