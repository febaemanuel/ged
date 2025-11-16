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
    Notificacao,
    TemplateDocumento,
    Comentario,
    ConfiguracaoWhatsApp,
    ConversacaoWhatsApp,
    LogWhatsApp
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
    'Notificacao',
    'TemplateDocumento',
    'Comentario',
    'ConfiguracaoWhatsApp',
    'ConversacaoWhatsApp',
    'LogWhatsApp'
]
