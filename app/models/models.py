"""
Modelos de Dados do Sistema GED
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):
    """
    Modelo de Usuário do sistema

    Perfis:
    - comum: Cria documentos e executa tarefas
    - gerente: Gerencia documentos e designa tarefas
    - responsavel_interno: Gerencia fluxo de documentos específicos
    - administrador: Gerencia usuários e configurações
    """
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(30), nullable=False, default='comum')
    ativo = db.Column(db.Boolean, default=True)
    setor = db.Column(db.String(100))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)

    # Relacionamentos
    documentos_criados = db.relationship('Documento', backref='criador', lazy='dynamic',
                                         foreign_keys='Documento.criador_id')
    tarefas_criadas = db.relationship('Tarefa', backref='criador', lazy='dynamic',
                                      foreign_keys='Tarefa.criador_id')
    tarefas_atribuidas = db.relationship('Tarefa', backref='responsavel', lazy='dynamic',
                                         foreign_keys='Tarefa.responsavel_id')

    def set_password(self, senha):
        """Define a senha do usuário (hash)"""
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)

    def is_gerente_ou_superior(self):
        """Verifica se o usuário é gerente ou superior"""
        return self.perfil in ['gerente', 'responsavel_interno', 'administrador']

    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.perfil == 'administrador'

    def pode_usar_ia(self):
        """Verifica se o usuário pode acionar funções de IA"""
        return self.perfil in ['gerente', 'administrador']

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Documento(db.Model):
    """
    Modelo de Documento do sistema GED

    Status possíveis:
    - Novo
    - Em Análise
    - Aprovado
    - Aprovado e Publicado
    - Cancelado
    - Obsoleto
    """
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)

    # Informações básicas
    titulo = db.Column(db.String(200), nullable=False)
    tipo_documento = db.Column(db.String(50), nullable=False)  # POP, Manual, Protocolo
    descricao = db.Column(db.Text)
    setor = db.Column(db.String(100))

    # Arquivos
    arquivo_original = db.Column(db.String(255))  # .doc, .odt
    arquivo_publicado_pdf = db.Column(db.String(255))  # PDF final

    # Códigos
    codigo_provisorio = db.Column(db.String(50), unique=True, index=True)
    codigo_definitivo = db.Column(db.String(50), unique=True, index=True)

    # Datas e vencimento
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_publicacao = db.Column(db.DateTime)
    validade_anos = db.Column(db.Integer, default=5)
    data_vencimento = db.Column(db.DateTime)

    # Status e controle
    status = db.Column(db.String(50), default='Novo', nullable=False, index=True)
    versao = db.Column(db.Integer, default=1)

    # IA - texto e metadados extraídos
    texto_extraido = db.Column(db.Text)
    metadados_json = db.Column(db.Text)  # JSON string com resultados da IA

    # Relacionamentos
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tarefas = db.relationship('Tarefa', backref='documento', lazy='dynamic',
                             cascade='all, delete-orphan')
    logs_ia = db.relationship('LogAI', backref='documento', lazy='dynamic',
                             cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Documento, self).__init__(*args, **kwargs)
        if not self.codigo_provisorio:
            self.gerar_codigo_provisorio()

    def gerar_codigo_provisorio(self):
        """Gera código provisório único: TIPO-PROV-TIMESTAMP"""
        prefixo = self.tipo_documento[:3].upper() if self.tipo_documento else 'DOC'
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self.codigo_provisorio = f"{prefixo}-PROV-{timestamp}"

    def gerar_codigo_definitivo(self):
        """Gera código definitivo único: TIPO-DEF-YYYYMMDD-SEQ"""
        prefixo = self.tipo_documento[:3].upper() if self.tipo_documento else 'DOC'
        data = datetime.utcnow().strftime('%Y%m%d')

        # Busca último código do dia para gerar sequencial
        ultimo = Documento.query.filter(
            Documento.codigo_definitivo.like(f"{prefixo}-DEF-{data}-%")
        ).order_by(Documento.codigo_definitivo.desc()).first()

        if ultimo:
            try:
                seq = int(ultimo.codigo_definitivo.split('-')[-1]) + 1
            except:
                seq = 1
        else:
            seq = 1

        self.codigo_definitivo = f"{prefixo}-DEF-{data}-{seq:04d}"

    def calcular_data_vencimento(self):
        """Calcula data de vencimento com base na validade em anos"""
        if self.data_publicacao and self.validade_anos:
            self.data_vencimento = self.data_publicacao + timedelta(days=self.validade_anos * 365)

    def esta_vencido(self):
        """Verifica se o documento está vencido"""
        if self.data_vencimento:
            return datetime.utcnow() > self.data_vencimento
        return False

    def dias_ate_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        if self.data_vencimento:
            delta = self.data_vencimento - datetime.utcnow()
            return delta.days
        return None

    def get_metadados(self):
        """Retorna metadados como dicionário"""
        if self.metadados_json:
            try:
                return json.loads(self.metadados_json)
            except:
                return {}
        return {}

    def set_metadados(self, dados):
        """Define metadados a partir de dicionário"""
        self.metadados_json = json.dumps(dados, ensure_ascii=False)

    def pode_editar(self, usuario):
        """Verifica se o usuário pode editar o documento"""
        if usuario.is_admin():
            return True
        if usuario.id == self.criador_id:
            return self.status in ['Novo', 'Em Análise']
        return usuario.is_gerente_ou_superior()

    def pode_publicar(self):
        """Verifica se o documento pode ser publicado"""
        return self.status == 'Aprovado'

    @property
    def codigo(self):
        """Retorna o código do documento (definitivo se existir, senão provisório)"""
        return self.codigo_definitivo or self.codigo_provisorio

    def get_caminho_arquivo(self):
        """Retorna o caminho completo do arquivo original"""
        if not self.arquivo_original:
            return None
        from flask import current_app
        import os
        return os.path.join(current_app.config['UPLOAD_FOLDER'], self.arquivo_original)

    def get_caminho_publicado(self):
        """Retorna o caminho completo do arquivo publicado em PDF"""
        if not self.arquivo_publicado_pdf:
            return None
        from flask import current_app
        import os
        return os.path.join(current_app.config['PUBLISHED_FOLDER'], self.arquivo_publicado_pdf)

    def __repr__(self):
        return f'<Documento {self.codigo}>'


class Tarefa(db.Model):
    """
    Modelo de Tarefa do sistema GED

    Tipos de tarefas:
    - Analisar
    - Validar Conteúdo
    - Validar Padronização
    - Aprovar
    - Publicar
    - Realizar Correção
    """
    __tablename__ = 'tarefas'

    id = db.Column(db.Integer, primary_key=True)

    # Relacionamentos
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False, index=True)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)

    # Informações da tarefa
    tipo_tarefa = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    prioridade = db.Column(db.String(20), default='normal')  # baixa, normal, alta, urgente

    # Controle de datas
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    prazo = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)

    # Resultado
    concluida = db.Column(db.Boolean, default=False, index=True)
    parecer = db.Column(db.Text)
    aprovado = db.Column(db.Boolean)  # True=aprovado, False=reprovado, None=sem decisão
    arquivo_anexo = db.Column(db.String(255))  # Para tarefa de publicação (PDF final)

    def esta_atrasada(self):
        """Verifica se a tarefa está atrasada"""
        if not self.concluida and self.prazo:
            return datetime.utcnow() > self.prazo
        return False

    def dias_ate_prazo(self):
        """Retorna quantos dias faltam para o prazo"""
        if self.prazo and not self.concluida:
            delta = self.prazo - datetime.utcnow()
            return delta.days
        return None

    def concluir(self, parecer, aprovado=None, arquivo=None):
        """Conclui a tarefa"""
        self.concluida = True
        self.data_conclusao = datetime.utcnow()
        self.parecer = parecer
        self.aprovado = aprovado
        if arquivo:
            self.arquivo_anexo = arquivo

    def pode_concluir(self, usuario):
        """Verifica se o usuário pode concluir a tarefa"""
        return usuario.id == self.responsavel_id or usuario.is_admin()

    def __repr__(self):
        return f'<Tarefa {self.tipo_tarefa} - Doc {self.documento_id}>'


class LogAI(db.Model):
    """
    Modelo para registro de chamadas à API de IA
    Para auditoria e rastreabilidade
    """
    __tablename__ = 'logs_ia'

    id = db.Column(db.Integer, primary_key=True)

    # Relacionamentos
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Informações da chamada
    funcao_ia = db.Column(db.String(50), nullable=False)  # extract, classify, summarize, etc
    data_chamada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Dados da requisição e resposta
    parametros_json = db.Column(db.Text)  # JSON dos parâmetros enviados
    resposta_json = db.Column(db.Text)  # JSON da resposta recebida

    # Status
    sucesso = db.Column(db.Boolean, default=True)
    mensagem_erro = db.Column(db.Text)
    tempo_resposta_ms = db.Column(db.Integer)  # tempo em milissegundos

    # Relacionamentos
    usuario = db.relationship('Usuario', backref='logs_ia')

    def __repr__(self):
        return f'<LogAI {self.funcao_ia} - Doc {self.documento_id}>'
