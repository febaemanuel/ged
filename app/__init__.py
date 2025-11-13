"""
Inicialização do aplicativo Flask GED
"""
from flask import Flask, render_template
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler

from config import config
from app.models import db, Usuario


login_manager = LoginManager()


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
        tarefa_bp,
        ia_bp,
        dashboard_bp,
        view_bp,
        busca_bp
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(documento_bp)
    app.register_blueprint(tarefa_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(busca_bp)

    # Rota inicial
    @app.route('/home')
    def home():
        """Página inicial com documentação básica"""
        return render_template('index.html')

    # Handler de erro 404
    @app.errorhandler(404)
    def not_found(error):
        return {'erro': 'Recurso não encontrado'}, 404

    # Handler de erro 500
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'erro': 'Erro interno do servidor'}, 500

    return app


@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para Flask-Login"""
    return Usuario.query.get(int(user_id))
