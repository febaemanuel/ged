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

    # ✅ Health check endpoint detalhado para Docker
    @app.route('/health')
    def health_check():
        """Health check endpoint detalhado para monitoramento"""
        from datetime import datetime
        import shutil

        health = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }

        # 1. Database
        try:
            db.session.execute(text('SELECT 1')).scalar()
            db.session.commit()
            health['checks']['database'] = 'ok'
        except Exception as e:
            db.session.rollback()
            health['checks']['database'] = f'error: {str(e)}'
            health['status'] = 'unhealthy'
            app.logger.error(f'Database health check failed: {str(e)}')

        # 2. Redis/Celery Broker
        try:
            from celery_app import celery
            celery.broker_connection().ensure_connection(max_retries=1, timeout=2)
            health['checks']['redis'] = 'ok'
        except Exception as e:
            health['checks']['redis'] = f'error: {str(e)}'
            health['status'] = 'degraded'
            app.logger.warning(f'Redis health check failed: {str(e)}')

        # 3. Celery Workers (opcional - não bloqueia)
        try:
            from celery_app import celery
            stats = celery.control.inspect(timeout=1).stats()
            if stats:
                health['checks']['celery_workers'] = f"{len(stats)} active"
            else:
                health['checks']['celery_workers'] = 'no workers'
                health['status'] = 'degraded' if health['status'] == 'healthy' else health['status']
        except Exception as e:
            health['checks']['celery_workers'] = 'unknown'
            app.logger.debug(f'Celery workers check failed: {str(e)}')

        # 4. Espaço em Disco
        try:
            disk = shutil.disk_usage('/app')
            disk_free_pct = (disk.free / disk.total) * 100
            health['checks']['disk_free'] = f"{disk_free_pct:.1f}%"
            if disk_free_pct < 10:
                health['status'] = 'degraded' if health['status'] == 'healthy' else health['status']
                app.logger.warning(f'Low disk space: {disk_free_pct:.1f}%')
        except Exception as e:
            health['checks']['disk_free'] = 'unknown'
            app.logger.debug(f'Disk check failed: {str(e)}')

        # Status code baseado no status
        status_code = 200 if health['status'] == 'healthy' else 503
        return health, status_code

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
