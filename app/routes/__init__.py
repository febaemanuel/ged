"""
Rotas do Sistema GED
"""
from .routes_documento import bp as documento_bp, bp_api as documentos_api_bp
from .routes_tarefa import bp as tarefa_bp
from .routes_ia import bp as ia_bp
from .routes_dashboard import bp as dashboard_bp
from .routes_auth import bp as auth_bp
from .routes_view import view_bp
from .routes_busca import bp as busca_bp
from .routes_template import bp as template_bp
from .routes_comentario import bp as comentario_bp
from .routes_dashboard_executivo import bp as dashboard_executivo_bp

__all__ = [
    'documento_bp',
    'documentos_api_bp',
    'tarefa_bp',
    'ia_bp',
    'dashboard_bp',
    'auth_bp',
    'view_bp',
    'busca_bp',
    'template_bp',
    'comentario_bp',
    'dashboard_executivo_bp'
]
