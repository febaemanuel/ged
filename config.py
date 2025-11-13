"""
Configurações do Sistema GED
"""
import os
from datetime import timedelta

# Força encoding UTF-8 no Windows
if os.name == 'nt':  # Windows
    import sys
    import codecs
    # Verifica se tem o atributo buffer antes de tentar modificar
    if hasattr(sys.stdout, 'buffer') and not hasattr(sys.stdout, 'write_through'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer') and not hasattr(sys.stderr, 'write_through'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class Config:
    """Configuração base da aplicação"""

    # Configurações gerais
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Configurações do banco de dados PostgreSQL
    _db_uri = os.environ.get('DATABASE_URL') or \
        'postgresql://ged_user:ged_password@localhost:5432/ged_db'

    # Garante que ?client_encoding=utf8 está na URI
    if '?' in _db_uri:
        if 'client_encoding' not in _db_uri:
            _db_uri += '&client_encoding=utf8'
    else:
        _db_uri += '?client_encoding=utf8'

    SQLALCHEMY_DATABASE_URI = _db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # True para debug SQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'client_encoding': 'utf8',
            'options': '-c client_encoding=utf8'
        },
        'pool_pre_ping': True,
        'echo': False
    }

    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'uploads', 'documentos')
    UPLOAD_FOLDER_DOCUMENTOS = os.path.join(BASE_DIR, 'app', 'uploads', 'documentos')  # Alias
    PUBLISHED_FOLDER = os.path.join(BASE_DIR, 'app', 'uploads', 'publicados')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'doc', 'docx', 'odt', 'pdf'}
    ALLOWED_EXTENSIONS_DOCUMENTO = {'doc', 'docx', 'odt', 'pdf'}  # Alias

    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Configurações da API de IA (DeepSeek)
    AI_API_BASE_URL = os.environ.get('AI_API_BASE_URL') or 'https://api.deepseek.com'
    AI_API_KEY = os.environ.get('AI_API_KEY') or ''
    AI_API_MODEL = os.environ.get('AI_API_MODEL') or 'deepseek-chat'
    AI_API_TIMEOUT = int(os.environ.get('AI_API_TIMEOUT', 30))  # segundos

    # Configurações de documentos
    VALIDADE_PADRAO_ANOS = 5
    DIAS_ALERTA_VENCIMENTO = 30

    # Perfis de usuário
    PERFIL_COMUM = 'comum'
    PERFIL_GERENTE = 'gerente'
    PERFIL_RESPONSAVEL = 'responsavel_interno'
    PERFIL_ADMIN = 'administrador'

    PERFIS_PERMITIDOS = [PERFIL_COMUM, PERFIL_GERENTE, PERFIL_RESPONSAVEL, PERFIL_ADMIN]

    # Status de documentos
    STATUS_NOVO = 'Novo'
    STATUS_EM_ANALISE = 'Em Análise'
    STATUS_APROVADO = 'Aprovado'
    STATUS_PUBLICADO = 'Aprovado e Publicado'
    STATUS_CANCELADO = 'Cancelado'
    STATUS_OBSOLETO = 'Obsoleto'

    # Tipos de documentos
    TIPO_POP = 'POP'
    TIPO_MANUAL = 'Manual'
    TIPO_PROTOCOLO = 'Protocolo'

    TIPOS_DOCUMENTO = [TIPO_POP, TIPO_MANUAL, TIPO_PROTOCOLO]

    # Tipos de tarefas
    TAREFA_ANALISAR = 'Analisar'
    TAREFA_VALIDAR_CONTEUDO = 'Validar Conteúdo'
    TAREFA_VALIDAR_PADRONIZACAO = 'Validar Padronização'
    TAREFA_APROVAR = 'Aprovar'
    TAREFA_PUBLICAR = 'Publicar'
    TAREFA_CORRIGIR = 'Realizar Correção'

    TIPOS_TAREFA = [
        TAREFA_ANALISAR,
        TAREFA_VALIDAR_CONTEUDO,
        TAREFA_VALIDAR_PADRONIZACAO,
        TAREFA_APROVAR,
        TAREFA_PUBLICAR,
        TAREFA_CORRIGIR
    ]


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # HTTPS apenas


class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://ged_user:ged_password@localhost:5432/ged_test_db'


# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
