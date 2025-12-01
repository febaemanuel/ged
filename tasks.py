"""
Tasks do Celery para Sistema GED EBSERH
Tarefas executadas em background
"""
import os
import logging
from datetime import datetime, timedelta
from celery import Task
from celery_app import celery

# Configuração de logging
logger = logging.getLogger(__name__)


# ============================================================================
# CLASSE BASE COM CONTEXTO DO FLASK
# ============================================================================

class FlaskTask(Task):
    """
    Classe base que configura contexto Flask para tasks
    Necessário para acessar db.session, current_app, etc.
    """
    _app = None

    @property
    def app_context(self):
        if self._app is None:
            from app import create_app
            self._app = create_app(os.getenv('FLASK_ENV', 'production'))
        return self._app.app_context()

    def __call__(self, *args, **kwargs):
        with self.app_context:
            return self.run(*args, **kwargs)


# ============================================================================
# PROCESSAMENTO DE DOCUMENTOS
# ============================================================================

@celery.task(base=FlaskTask, bind=True, max_retries=3)
def processar_documento_ia(self, documento_id):
    """
    Processa documento com IA (DeepSeek)
    - Extrai texto do PDF/DOCX
    - Analisa com IA
    - Extrai metadados
    - Salva resultados

    Args:
        documento_id: ID do documento a processar

    Returns:
        dict: Resultado do processamento
    """
    from app.models import db
    from app.models.models import Documento, LogAI
    from app.services.ai_client import AIClient

    try:
        logger.info(f"Iniciando processamento IA do documento {documento_id}")

        # Busca documento
        documento = Documento.query.get(documento_id)
        if not documento:
            logger.error(f"Documento {documento_id} não encontrado")
            return {'status': 'error', 'message': 'Documento não encontrado'}

        # Extrai texto do arquivo
        logger.info(f"Extraindo texto do arquivo: {documento.arquivo_original}")
        from PyPDF2 import PdfReader
        import docx

        arquivo_path = os.path.join('app/uploads/documentos', documento.arquivo_original)

        texto = ""
        if documento.arquivo_original.endswith('.pdf'):
            reader = PdfReader(arquivo_path)
            texto = "\n".join([page.extract_text() for page in reader.pages])
        elif documento.arquivo_original.endswith('.docx'):
            doc = docx.Document(arquivo_path)
            texto = "\n".join([para.text for para in doc.paragraphs])
        else:
            # ODT ou outros formatos
            with open(arquivo_path, 'r', encoding='utf-8', errors='ignore') as f:
                texto = f.read()

        documento.texto_extraido = texto[:50000]  # Limita a 50k caracteres

        # Processa com IA (se API key configurada)
        if os.getenv('AI_API_KEY'):
            logger.info("Processando com IA DeepSeek")
            ai_client = AIClient()

            # Análise do documento
            resultado_ia = ai_client.analisar_documento(texto[:10000])  # Primeiros 10k chars

            # Salva metadados
            documento.metadados_json = resultado_ia.get('metadados', {})

            # Log da operação
            log = LogAI(
                documento_id=documento_id,
                tipo_operacao='analise_completa',
                prompt_enviado=f"Analisar documento: {documento.titulo}",
                resposta_recebida=str(resultado_ia),
                modelo_utilizado=os.getenv('AI_API_MODEL', 'deepseek-chat'),
                tokens_usados=resultado_ia.get('tokens', 0)
            )
            db.session.add(log)

        # Salva alterações
        db.session.commit()

        logger.info(f"Processamento IA concluído para documento {documento_id}")

        # ✅ CRIA NOTIFICAÇÃO NO SISTEMA (para UI)
        if documento.criador:
            from app.models.models import Notificacao
            Notificacao.criar(
                usuario_id=documento.criador_id,
                tipo='processamento_ia',
                titulo='✅ Documento processado pela IA',
                mensagem=f'O documento "{documento.titulo}" foi analisado automaticamente e está pronto!',
                link=f'/documento/{documento_id}'
            )
            logger.info(f"Notificação criada para usuário {documento.criador_id}")

            # Também envia email (opcional)
            enviar_notificacao_email.delay(
                usuario_id=documento.criador_id,
                assunto='Documento processado',
                mensagem=f'O documento "{documento.titulo}" foi processado com sucesso!'
            )

        return {
            'status': 'success',
            'documento_id': documento_id,
            'texto_length': len(texto),
            'metadados': documento.metadados_json
        }

    except Exception as exc:
        logger.error(f"Erro ao processar documento {documento_id}: {str(exc)}")
        # Retry automático com backoff exponencial
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery.task(base=FlaskTask)
def gerar_pdf_publicado(documento_id):
    """
    Gera versão PDF publicada do documento

    Args:
        documento_id: ID do documento
    """
    from app.models import db
    from app.models.models import Documento
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    try:
        logger.info(f"Gerando PDF publicado para documento {documento_id}")

        documento = Documento.query.get(documento_id)
        if not documento:
            return {'status': 'error', 'message': 'Documento não encontrado'}

        # Gera PDF
        pdf_path = f"app/uploads/publicados/{documento.codigo_definitivo or documento_id}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=A4)

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, documento.titulo)

        # Metadados
        c.setFont("Helvetica", 10)
        y = 760
        c.drawString(50, y, f"Código: {documento.codigo_definitivo or 'N/A'}")
        y -= 20
        c.drawString(50, y, f"Tipo: {documento.tipo_documento}")
        y -= 20
        c.drawString(50, y, f"Setor: {documento.setor}")
        y -= 20
        c.drawString(50, y, f"Data: {datetime.now().strftime('%d/%m/%Y')}")

        # Conteúdo (simplificado)
        y -= 40
        c.setFont("Helvetica", 9)
        if documento.texto_extraido:
            lines = documento.texto_extraido.split('\n')[:50]  # Primeiras 50 linhas
            for line in lines:
                if y < 50:
                    c.showPage()
                    y = 800
                c.drawString(50, y, line[:80])  # 80 caracteres por linha
                y -= 15

        c.save()

        # Atualiza documento
        documento.arquivo_publicado_pdf = os.path.basename(pdf_path)
        db.session.commit()

        logger.info(f"PDF publicado gerado: {pdf_path}")
        return {'status': 'success', 'pdf_path': pdf_path}

    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ============================================================================
# TAREFAS AGENDADAS (CRON)
# ============================================================================

@celery.task(base=FlaskTask)
def verificar_documentos_vencidos():
    """
    Verifica e marca documentos vencidos como Obsoleto
    Executado diariamente às 2h da manhã
    """
    from app.models import db
    from app.models.models import Documento

    try:
        logger.info("Iniciando verificação de documentos vencidos")

        agora = datetime.utcnow()

        # Busca documentos vencidos
        documentos_vencidos = Documento.query.filter(
            Documento.data_vencimento != None,
            Documento.data_vencimento < agora,
            Documento.status == 'Publicado'
        ).all()

        total = 0
        for doc in documentos_vencidos:
            doc.status = 'Obsoleto'
            total += 1

            # Notifica criador
            if doc.criador:
                enviar_notificacao_email.delay(
                    usuario_id=doc.criador_id,
                    assunto='Documento vencido',
                    mensagem=f'O documento "{doc.titulo}" venceu em {doc.data_vencimento.strftime("%d/%m/%Y")}'
                )

        db.session.commit()

        logger.info(f"Marcados {total} documentos como Obsoleto")
        return {'status': 'success', 'total': total}

    except Exception as e:
        logger.error(f"Erro ao verificar documentos vencidos: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(base=FlaskTask)
def alertar_documentos_vencendo():
    """
    Envia alertas para documentos próximos de vencer (30 dias)
    Executado diariamente às 9h da manhã
    """
    from app.models import db
    from app.models.models import Documento

    try:
        logger.info("Verificando documentos próximos de vencer")

        agora = datetime.utcnow()
        data_limite = agora + timedelta(days=30)

        # Busca documentos vencendo em 30 dias
        documentos = Documento.query.filter(
            Documento.data_vencimento != None,
            Documento.data_vencimento >= agora,
            Documento.data_vencimento <= data_limite,
            Documento.status == 'Publicado'
        ).all()

        total = 0
        for doc in documentos:
            dias = (doc.data_vencimento - agora).days

            # Notifica responsável
            if doc.criador:
                enviar_notificacao_email.delay(
                    usuario_id=doc.criador_id,
                    assunto=f'Documento vence em {dias} dias',
                    mensagem=f'O documento "{doc.titulo}" vence em {dias} dias ({doc.data_vencimento.strftime("%d/%m/%Y")}). Providencie revisão!'
                )
                total += 1

        logger.info(f"Enviados {total} alertas de vencimento")
        return {'status': 'success', 'total': total}

    except Exception as e:
        logger.error(f"Erro ao alertar vencimentos: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(base=FlaskTask)
def backup_banco_dados():
    """
    Realiza backup do banco de dados PostgreSQL
    Executado diariamente às 3h da manhã
    """
    import subprocess
    from datetime import date

    try:
        logger.info("Iniciando backup do banco de dados")

        # Configurações do banco
        db_name = os.getenv('DB_NAME', 'ged_db')
        db_user = os.getenv('DB_USER', 'ged_user')
        db_password = os.getenv('DB_PASSWORD', 'ged_password')
        db_host = os.getenv('DB_HOST', 'localhost')

        # Nome do arquivo de backup
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = f"{backup_dir}/ged_backup_{date.today()}.sql"

        # Comando pg_dump
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-U', db_user,
            '-d', db_name,
            '-f', backup_file,
            '--clean',
            '--if-exists'
        ]

        # Executa backup
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Backup criado com sucesso: {backup_file}")

            # Remove backups antigos (>7 dias)
            import glob
            cutoff = datetime.now() - timedelta(days=7)
            for old_backup in glob.glob(f"{backup_dir}/ged_backup_*.sql"):
                if os.path.getmtime(old_backup) < cutoff.timestamp():
                    os.remove(old_backup)
                    logger.info(f"Backup antigo removido: {old_backup}")

            return {'status': 'success', 'backup_file': backup_file}
        else:
            logger.error(f"Erro no backup: {result.stderr}")
            return {'status': 'error', 'message': result.stderr}

    except Exception as e:
        logger.error(f"Erro ao fazer backup: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery.task(base=FlaskTask)
def limpar_logs_antigos():
    """
    Remove logs de IA e WhatsApp com mais de 90 dias
    Executado semanalmente aos domingos às 4h
    """
    from app.models import db
    from app.models.models import LogAI, LogWhatsApp

    try:
        logger.info("Limpando logs antigos")

        cutoff_date = datetime.utcnow() - timedelta(days=90)

        # Remove logs de IA
        logs_ia_deletados = LogAI.query.filter(
            LogAI.data_hora < cutoff_date
        ).delete()

        # Remove logs de WhatsApp
        logs_whats_deletados = LogWhatsApp.query.filter(
            LogWhatsApp.data_hora < cutoff_date
        ).delete()

        db.session.commit()

        total = logs_ia_deletados + logs_whats_deletados
        logger.info(f"Removidos {total} logs antigos (IA: {logs_ia_deletados}, WhatsApp: {logs_whats_deletados})")

        return {
            'status': 'success',
            'total': total,
            'logs_ia': logs_ia_deletados,
            'logs_whatsapp': logs_whats_deletados
        }

    except Exception as e:
        logger.error(f"Erro ao limpar logs: {str(e)}")
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}


# ============================================================================
# NOTIFICAÇÕES
# ============================================================================

@celery.task(base=FlaskTask, bind=True, max_retries=3)
def enviar_notificacao_email(self, usuario_id, assunto, mensagem):
    """
    Envia email de notificação para usuário

    Args:
        usuario_id: ID do usuário
        assunto: Assunto do email
        mensagem: Corpo do email
    """
    from app.models.models import Usuario
    from app.services.email_service import EmailService

    try:
        logger.info(f"Enviando email para usuário {usuario_id}")

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            logger.warning(f"Usuário {usuario_id} não encontrado")
            return {'status': 'error', 'message': 'Usuário não encontrado'}

        # Envia email
        email_service = EmailService()
        email_service.enviar_notificacao(
            destinatario=usuario.email,
            assunto=assunto,
            corpo=mensagem
        )

        logger.info(f"Email enviado com sucesso para {usuario.email}")
        return {'status': 'success', 'email': usuario.email}

    except Exception as exc:
        logger.error(f"Erro ao enviar email: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry em 5 minutos


@celery.task(base=FlaskTask)
def enviar_notificacoes_setor(setor, assunto, mensagem):
    """
    Envia notificação para todos usuários de um setor

    Args:
        setor: Nome do setor
        assunto: Assunto
        mensagem: Mensagem
    """
    from app.models.models import Usuario

    try:
        logger.info(f"Enviando notificações para setor: {setor}")

        usuarios = Usuario.query.filter_by(setor=setor, ativo=True).all()

        total = 0
        for usuario in usuarios:
            # Envia em background (cada email é uma task separada)
            enviar_notificacao_email.delay(usuario.id, assunto, mensagem)
            total += 1

        logger.info(f"Agendados {total} emails para o setor {setor}")
        return {'status': 'success', 'total': total}

    except Exception as e:
        logger.error(f"Erro ao enviar notificações: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ============================================================================
# RELATÓRIOS
# ============================================================================

@celery.task(base=FlaskTask, bind=True)
def gerar_relatorio_pdf(self, tipo_relatorio, parametros=None):
    """
    Gera relatório em PDF (pode ser demorado)

    Args:
        tipo_relatorio: Tipo do relatório (mensal, anual, etc)
        parametros: Parâmetros adicionais
    """
    from app.services.report_generator import ReportGenerator

    try:
        logger.info(f"Gerando relatório: {tipo_relatorio}")

        # Atualiza progresso
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100})

        generator = ReportGenerator()

        if tipo_relatorio == 'mensal':
            pdf_path = generator.gerar_relatorio_mensal(parametros)
        elif tipo_relatorio == 'anual':
            pdf_path = generator.gerar_relatorio_anual(parametros)
        else:
            raise ValueError(f"Tipo de relatório desconhecido: {tipo_relatorio}")

        self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100})

        logger.info(f"Relatório gerado: {pdf_path}")
        return {'status': 'success', 'pdf_path': pdf_path}

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return {'status': 'error', 'message': str(e)}
