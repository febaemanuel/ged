"""
Rotas do Sistema GED
"""
from .routes_documento import bp as documento_bp
from .routes_tarefa import bp as tarefa_bp
from .routes_ia import bp as ia_bp
from .routes_dashboard import bp as dashboard_bp
from .routes_auth import bp as auth_bp

__all__ = ['documento_bp', 'tarefa_bp', 'ia_bp', 'dashboard_bp', 'auth_bp']
