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

    # WhatsApp
    telefone = db.Column(db.String(20))  # Formato: +5585999999999
    whatsapp_ativo = db.Column(db.Boolean, default=True)  # Aceita notificações WhatsApp

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

    def is_triador_ugq(self):
        """Verifica se o usuário é Triador UGQ"""
        from config import Config
        return self.perfil == Config.PERFIL_QUALIDADE_TRIADOR

    def is_validador_ugq(self):
        """Verifica se o usuário é Validador UGQ"""
        from config import Config
        return self.perfil == Config.PERFIL_QUALIDADE_VALIDADOR

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Documento(db.Model):
    """
    Modelo de Documento do sistema GED

    Status possíveis (Workflow UGQ):
    - Novo
    - Em Triagem (Triador UGQ)
    - Em Validação (Validador UGQ)
    - Em Correção (Autor corrige)
    - Validado (Codificado pelo Validador)
    - Em Aprovação (Bloco de Assinatura)
    - Em Ajustes (Reprovado, precisa ajustes)
    - Aprovado
    - Publicado
    - Cancelado
    - Obsoleto
    """
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)

    # Informações básicas
    titulo = db.Column(db.String(200), nullable=False, index=True)  # ✅ Índice para busca
    tipo_documento = db.Column(db.String(50), nullable=False, index=True)  # ✅ Índice para filtros
    descricao = db.Column(db.Text)
    setor = db.Column(db.String(100), index=True)  # ✅ Índice para filtros por setor
    abrangencia = db.Column(db.String(100), index=True)  # ✅ Índice para filtros por abrangência
    autores = db.Column(db.Text)  # Autores extraídos pela IA (formato JSON ou texto)

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
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)  # ✅ Índice
    data_publicacao = db.Column(db.DateTime, index=True)  # ✅ Índice para ordenação
    validade_anos = db.Column(db.Integer, default=5)
    data_vencimento = db.Column(db.DateTime, index=True)  # ✅ Índice para alertas de vencimento

    # Status e controle
    status = db.Column(db.String(50), default='Novo', nullable=False, index=True)

    # ✅ SOFT DELETE - Para auditoria e recuperação
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    # ✅ AUDITORIA - Rastreamento de alterações
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    # IA - texto e metadados extraídos
    texto_extraido = db.Column(db.Text)
    metadados_json = db.Column(db.Text)  # JSON string com resultados da IA

    # Relacionamentos
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)  # ✅ Índice
    chefia_imediata_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Chefia para aprovação
    tarefas = db.relationship('Tarefa', backref='documento', lazy='dynamic',
                             cascade='all, delete-orphan')
    logs_ia = db.relationship('LogAI', backref='documento', lazy='dynamic',
                             cascade='all, delete-orphan')

    # ✅ ÍNDICES COMPOSTOS para queries complexas
    __table_args__ = (
        db.Index('ix_doc_setor_tipo', 'setor', 'tipo_documento'),
        db.Index('ix_doc_status_vencimento', 'status', 'data_vencimento'),
        db.Index('ix_doc_abrangencia_setor', 'abrangencia', 'setor'),
        db.Index('ix_doc_criador_status', 'criador_id', 'status'),
        db.Index('ix_doc_data_criacao_status', 'data_criacao', 'status'),
    )

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
            except (ValueError, IndexError, AttributeError):
                seq = 1
        else:
            seq = 1

        self.codigo_definitivo = f"{prefixo}-DEF-{data}-{seq:04d}"

    def calcular_data_vencimento(self):
        """
        Calcula data de vencimento com base no tipo de documento (regra automática)

        Regras EBSERH:
        - Política, Regimento, Regulamento: 4 anos
        - POP, Manual, Protocolo: 2 anos
        """
        if self.data_publicacao and self.tipo_documento:
            from config import Config

            # Define validade baseada no tipo
            if self.tipo_documento in Config.TIPOS_VALIDADE_4_ANOS:
                anos = 4
            else:
                anos = 2

            # Atualiza campo validade_anos para refletir a regra
            self.validade_anos = anos

            # Calcula data de vencimento
            self.data_vencimento = self.data_publicacao + timedelta(days=anos * 365)

    @property
    def tipo_documento_nome(self):
        """
        Retorna o nome completo do tipo de documento.
        Ex: se tipo_documento = 'MAN', retorna 'Manual'
        """
        if not self.tipo_documento:
            return ''

        # Busca o tipo de documento pelo código
        tipo_obj = TipoDocumento.query.filter_by(codigo=self.tipo_documento).first()
        if tipo_obj:
            return tipo_obj.nome

        # Se não encontrar, retorna o próprio código
        return self.tipo_documento

    def esta_vencido(self):
        """Verifica se o documento está vencido"""
        if self.data_vencimento:
            return datetime.utcnow() > self.data_vencimento
        return False

    @property
    def codigo(self):
        """Retorna o código preferido (definitivo > provisório > único)"""
        return self.codigo_definitivo or self.codigo_provisorio or self.codigo_unico

    @property
    def titulo_completo(self):
        """Retorna título formatado: CODIGO - TITULO"""
        codigo = self.codigo_definitivo or self.codigo_provisorio or f"DOC-{self.id}"
        if self.titulo:
            return f"{codigo} - {self.titulo}"
        return codigo

    def dias_ate_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        if self.data_vencimento:
            delta = self.data_vencimento - datetime.utcnow()
            return delta.days
        return None

    def proxima_vencimento(self, dias=30):
        """Verifica se o documento vence nos próximos X dias"""
        if self.data_vencimento and not self.esta_vencido():
            dias_restantes = self.dias_ate_vencimento()
            if dias_restantes is not None and dias_restantes <= dias:
                return True
        return False

    def get_metadados(self):
        """Retorna metadados como dicionário"""
        if self.metadados_json:
            try:
                return json.loads(self.metadados_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return {}

    def set_metadados(self, dados):
        """Define metadados a partir de dicionário"""
        self.metadados_json = json.dumps(dados, ensure_ascii=False)

    def pode_editar(self, usuario):
        """Verifica se o usuário pode editar o documento"""
        if usuario.is_admin():
            return True

        # Autor pode editar SOMENTE se tem tarefa de correção pendente pra ele
        # OU se o documento ainda está em status inicial (Novo ou Em Correção)
        if usuario.id == self.criador_id:
            # Pode editar se está em status inicial ou em correção (Workflow UGQ)
            if self.status in ['Novo', 'Em Correção', 'Em Triagem']:
                return True

            # OU se tem tarefa de correção pendente
            from app.models.models import Tarefa
            from config import Config
            tem_tarefa_correcao = Tarefa.query.filter_by(
                documento_id=self.id,
                responsavel_id=usuario.id,
                concluida=False,
                tipo_tarefa=Config.TAREFA_REALIZAR_CORRECAO
            ).first()

            if tem_tarefa_correcao:
                return True

            return False

        # Triador UGQ pode editar durante triagem (workflow normal)
        if usuario.is_triador_ugq() and self.status == 'Em Triagem':
            return True

        # Validador UGQ pode editar durante validação ou ajustes
        if usuario.is_validador_ugq() and self.status in ['Em Validação', 'Em Ajustes', 'Validado']:
            return True

        # Gerentes e superiores podem editar sempre
        return usuario.is_gerente_ou_superior()

    def pode_publicar(self):
        """Verifica se o documento pode ser publicado"""
        return self.status == 'Aprovado'

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

    def obter_historico_versoes(self):
        """
        Retorna todas as versões do documento em ordem cronológica (mais antiga → mais nova)

        Returns:
            list: Lista de documentos ordenados por data_criacao

        Note:
            Inclui proteção contra ciclos de versionamento para evitar loops infinitos.
        """
        versoes = []
        visited_ids = set()  # Proteção contra ciclos

        # Busca versão anterior recursivamente
        versao_atual = self
        while versao_atual.versao_anterior_id:
            # Proteção contra ciclos - evita loop infinito
            if versao_atual.versao_anterior_id in visited_ids:
                import logging
                logging.getLogger(__name__).warning(
                    f"Ciclo detectado no versionamento do documento {self.id}. "
                    f"ID repetido: {versao_atual.versao_anterior_id}"
                )
                break

            visited_ids.add(versao_atual.versao_anterior_id)
            versao_anterior = Documento.query.get(versao_atual.versao_anterior_id)
            if versao_anterior:
                versoes.append(versao_anterior)  # Usando append ao invés de insert(0)
                versao_atual = versao_anterior
            else:
                break

        # Reverte a lista para ordem cronológica correta (mais eficiente que insert(0))
        versoes.reverse()

        # Adiciona versão atual
        versoes.append(self)

        # Busca versões posteriores (que substituíram esta)
        versoes_posteriores = self.obter_versoes_posteriores()
        versoes.extend(versoes_posteriores)

        return versoes

    def obter_versao_anterior(self):
        """Retorna o documento que esta versão substituiu"""
        if self.versao_anterior_id:
            return Documento.query.get(self.versao_anterior_id)
        return None

    def obter_versoes_posteriores(self):
        """
        Retorna todas as versões que substituíram este documento (recursivamente)

        Returns:
            list: Lista de documentos que são versões posteriores

        Note:
            Inclui proteção contra ciclos de versionamento para evitar loops infinitos.
        """
        versoes = []
        visited_ids = set()  # Proteção contra ciclos
        visited_ids.add(self.id)  # Marca o atual como visitado

        # Busca documentos que apontam para este como versao_anterior_id
        proxima_versao = Documento.query.filter_by(versao_anterior_id=self.id).first()

        while proxima_versao:
            # Proteção contra ciclos - evita loop infinito
            if proxima_versao.id in visited_ids:
                import logging
                logging.getLogger(__name__).warning(
                    f"Ciclo detectado nas versões posteriores do documento {self.id}. "
                    f"ID repetido: {proxima_versao.id}"
                )
                break

            visited_ids.add(proxima_versao.id)
            versoes.append(proxima_versao)
            # Busca próxima versão recursivamente
            proxima_versao = Documento.query.filter_by(versao_anterior_id=proxima_versao.id).first()

        return versoes

    def obter_versao_atual(self):
        """Retorna a versão mais recente deste documento"""
        versoes_posteriores = self.obter_versoes_posteriores()
        if versoes_posteriores:
            return versoes_posteriores[-1]  # Última versão
        return self  # Esta já é a versão atual

    def eh_versao_atual(self):
        """Verifica se este documento é a versão mais recente"""
        # Se não existe versão posterior, é a atual
        versao_posterior = Documento.query.filter_by(versao_anterior_id=self.id).first()
        return versao_posterior is None

    # ✅ MÉTODOS DE SOFT DELETE
    def soft_delete(self, usuario_id=None):
        """Marca documento como deletado sem remover do banco"""
        self.deleted_at = datetime.utcnow()
        self.status = 'Deletado'
        if usuario_id:
            self.updated_by_id = usuario_id

    def restore(self, usuario_id=None):
        """Restaura documento deletado"""
        self.deleted_at = None
        self.status = 'Novo'
        if usuario_id:
            self.updated_by_id = usuario_id

    @classmethod
    def query_active(cls):
        """Retorna query apenas de documentos não deletados"""
        return cls.query.filter(cls.deleted_at.is_(None))

    def restaurar_versao(self, usuario_id, motivo="Restauração de versão anterior"):
        """
        Restaura uma versão anterior criando uma nova versão baseada nesta

        Args:
            usuario_id: ID do usuário que está restaurando
            motivo: Motivo da restauração

        Returns:
            Documento: Nova versão criada
        """
        import shutil
        import os
        from flask import current_app

        # Obtém a versão atual (mais recente)
        versao_atual = self.obter_versao_atual()

        # Calcula número da próxima versão
        if versao_atual.versao:
            try:
                # Extrai número da versão (ex: "v2.0" -> 2.0)
                numero_versao = float(versao_atual.versao.replace('v', '').replace('V', ''))
                proxima_versao = f"v{numero_versao + 1:.1f}"
            except (ValueError, AttributeError):
                proxima_versao = "v2.0"
        else:
            proxima_versao = "v2.0"

        # Cria nova versão baseada nesta versão antiga
        nova_versao = Documento(
            titulo=self.titulo,
            tipo_documento=self.tipo_documento,
            descricao=f"{self.descricao}\n\n[RESTAURADO EM {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}] {motivo}",
            setor=self.setor,
            versao=proxima_versao,
            versao_anterior_id=versao_atual.id,  # Aponta para a versão atual
            criador_id=usuario_id,
            status='Em Triagem',  # Workflow UGQ: volta para triagem
            validade_anos=self.validade_anos,
            codigo_definitivo=versao_atual.codigo_definitivo,  # Mantém mesmo código definitivo
            texto_extraido=self.texto_extraido,
            metadados_json=self.metadados_json
        )

        # Copia arquivos se existirem
        if self.arquivo_original and os.path.exists(self.get_caminho_arquivo()):
            # Gera novo nome de arquivo
            ext = os.path.splitext(self.arquivo_original)[1]
            novo_nome = f"restaurado_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{ext}"
            novo_caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], novo_nome)

            # Copia arquivo
            shutil.copy2(self.get_caminho_arquivo(), novo_caminho)
            nova_versao.arquivo_original = novo_nome

        if self.arquivo_publicado_pdf and os.path.exists(self.get_caminho_publicado()):
            # Gera novo nome de arquivo
            novo_nome_pdf = f"restaurado_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
            novo_caminho_pdf = os.path.join(current_app.config['PUBLISHED_FOLDER'], novo_nome_pdf)

            # Copia arquivo
            shutil.copy2(self.get_caminho_publicado(), novo_caminho_pdf)
            nova_versao.arquivo_publicado_pdf = novo_nome_pdf

        # Atualiza status da versão atual para ANTIGO
        versao_atual.status = 'ANTIGO'

        db.session.add(nova_versao)
        db.session.commit()

        return nova_versao

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

    # ✅ ÍNDICES COMPOSTOS para queries de tarefas
    __table_args__ = (
        db.Index('ix_tarefas_responsavel_concluida', 'responsavel_id', 'concluida'),
        db.Index('ix_tarefas_documento_concluida', 'documento_id', 'concluida'),
        db.Index('ix_tarefas_prazo_concluida', 'prazo', 'concluida'),
    )

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
            except (json.JSONDecodeError, TypeError, ValueError):
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
    abrangencia = db.Column(db.String(100))  # CHUFC, HUWC, MEAC, etc
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

    # Assinatura digital profissional
    assinatura_hash = db.Column(db.String(255))  # SHA-256 hash da assinatura
    ip_address = db.Column(db.String(45))  # IP de onde foi assinado (IPv4 ou IPv6)
    user_agent = db.Column(db.String(255))  # Navegador/sistema usado

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    aprovador = db.relationship('Usuario', foreign_keys=[aprovador_id], backref='itens_aprovacao')

    def aprovar(self, parecer, senha_hash=None, ip_address=None, user_agent=None):
        """Marca item como aprovado com assinatura digital"""
        self.status = 'Aprovado'
        self.parecer = parecer
        self.data_assinatura = datetime.utcnow()
        self.assinatura_hash = senha_hash
        self.ip_address = ip_address
        self.user_agent = user_agent

    def reprovar(self, parecer, senha_hash=None, ip_address=None, user_agent=None):
        """Marca item como reprovado"""
        self.status = 'Reprovado'
        self.parecer = parecer
        self.data_assinatura = datetime.utcnow()
        self.assinatura_hash = senha_hash
        self.ip_address = ip_address
        self.user_agent = user_agent

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
    Modelo de Notificações do Sistema

    Tipos de notificação:
    - processamento_ia: Documento processado pela IA
    - tarefa_atribuida: Nova tarefa atribuída
    - documento_aprovado: Documento aprovado
    - documento_reprovado: Documento reprovado/ajustes
    - documento_vencendo: Documento próximo de vencer
    - documento_vencido: Documento venceu
    - comentario: Novo comentário em documento
    - publicacao: Documento publicado
    - atualizacao: Documento atualizado
    - mencao_comentario: Usuário mencionado em comentário
    - resposta_comentario: Resposta a comentário
    - revisao: Nova versão de documento
    """
    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=True, index=True)
    tipo = db.Column(db.String(50), nullable=False, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500))  # URL para onde a notificação aponta
    lida = db.Column(db.Boolean, default=False, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_leitura = db.Column(db.DateTime)

    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('notificacoes', lazy='dynamic'))
    documento = db.relationship('Documento', backref='notificacoes')

    def marcar_como_lida(self):
        """Marca notificação como lida"""
        if not self.lida:
            self.lida = True
            self.data_leitura = datetime.utcnow()
            db.session.commit()

    @classmethod
    def criar(cls, usuario_id, tipo, titulo, mensagem, link=None, documento_id=None):
        """
        Método helper para criar notificação

        Args:
            usuario_id: ID do usuário
            tipo: Tipo de notificação
            titulo: Título
            mensagem: Mensagem
            link: URL de destino (opcional)
            documento_id: ID do documento relacionado (opcional)

        Returns:
            Notificacao: Objeto criado
        """
        notificacao = cls(
            usuario_id=usuario_id,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            link=link,
            documento_id=documento_id
        )
        db.session.add(notificacao)
        db.session.commit()
        return notificacao

    @classmethod
    def nao_lidas_usuario(cls, usuario_id):
        """Retorna notificações não lidas de um usuário"""
        return cls.query.filter_by(usuario_id=usuario_id, lida=False).order_by(cls.data_criacao.desc()).all()

    @classmethod
    def contar_nao_lidas(cls, usuario_id):
        """Conta notificações não lidas de um usuário"""
        return cls.query.filter_by(usuario_id=usuario_id, lida=False).count()

    @classmethod
    def marcar_todas_lidas(cls, usuario_id):
        """Marca todas notificações de um usuário como lidas"""
        notificacoes = cls.query.filter_by(usuario_id=usuario_id, lida=False).all()
        for notif in notificacoes:
            notif.lida = True
            notif.data_leitura = datetime.utcnow()
        db.session.commit()
        return len(notificacoes)

    def __repr__(self):
        return f'<Notificacao {self.id} - {self.tipo} - Usuario {self.usuario_id}>'


class TemplateDocumento(db.Model):
    """
    Templates pré-aprovados para criação de documentos
    Facilita a padronização EBSERH e reduz erros de formatação
    """
    __tablename__ = 'templates_documento'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    tipo_documento = db.Column(db.String(50), nullable=False)  # POP, Manual, Protocolo
    setor = db.Column(db.String(100))  # null = disponível para todos
    arquivo_template = db.Column(db.String(255), nullable=False)  # Arquivo base
    ativo = db.Column(db.Boolean, default=True, index=True)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Campos de preenchimento automático (JSON)
    # Ex: {"campos": ["nome_procedimento", "setor", "responsavel"]}
    campos_json = db.Column(db.Text)

    # Contador de uso
    vezes_utilizado = db.Column(db.Integer, default=0)

    # Relacionamentos
    criador = db.relationship('Usuario', backref='templates_criados')

    def get_campos(self):
        """Retorna campos como dicionário"""
        if self.campos_json:
            try:
                return json.loads(self.campos_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return {}

    def set_campos(self, dados):
        """Define campos a partir de dicionário"""
        self.campos_json = json.dumps(dados, ensure_ascii=False)

    def incrementar_uso(self):
        """Incrementa contador de uso"""
        self.vezes_utilizado += 1

    def pode_usar(self, usuario):
        """Verifica se usuário pode usar este template"""
        if not self.ativo:
            return False
        # Template sem setor específico = disponível para todos
        if not self.setor:
            return True
        # Template de setor específico = apenas para aquele setor
        return usuario.setor == self.setor

    def __repr__(self):
        return f'<TemplateDocumento {self.nome}>'


class Comentario(db.Model):
    """
    Sistema de comentários e discussões em documentos
    Suporta @menções e threads de discussão
    """
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)

    # Conteúdo
    texto = db.Column(db.Text, nullable=False)

    # Thread (comentário pai para respostas)
    pai_id = db.Column(db.Integer, db.ForeignKey('comentarios.id'), nullable=True, index=True)

    # Menções (lista de IDs de usuários mencionados)
    # Ex: "[1, 3, 5]" para usuários com IDs 1, 3 e 5
    mencoes_json = db.Column(db.Text)

    # Seção do documento (opcional - para comentários contextualizados)
    secao = db.Column(db.String(200))

    # Controle
    editado = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_edicao = db.Column(db.DateTime)

    # Relacionamentos
    documento = db.relationship('Documento', backref='comentarios')
    usuario = db.relationship('Usuario', backref='comentarios')
    respostas = db.relationship('Comentario', backref=db.backref('pai', remote_side=[id]),
                                lazy='dynamic', cascade='all, delete-orphan')

    def get_mencoes(self):
        """Retorna lista de IDs de usuários mencionados"""
        if self.mencoes_json:
            try:
                return json.loads(self.mencoes_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                return []
        return []

    def set_mencoes(self, usuario_ids):
        """Define menções a partir de lista de IDs"""
        self.mencoes_json = json.dumps(usuario_ids)

    def extrair_mencoes_do_texto(self):
        """
        Extrai @menções do texto e retorna lista de emails mencionados
        Ex: "@joao.silva@hospital.com fica responsável" -> ["joao.silva@hospital.com"]
        """
        import re
        # Padrão: @email
        padrao = r'@([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(padrao, self.texto)
        return emails

    def processar_mencoes(self):
        """
        Processa menções no texto e salva IDs dos usuários
        Retorna lista de usuários mencionados
        """
        emails = self.extrair_mencoes_do_texto()
        if not emails:
            return []

        # Busca usuários pelos emails
        usuarios = Usuario.query.filter(Usuario.email.in_(emails)).all()
        usuario_ids = [u.id for u in usuarios]

        self.set_mencoes(usuario_ids)
        return usuarios

    def editar_texto(self, novo_texto):
        """Edita o texto do comentário"""
        self.texto = novo_texto
        self.editado = True
        self.data_edicao = datetime.utcnow()

    def pode_editar(self, usuario):
        """Verifica se usuário pode editar este comentário"""
        return usuario.id == self.usuario_id or usuario.is_admin()

    def pode_deletar(self, usuario):
        """Verifica se usuário pode deletar este comentário"""
        return usuario.id == self.usuario_id or usuario.is_admin()

    def total_respostas(self):
        """Retorna total de respostas (recursivo)"""
        return self.respostas.count()

    def __repr__(self):
        return f'<Comentario #{self.id} no Doc {self.documento_id}>'
# MODELOS - WHATSAPP CHATBOT
# ============================================================================


class ConfiguracaoWhatsApp(db.Model):
    """
    Configurações globais do WhatsApp para o sistema
    Gerenciado apenas por administradores
    """
    __tablename__ = 'configuracao_whatsapp'

    id = db.Column(db.Integer, primary_key=True)

    # Status
    ativo = db.Column(db.Boolean, default=False, nullable=False)  # WhatsApp ativado/desativado

    # Credenciais Twilio (DEPRECATED - mantido para compatibilidade)
    twilio_account_sid = db.Column(db.String(100))
    twilio_auth_token = db.Column(db.String(100))
    twilio_whatsapp_number = db.Column(db.String(20))  # Ex: +14155238886

    # Credenciais Evolution API (NOVO - recomendado)
    evolution_api_url = db.Column(db.String(200))  # Ex: https://api.evolution.com
    evolution_instance_name = db.Column(db.String(100))  # Ex: minha_instancia
    evolution_api_key = db.Column(db.String(200))  # API Key da Evolution

    # Configurações de uso
    usar_para_notificacoes = db.Column(db.Boolean, default=True)  # Notificar tarefas novas
    usar_para_assinaturas = db.Column(db.Boolean, default=True)  # Permitir assinar via WhatsApp
    usar_para_lembretes = db.Column(db.Boolean, default=True)  # Enviar lembretes de prazo

    # Método de confirmação: 'email', 'whatsapp', 'ambos'
    metodo_confirmacao = db.Column(db.String(20), default='ambos')  # Como enviar notificações

    # Segurança
    exigir_2fa = db.Column(db.Boolean, default=False)  # Exigir código 2FA além da senha
    timeout_sessao_minutos = db.Column(db.Integer, default=15)  # Timeout da conversa
    deletar_mensagens_sensiveis = db.Column(db.Boolean, default=True)  # Deletar msgs com senha

    # Horários de funcionamento
    horario_inicio = db.Column(db.String(5), default='08:00')  # HH:MM
    horario_fim = db.Column(db.String(5), default='18:00')  # HH:MM
    dias_semana = db.Column(db.String(50), default='1,2,3,4,5')  # 1=Seg, 7=Dom

    # Templates de mensagens (JSON)
    templates_json = db.Column(db.Text)  # JSON com templates customizáveis

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    atualizado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    # Relacionamento
    atualizado_por = db.relationship('Usuario', foreign_keys=[atualizado_por_id])

    @classmethod
    def get_config(cls):
        """Retorna configuração única do sistema (singleton)"""
        config = cls.query.first()
        if not config:
            # Cria configuração padrão
            config = cls(
                ativo=False,
                usar_para_notificacoes=True,
                usar_para_assinaturas=True,
                usar_para_lembretes=True,
                metodo_confirmacao='ambos',
                exigir_2fa=False,
                timeout_sessao_minutos=15,
                deletar_mensagens_sensiveis=True
            )
            db.session.add(config)
            db.session.commit()
        return config

    def get_templates(self):
        """Retorna templates como dicionário"""
        if self.templates_json:
            try:
                return json.loads(self.templates_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                return self._templates_padrao()
        return self._templates_padrao()

    def set_templates(self, templates):
        """Define templates a partir de dicionário"""
        self.templates_json = json.dumps(templates, ensure_ascii=False)

    def _templates_padrao(self):
        """Templates padrão de mensagens"""
        return {
            'boas_vindas': '👋 Olá {nome}! Bem-vindo ao Sistema GED EBSERH.',
            'menu_principal': '📋 *Documentos Pendentes ({total})*\n\n{lista}\n\n💬 *Responda o número do documento*',
            'documento_detalhes': '📄 *{codigo}*\n{titulo}\n\n👤 Autor: {autor}\n⏰ Prazo: {prazo}\n\n💬 *O que deseja fazer?*\n1️⃣ - Aprovar e assinar\n2️⃣ - Reprovar\n3️⃣ - Ver documento completo\n4️⃣ - Voltar',
            'pedir_senha': '🔒 *Digite sua senha para confirmar:*\n\n⚠️ A senha será apagada após validação.',
            'assinatura_sucesso': '✅ *Assinatura registrada!*\n\n📋 {codigo}\n⏰ {timestamp}\n🔐 Hash: {hash}\n\n📧 Comprovante enviado para {email}',
            'senha_incorreta': '❌ Senha incorreta! Tente novamente.',
            'sessao_expirada': '⏰ Sessão expirada. Digite *menu* para começar novamente.',
            'fora_horario': '⏰ Atendimento disponível de {inicio} às {fim}, de segunda a sexta.',
            'numero_nao_cadastrado': '❌ Número não cadastrado no sistema GED.'
        }

    def esta_em_horario_funcionamento(self):
        """Verifica se está no horário de funcionamento"""
        from datetime import datetime

        agora = datetime.now()

        # Verifica dia da semana (1=Seg, 7=Dom)
        dia_semana = str(agora.isoweekday())
        if dia_semana not in self.dias_semana.split(','):
            return False

        # Verifica horário
        hora_atual = agora.strftime('%H:%M')
        if hora_atual < self.horario_inicio or hora_atual > self.horario_fim:
            return False

        return True

    def __repr__(self):
        return f'<ConfiguracaoWhatsApp ativo={self.ativo}>'


class ConversacaoWhatsApp(db.Model):
    """
    Armazena estado de conversações ativas do WhatsApp
    Usado para manter contexto entre mensagens
    """
    __tablename__ = 'conversacoes_whatsapp'

    id = db.Column(db.Integer, primary_key=True)

    # Identificação
    telefone = db.Column(db.String(20), unique=True, nullable=False, index=True)  # whatsapp:+5585999999999
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)

    # Estado da conversa
    estado_atual = db.Column(db.String(50))  # 'menu', 'aguardando_senha', 'aguardando_justificativa', etc
    contexto_json = db.Column(db.Text)  # JSON com dados do contexto (tarefa_id, documento_id, etc)

    # Segurança
    tentativas_senha = db.Column(db.Integer, default=0)  # Contador de tentativas de senha
    bloqueado_ate = db.Column(db.DateTime)  # Bloqueia após muitas tentativas

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultima_mensagem_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento
    usuario = db.relationship('Usuario', backref='conversacoes_whatsapp')

    def get_contexto(self):
        """Retorna contexto como dicionário"""
        if self.contexto_json:
            try:
                return json.loads(self.contexto_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return {}

    def set_contexto(self, contexto):
        """Define contexto a partir de dicionário"""
        self.contexto_json = json.dumps(contexto, ensure_ascii=False)

    def atualizar_estado(self, novo_estado, contexto=None):
        """Atualiza estado da conversa"""
        self.estado_atual = novo_estado
        if contexto:
            self.set_contexto(contexto)
        self.ultima_mensagem_em = datetime.utcnow()

    def esta_ativa(self, timeout_minutos=15):
        """Verifica se conversa ainda está ativa"""
        if not self.ultima_mensagem_em:
            return False

        timeout = timedelta(minutes=timeout_minutos)
        return (datetime.utcnow() - self.ultima_mensagem_em) < timeout

    def esta_bloqueado(self):
        """Verifica se usuário está temporariamente bloqueado"""
        if not self.bloqueado_ate:
            return False
        return datetime.utcnow() < self.bloqueado_ate

    def incrementar_tentativa_senha(self):
        """Incrementa contador de tentativas de senha"""
        self.tentativas_senha += 1

        # Bloqueia por 30 minutos após 3 tentativas
        if self.tentativas_senha >= 3:
            self.bloqueado_ate = datetime.utcnow() + timedelta(minutes=30)

    def resetar_tentativas(self):
        """Reseta contador de tentativas"""
        self.tentativas_senha = 0
        self.bloqueado_ate = None

    def expirar(self):
        """Expira a conversa"""
        self.estado_atual = 'expirado'
        self.set_contexto({})

    def __repr__(self):
        return f'<ConversacaoWhatsApp {self.telefone} - {self.estado_atual}>'


class LogWhatsApp(db.Model):
    """
    Log de mensagens enviadas/recebidas via WhatsApp
    Para auditoria e troubleshooting
    """
    __tablename__ = 'logs_whatsapp'

    id = db.Column(db.Integer, primary_key=True)

    # Identificação
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), index=True)
    telefone = db.Column(db.String(20), nullable=False)

    # Mensagem
    direcao = db.Column(db.String(10), nullable=False)  # 'enviada' ou 'recebida'
    mensagem = db.Column(db.Text, nullable=False)
    twilio_sid = db.Column(db.String(100))  # ID da mensagem no Twilio

    # Contexto
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), index=True)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefas.id'), index=True)

    # Status
    status = db.Column(db.String(20))  # 'enviado', 'entregue', 'lido', 'falhou'
    erro = db.Column(db.Text)  # Mensagem de erro se falhou

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relacionamentos
    usuario = db.relationship('Usuario', backref='logs_whatsapp')
    documento = db.relationship('Documento', backref='logs_whatsapp')
    tarefa = db.relationship('Tarefa', backref='logs_whatsapp')

    def __repr__(self):
        return f'<LogWhatsApp {self.direcao} - {self.telefone}>'


# ============================================================================
# MODELOS - CONFIGURAÇÕES DO SISTEMA (EDITÁVEIS)
# ============================================================================


class Abrangencia(db.Model):
    """
    Abrangências do Complexo Hospitalar (CHUFC, HUWC, MEAC)
    Editável pelo administrador
    """
    __tablename__ = 'abrangencias'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)  # CHUFC, HUWC, MEAC
    nome = db.Column(db.String(200), nullable=False)  # Nome completo
    descricao = db.Column(db.Text)
    cor = db.Column(db.String(20), default='#2563eb')  # Cor para exibição
    icone = db.Column(db.String(50), default='bi-building')  # Ícone Bootstrap
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)  # Ordem de exibição
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    setores = db.relationship('Setor', backref='abrangencia_rel', lazy='dynamic')

    @classmethod
    def get_all_active(cls):
        """Retorna todas as abrangências ativas ordenadas"""
        return cls.query.filter_by(ativo=True).order_by(cls.ordem).all()

    @classmethod
    def get_by_codigo(cls, codigo):
        """Busca abrangência pelo código"""
        return cls.query.filter_by(codigo=codigo).first()

    def __repr__(self):
        return f'<Abrangencia {self.codigo}>'


class TipoDocumento(db.Model):
    """
    Tipos de documento (POP, Manual, Protocolo, etc)
    Editável pelo administrador
    """
    __tablename__ = 'tipos_documento'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)  # POP, MAN, PROT (já é a abreviação)
    nome = db.Column(db.String(100), nullable=False)  # Nome completo
    descricao = db.Column(db.Text)
    validade_anos = db.Column(db.Integer, default=2)  # Validade padrão em anos
    prefixo_codigo = db.Column(db.String(20))  # Prefixo para geração de código (ex: POP, MAN)
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_all_active(cls):
        """Retorna todos os tipos ativos ordenados"""
        return cls.query.filter_by(ativo=True).order_by(cls.ordem).all()

    @classmethod
    def get_by_codigo(cls, codigo):
        """Busca tipo pelo código"""
        return cls.query.filter_by(codigo=codigo).first()

    def __repr__(self):
        return f'<TipoDocumento {self.codigo}>'


class Setor(db.Model):
    """
    Setores/Departamentos por abrangência
    Editável pelo administrador
    """
    __tablename__ = 'setores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    abrangencia_id = db.Column(db.Integer, db.ForeignKey('abrangencias.id'), nullable=False)
    descricao = db.Column(db.Text)
    sigla = db.Column(db.String(20))  # Sigla opcional
    responsavel = db.Column(db.String(200))  # Nome do responsável
    email = db.Column(db.String(200))  # Email de contato
    telefone = db.Column(db.String(50))
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_by_abrangencia(cls, abrangencia_id):
        """Retorna setores de uma abrangência"""
        return cls.query.filter_by(abrangencia_id=abrangencia_id, ativo=True).order_by(cls.nome).all()

    @classmethod
    def get_all_active(cls):
        """Retorna todos os setores ativos"""
        return cls.query.filter_by(ativo=True).order_by(cls.nome).all()

    def __repr__(self):
        return f'<Setor {self.nome}>'


class PerfilPermissao(db.Model):
    """
    Perfis de usuário e suas permissões
    Editável pelo administrador
    """
    __tablename__ = 'perfis_permissao'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)  # comum, gerente, admin
    nome = db.Column(db.String(100), nullable=False)  # Nome amigável
    descricao = db.Column(db.Text)
    cor = db.Column(db.String(20), default='#6b7280')  # Cor para badge
    nivel = db.Column(db.Integer, default=0)  # Nível hierárquico (0=comum, 10=admin)
    ativo = db.Column(db.Boolean, default=True)

    # Permissões (JSON com lista de permissões)
    permissoes_json = db.Column(db.Text)

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_permissoes(self):
        """Retorna lista de permissões"""
        if self.permissoes_json:
            try:
                return json.loads(self.permissoes_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                return []
        return []

    def set_permissoes(self, permissoes):
        """Define permissões a partir de lista"""
        self.permissoes_json = json.dumps(permissoes, ensure_ascii=False)

    def tem_permissao(self, permissao):
        """Verifica se perfil tem determinada permissão"""
        return permissao in self.get_permissoes()

    @classmethod
    def get_all_active(cls):
        """Retorna todos os perfis ativos ordenados por nível"""
        return cls.query.filter_by(ativo=True).order_by(cls.nivel).all()

    @classmethod
    def get_by_codigo(cls, codigo):
        """Busca perfil pelo código"""
        return cls.query.filter_by(codigo=codigo).first()

    def __repr__(self):
        return f'<PerfilPermissao {self.codigo}>'


# NOTA: Classe Notificacao foi removida desta posição para evitar duplicação.
# A definição principal está nas linhas 794-822 acima.
