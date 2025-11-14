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
    documentos_como_chefia = db.relationship('Documento', backref='chefia_imediata', lazy='dynamic',
                                            foreign_keys='Documento.chefia_imediata_id')
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
    arquivo_final = db.Column(db.String(255))  # PDF codificado final (UGQ)

    # Códigos
    codigo_unico = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ID único permanente (DOC-YYYYMMDD-HHMMSS-XXX)
    codigo_provisorio = db.Column(db.String(50), unique=True, index=True)
    codigo_definitivo = db.Column(db.String(50), unique=True, index=True)  # Gerado pela UGQ

    # Versionamento
    versao = db.Column(db.String(20))  # v1.0, v2.0
    versao_anterior_id = db.Column(db.Integer, db.ForeignKey('documentos.id'))  # Documento que esta versão substituiu

    # Datas e vencimento
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_publicacao = db.Column(db.DateTime)
    validade_anos = db.Column(db.Integer, default=5)
    data_vencimento = db.Column(db.DateTime)

    # Status e controle
    status = db.Column(db.String(50), default='Novo', nullable=False, index=True)

    # IA - texto e metadados extraídos
    texto_extraido = db.Column(db.Text)
    metadados_json = db.Column(db.Text)  # JSON string com resultados da IA

    # Relacionamentos
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    chefia_imediata_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Chefia para aprovação
    tarefas = db.relationship('Tarefa', backref='documento', lazy='dynamic',
                             cascade='all, delete-orphan')
    logs_ia = db.relationship('LogAI', backref='documento', lazy='dynamic',
                             cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Documento, self).__init__(*args, **kwargs)
        if not self.codigo_unico:
            self.gerar_codigo_unico()
        if not self.codigo_provisorio:
            self.gerar_codigo_provisorio()

    def gerar_codigo_unico(self):
        """
        Gera código único permanente do documento (identidade)
        Formato: DOC-YYYYMMDD-HHMMSS-XXX
        Este código nunca muda e identifica o documento ao longo de todo ciclo de vida
        """
        import random
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        random_suffix = f"{random.randint(0, 999):03d}"
        self.codigo_unico = f"DOC-{timestamp}-{random_suffix}"

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

    # Metadados extras (para bloco de assinatura, etc)
    metadata_json = db.Column(db.Text)  # JSON com dados extras (bloco_id, item_id, modo, etc)

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

    def get_metadata(self):
        """Retorna metadata como dicionário"""
        if self.metadata_json:
            try:
                return json.loads(self.metadata_json)
            except:
                return {}
        return {}

    def set_metadata(self, dados):
        """Define metadata a partir de dicionário"""
        self.metadata_json = json.dumps(dados, ensure_ascii=False)

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


# ============================================================================
# NOVOS MODELOS - WORKFLOW UGQ CENTRALIZADO
# ============================================================================


class ListaMestra(db.Model):
    """
    Lista Mestra de Documentos da UGQ
    Controle de códigos definitivos e versionamento
    """
    __tablename__ = 'lista_mestra'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    versao = db.Column(db.String(20), nullable=False)
    data_publicacao = db.Column(db.DateTime, nullable=False)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'))
    status = db.Column(db.String(50), default='EM_APROVACAO', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    documento = db.relationship('Documento', backref='registro_lista_mestra', uselist=False)

    def __repr__(self):
        return f'<ListaMestra {self.codigo} - {self.status}>'


class BlocoAssinatura(db.Model):
    """
    Bloco de Assinatura para aprovação final
    Gerenciado pelo Validador UGQ
    """
    __tablename__ = 'blocos_assinatura'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False, index=True)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    modo = db.Column(db.String(20), nullable=False)  # 'sequencial' ou 'concomitante'
    status = db.Column(db.String(50), default='Em Andamento', index=True)
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    documento = db.relationship('Documento', backref='blocos_assinatura')
    criador = db.relationship('Usuario', foreign_keys=[criador_id], backref='blocos_criados')
    itens = db.relationship('ItemBlocoAssinatura', backref='bloco', lazy='dynamic',
                            order_by='ItemBlocoAssinatura.ordem', cascade='all, delete-orphan')

    def total_aprovadores(self):
        """Retorna total de aprovadores no bloco"""
        return self.itens.count()

    def aprovadores_aprovaram(self):
        """Retorna quantos aprovadores já aprovaram"""
        return self.itens.filter_by(status='Aprovado').count()

    def aprovadores_reprovaram(self):
        """Retorna quantos aprovadores reprovaram"""
        return self.itens.filter_by(status='Reprovado').count()

    def aprovadores_pendentes(self):
        """Retorna quantos aprovadores estão pendentes"""
        return self.itens.filter_by(status='Pendente').count()

    def todos_aprovaram(self):
        """Verifica se todos os aprovadores aprovaram"""
        return self.aprovadores_aprovaram() == self.total_aprovadores()

    def algum_reprovou(self):
        """Verifica se algum aprovador reprovou"""
        return self.aprovadores_reprovaram() > 0

    def __repr__(self):
        return f'<BlocoAssinatura #{self.id} - {self.status}>'


class ItemBlocoAssinatura(db.Model):
    """
    Item individual do bloco de assinatura
    Representa cada aprovador
    """
    __tablename__ = 'itens_bloco_assinatura'

    id = db.Column(db.Integer, primary_key=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey('blocos_assinatura.id'), nullable=False, index=True)
    aprovador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    ordem = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pendente', index=True)
    parecer = db.Column(db.Text)
    data_assinatura = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    aprovador = db.relationship('Usuario', foreign_keys=[aprovador_id], backref='itens_aprovacao')

    def aprovar(self, parecer):
        """Marca item como aprovado"""
        self.status = 'Aprovado'
        self.parecer = parecer
        self.data_assinatura = datetime.utcnow()

    def reprovar(self, parecer):
        """Marca item como reprovado"""
        self.status = 'Reprovado'
        self.parecer = parecer
        self.data_assinatura = datetime.utcnow()

    def __repr__(self):
        return f'<Item #{self.ordem} - {self.aprovador.nome if self.aprovador else "?"} - {self.status}>'


class ValidacaoUGQ(db.Model):
    """
    Registro de validação técnica feita pelo Validador UGQ
    """
    __tablename__ = 'validacoes_ugq'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False, index=True)
    validador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    data_validacao = db.Column(db.DateTime, nullable=False)
    declaracao_sei = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    documento = db.relationship('Documento', backref='validacoes_ugq')
    validador = db.relationship('Usuario', foreign_keys=[validador_id], backref='validacoes_realizadas')

    def __repr__(self):
        return f'<ValidacaoUGQ Doc {self.documento_id} - {self.data_validacao.strftime("%d/%m/%Y")}>'


class Notificacao(db.Model):
    """
    Notificações para usuários (não são tarefas)
    Usado para informar sobre publicações, atualizações, etc.
    """
    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=True, index=True)
    tipo = db.Column(db.String(50), nullable=False)  # 'publicacao', 'atualizacao', 'aprovacao', etc.
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_leitura = db.Column(db.DateTime)

    # Relacionamentos
    usuario = db.relationship('Usuario', backref='notificacoes')
    documento = db.relationship('Documento', backref='notificacoes')

    def marcar_como_lida(self):
        """Marca notificação como lida"""
        self.lida = True
        self.data_leitura = datetime.utcnow()

    def __repr__(self):
        return f'<Notificacao {self.tipo} para User {self.usuario_id}>'
