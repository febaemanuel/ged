"""
Modelos do Sistema GED
"""
from .models import (
    db,
    Usuario,
    Documento,
    Tarefa,
    LogAI,
    ListaMestra,
    BlocoAssinatura,
    ItemBlocoAssinatura,
    ValidacaoUGQ,
    Notificacao
)

__all__ = [
    'db',
    'Usuario',
    'Documento',
    'Tarefa',
    'LogAI',
    'ListaMestra',
    'BlocoAssinatura',
    'ItemBlocoAssinatura',
    'ValidacaoUGQ',
    'Notificacao'
]
