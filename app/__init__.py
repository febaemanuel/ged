"""
Inicialização do aplicativo Flask GED
"""
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text
import os
import logging
from logging.handlers import RotatingFileHandler

from config import config
from app.models import db, Usuario


login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """
    Factory function para criar a aplicação Flask

    Args:
        config_name: Nome da configuração (development, production, testing)

    Returns:
        Aplicação Flask configurada
    """
    app = Flask(__name__)

    # Carrega configuração
    app.config.from_object(config[config_name])

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'view.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    mail.init_app(app)
    csrf.init_app(app)

    # Configura logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/ged.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema GED inicializado')

    # Registra blueprints
    from app.routes import (
        auth_bp,
        documento_bp,
        documentos_api_bp,
        tarefa_bp,
        ia_bp,
        dashboard_bp,
        view_bp,
        busca_bp,
        template_bp,
        comentario_bp,
        dashboard_executivo_bp,
        admin_bp,
        notificacao_bp
    )
    from app.routes.routes_whatsapp import webhook_bp, admin_bp as whatsapp_admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(documento_bp)
    app.register_blueprint(documentos_api_bp)
    app.register_blueprint(tarefa_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(busca_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(comentario_bp)
    app.register_blueprint(dashboard_executivo_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(whatsapp_admin_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notificacao_bp)

    # Rota inicial
    @app.route('/home')
    def home():
        """Página inicial com documentação básica"""
        return render_template('index.html')

    # Health check endpoint para Docker
    @app.route('/health')
    def health_check():
        """Health check endpoint para monitoramento"""
        try:
            # Testa conexão com banco de dados (SQLAlchemy 2.0)
            db.session.execute(text('SELECT 1')).scalar()
            db.session.commit()
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            db.session.rollback()
            # Log do erro (não expõe detalhes em produção)
            app.logger.error(f'Health check failed: {str(e)}')
            return {'status': 'unhealthy', 'database': 'disconnected'}, 503

    # Handler de erro 404
    @app.errorhandler(404)
    def not_found(error):
        return {'erro': 'Recurso não encontrado'}, 404

    # Handler de erro 500
    @app.errorhandler(500)
    def internal_error(error):
        """Handler para erros internos do servidor"""
        db.session.rollback()
        # Log do erro completo para debug
        app.logger.error(f'Internal server error: {error}', exc_info=True)
        return {'erro': 'Erro interno do servidor'}, 500

    return app


@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para Flask-Login"""
    return Usuario.query.get(int(user_id))
