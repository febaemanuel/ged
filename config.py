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
    # IMPORTANTE: SECRET_KEY deve SEMPRE ser definida via variável de ambiente
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY não definida! "
            "Por favor, defina a variável de ambiente SECRET_KEY com uma chave segura. "
            "Você pode gerar uma com: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
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
    ASSINATURAS_FOLDER = os.path.join(BASE_DIR, 'uploads', 'assinaturas')  # PDF de assinaturas
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

    # Configurações de E-mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@ged.com'
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False

    # Configurações de documentos
    VALIDADE_PADRAO_ANOS = 5
    DIAS_ALERTA_VENCIMENTO = 30

    # Perfis de usuário
    PERFIL_COMUM = 'comum'
    PERFIL_GERENTE = 'gerente'
    PERFIL_RESPONSAVEL = 'responsavel_interno'
    PERFIL_ADMIN = 'administrador'
    PERFIL_QUALIDADE_TRIADOR = 'qualidade_triador'         # Novo - Workflow UGQ
    PERFIL_QUALIDADE_VALIDADOR = 'qualidade_validador'     # Novo - Workflow UGQ

    PERFIS_PERMITIDOS = [
        PERFIL_COMUM,
        PERFIL_GERENTE,
        PERFIL_RESPONSAVEL,
        PERFIL_ADMIN,
        PERFIL_QUALIDADE_TRIADOR,
        PERFIL_QUALIDADE_VALIDADOR
    ]

    # Status de documentos
    STATUS_NOVO = 'Novo'
    STATUS_EM_ANALISE = 'Em Análise'
    STATUS_EM_TRIAGEM = 'Em Triagem'                        # Novo - Workflow UGQ
    STATUS_EM_VALIDACAO = 'Em Validação'                    # Novo - Workflow UGQ
    STATUS_EM_CORRECAO = 'Em Correção'                      # Novo - Workflow UGQ
    STATUS_VALIDADO = 'Validado'                            # Novo - Workflow UGQ (codificado)
    STATUS_EM_APROVACAO = 'Em Aprovação'                    # Novo - Workflow UGQ (bloco assinatura)
    STATUS_EM_AJUSTES = 'Em Ajustes'                        # Novo - Workflow UGQ (reprovado)
    STATUS_APROVADO = 'Aprovado'
    STATUS_PUBLICADO = 'Publicado'                          # Simplificado
    STATUS_CANCELADO = 'Cancelado'
    STATUS_OBSOLETO = 'Obsoleto'
    STATUS_VIGENTE = 'Vigente'                              # Novo - Workflow UGQ

    # Tipos de documentos
    TIPO_POP = 'POP'
    TIPO_MANUAL = 'Manual'
    TIPO_PROTOCOLO = 'Protocolo'
    TIPO_POLITICA = 'Política'
    TIPO_REGIMENTO = 'Regimento'
    TIPO_REGULAMENTO = 'Regulamento'

    TIPOS_DOCUMENTO = [TIPO_POP, TIPO_MANUAL, TIPO_PROTOCOLO, TIPO_POLITICA, TIPO_REGIMENTO, TIPO_REGULAMENTO]

    # Tipos que têm validade de 4 anos (os demais têm 2 anos)
    TIPOS_VALIDADE_4_ANOS = [TIPO_POLITICA, TIPO_REGIMENTO, TIPO_REGULAMENTO]

    # =========================================================================
    # ABRANGÊNCIAS E SETORES - COMPLEXO HOSPITALAR UFC
    # =========================================================================

    # Abrangências do Complexo Hospitalar
    ABRANGENCIA_CHUFC = 'CHUFC'   # Complexo Hospitalar Universitário da UFC
    ABRANGENCIA_HUWC = 'HUWC'     # Hospital Universitário Walter Cantídio
    ABRANGENCIA_MEAC = 'MEAC'     # Maternidade Escola Assis Chateaubriand

    ABRANGENCIAS = [ABRANGENCIA_CHUFC, ABRANGENCIA_HUWC, ABRANGENCIA_MEAC]

    # Setores por abrangência (exemplo - adicione mais conforme necessário)
    SETORES_POR_ABRANGENCIA = {
        ABRANGENCIA_CHUFC: [
            'Administração',
            'Assessoria de Comunicação',
            'Auditoria',
            'Comissões',
            'Contabilidade',
            'Contratos',
            'Diretoria Geral',
            'Farmácia',
            'Financeiro',
            'Gestão de Pessoas',
            'Governança',
            'Informática',
            'Logística',
            'Operações',
            'Ouvidoria',
            'Patrimônio',
            'Planejamento',
            'Qualidade',
            'Recursos Humanos',
            'Secretaria Geral',
            'Segurança',
            'Tecnologia da Informação',
            'Transporte',
            'Unidade de Gestão da Qualidade',
        ],
        ABRANGENCIA_HUWC: [
            'Administração',
            'Ambulatório',
            'Banco de Sangue',
            'Bloco Cirúrgico',
            'Cardiologia',
            'Centro Cirúrgico',
            'Cirurgia Geral',
            'Clínica Médica',
            'CME',
            'Dermatologia',
            'Diretoria',
            'Emergência',
            'Endocrinologia',
            'Enfermagem',
            'Farmácia',
            'Fisioterapia',
            'Gastroenterologia',
            'Geriatria',
            'Hematologia',
            'Hemoterapia',
            'Hotelaria Hospitalar',
            'Imagenologia',
            'Infectologia',
            'Laboratório',
            'Nefrologia',
            'Neurologia',
            'Nutrição',
            'Oftalmologia',
            'Oncologia',
            'Ortopedia',
            'Otorrinolaringologia',
            'Pediatria',
            'Pneumologia',
            'Pronto Socorro',
            'Psicologia',
            'Qualidade',
            'Radiologia',
            'Reumatologia',
            'Serviço Social',
            'Transplante',
            'Urologia',
            'UTI',
        ],
        ABRANGENCIA_MEAC: [
            'Administração',
            'Aleitamento Materno',
            'Ambulatório',
            'Banco de Leite',
            'Bloco Cirúrgico',
            'Centro Cirúrgico',
            'Centro Obstétrico',
            'CME',
            'Diretoria',
            'Enfermagem',
            'Farmácia',
            'Fisioterapia',
            'Ginecologia',
            'Hotelaria Hospitalar',
            'Laboratório',
            'Mastologia',
            'Medicina Fetal',
            'Neonatologia',
            'Nutrição',
            'Obstetrícia',
            'Patologia',
            'Planejamento Familiar',
            'Psicologia',
            'Qualidade',
            'Radiologia',
            'Reprodução Humana',
            'Serviço Social',
            'UCI Neonatal',
            'UTI Materna',
            'UTI Neonatal',
        ],
    }

    # Lista completa de todos os setores (para uso geral)
    @classmethod
    def get_todos_setores(cls):
        """Retorna lista de todos os setores com suas abrangências"""
        todos = []
        for abrang, setores in cls.SETORES_POR_ABRANGENCIA.items():
            for setor in setores:
                todos.append({'setor': setor, 'abrangencia': abrang})
        return sorted(todos, key=lambda x: (x['setor'], x['abrangencia']))

    @classmethod
    def get_setores_por_abrangencia(cls, abrangencia):
        """Retorna setores de uma abrangência específica"""
        return cls.SETORES_POR_ABRANGENCIA.get(abrangencia, [])

    # Tipos de tarefas - WORKFLOW UGQ OFICIAL EBSERH
    # ETAPA 0 - Autor
    TAREFA_DOCUMENTO_RECEBIDO = 'Documento Recebido'                        # Novo - Triador UGQ

    # ETAPA 1 - Triador UGQ
    TAREFA_TRIAGEM = 'Triagem de Documento'                                 # Novo - Triador UGQ

    # ETAPA 2 - Validador UGQ
    TAREFA_VALIDAR_CODIFICAR = 'Validar e Codificar Documento'            # Novo - Validador UGQ

    # ETAPA 3 - Validador UGQ + Aprovadores
    TAREFA_GESTAO_BLOCO = 'Gestão do Bloco de Assinatura'                 # Novo - Validador UGQ
    TAREFA_ASSINAR = 'Assinar Documento'                                   # Novo - Aprovadores

    # ETAPA 4 - Validador UGQ
    TAREFA_PUBLICAR_APROVADO = 'Publicar Documento Aprovado'              # Novo - Validador UGQ

    # Tarefas de Correção
    TAREFA_REALIZAR_CORRECAO = 'Realizar Correção'                         # Autor (se devolvido)
    TAREFA_REALIZAR_AJUSTES = 'Realizar Ajustes'                          # Novo - Validador UGQ (se reprovado)

    # Tipos antigos (mantidos para compatibilidade - DEPRECATED)
    TAREFA_ANALISAR = 'Analisar'
    TAREFA_VALIDAR_CONTEUDO = 'Validar Conteúdo'
    TAREFA_VALIDAR_PADRONIZACAO = 'Validar Padronização'
    TAREFA_APROVAR = 'Aprovar'
    TAREFA_PUBLICAR = 'Publicar'
    TAREFA_CORRIGIR = 'Realizar Correção'

    # Todos os tipos de tarefa (novos + antigos)
    TIPOS_TAREFA = [
        # Workflow UGQ (NOVO)
        TAREFA_DOCUMENTO_RECEBIDO,
        TAREFA_TRIAGEM,
        TAREFA_VALIDAR_CODIFICAR,
        TAREFA_GESTAO_BLOCO,
        TAREFA_ASSINAR,
        TAREFA_PUBLICAR_APROVADO,
        TAREFA_REALIZAR_CORRECAO,
        TAREFA_REALIZAR_AJUSTES,
        # Workflow Antigo (DEPRECATED - mantido para compatibilidade)
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

    # Em desenvolvimento, permite chave fraca SE não estiver definida
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-key-CHANGE-IN-PRODUCTION-OR-APP-WILL-FAIL'


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False

    # Segurança de cookies (HTTPS obrigatório)
    SESSION_COOKIE_SECURE = True  # HTTPS apenas
    SESSION_COOKIE_HTTPONLY = True  # Não acessível via JavaScript
    SESSION_COOKIE_SAMESITE = 'Strict'  # Proteção CSRF adicional

    # Força verificação de SECRET_KEY em produção
    if not os.environ.get('SECRET_KEY') or len(os.environ.get('SECRET_KEY', '')) < 32:
        raise ValueError(
            "Em produção, SECRET_KEY deve ter pelo menos 32 caracteres! "
            "Gere uma chave segura com: python -c 'import secrets; print(secrets.token_hex(32))'"
        )


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
