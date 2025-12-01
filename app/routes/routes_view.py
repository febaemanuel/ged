"""
Routes VIEW - Rotas para renderizar templates HTML
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import logging

from app import db
from app.models.models import Usuario, Documento, Tarefa, LogAI
from config import Config

logger = logging.getLogger(__name__)

view_bp = Blueprint('view', __name__)

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

@view_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('view.dashboard'))
    return redirect(url_for('view.login'))


@view_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('view.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        lembrar = request.form.get('lembrar') == 'on'

        usuario = Usuario.query.filter_by(email=email).first()

        # Proteção contra timing attack: sempre faz hash check
        # mesmo se usuário não existe (usa hash dummy)
        if usuario:
            senha_valida = check_password_hash(usuario.senha_hash, senha)
        else:
            # Hash dummy para manter timing constante
            # Formato bcrypt: $2b$12$...
            hash_dummy = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lW.oYdQeWqXe'
            check_password_hash(hash_dummy, senha)
            senha_valida = False

        if usuario and senha_valida:
            login_user(usuario, remember=lembrar)
            usuario.ultimo_acesso = datetime.utcnow()
            db.session.commit()

            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('view.dashboard'))
        else:
            flash('Email ou senha inválidos', 'danger')

    return render_template('login.html')


@view_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('view.login'))


# ============================================================================
# DASHBOARD
# ============================================================================

@view_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    # Estatísticas
    stats = {
        'minhas_pendentes': Tarefa.query.filter_by(
            responsavel_id=current_user.id,
            concluida=False
        ).count(),
        'minhas_atrasadas': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        ).count(),
        'minhas_concluidas_mes': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
        ).count(),
        'total_documentos': Documento.query.count()
    }

    # Minhas tarefas pendentes (últimas 10)
    tarefas = Tarefa.query.filter_by(
        responsavel_id=current_user.id,
        concluida=False
    ).order_by(Tarefa.prazo.asc()).limit(10).all()

    return render_template('dashboard.html', stats=stats, tarefas=tarefas)


@view_bp.route('/dashboard-executivo')
@login_required
def dashboard_executivo():
    """Dashboard Executivo - Apenas para Admin e Validadores UGQ"""
    if not (current_user.is_admin() or current_user.is_validador_ugq()):
        flash('Sem permissão para acessar o Dashboard Executivo', 'error')
        return redirect(url_for('view.dashboard'))

    # Busca tipos do banco
    from app.models.models import TipoDocumento
    tipos_documento = TipoDocumento.query.filter_by(ativo=True).order_by(TipoDocumento.ordem).all()

    return render_template('dashboard_executivo.html', tipos_documento=tipos_documento)


# ============================================================================
# DOCUMENTOS
# ============================================================================

@view_bp.route('/documentos')
@login_required
def documentos():
    """Lista de documentos"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtros
    query = Documento.query
    busca = request.args.get('q')
    status = request.args.get('status')
    tipo = request.args.get('tipo')
    setor = request.args.get('setor')

    if busca:
        query = query.filter(
            (Documento.titulo.ilike(f'%{busca}%')) |
            (Documento.codigo_provisorio.ilike(f'%{busca}%')) |
            (Documento.codigo_definitivo.ilike(f'%{busca}%')) |
            (Documento.codigo_unico.ilike(f'%{busca}%'))
        )
    if status:
        query = query.filter_by(status=status)
    if tipo:
        query = query.filter_by(tipo_documento=tipo)
    if setor:
        query = query.filter_by(setor=setor)

    documentos = query.order_by(Documento.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Busca tipos do banco
    from app.models.models import TipoDocumento
    tipos_documento = TipoDocumento.query.filter_by(ativo=True).order_by(TipoDocumento.ordem).all()

    return render_template('documentos.html', documentos=documentos, tipos_documento=tipos_documento)


@view_bp.route('/documento/<int:id>')
def documento_detalhe(id):
    """Detalhes do documento - acesso público para documentos publicados"""
    documento = Documento.query.get_or_404(id)

    # Se documento está publicado, permite acesso público
    # Se não está publicado, requer autenticação
    if documento.status != 'Publicado':
        if not current_user.is_authenticated:
            flash('Este documento requer autenticação', 'warning')
            return redirect(url_for('view.login', next=request.url))

    # Verifica se usuário participou do processo
    usuario_participou = False
    if current_user.is_authenticated:
        # Verifica se é criador, triador, validador ou assinante
        usuario_participou = (
            documento.criador_id == current_user.id or
            any(t.responsavel_id == current_user.id for t in documento.tarefas)
        )

    # Timeline de tarefas
    tarefas_raw = Tarefa.query.filter_by(documento_id=id).order_by(
        Tarefa.data_criacao.desc()
    ).all()

    # Agrupa tarefas de assinatura do mesmo bloco
    tarefas = []
    blocos_processados = set()

    for tarefa in tarefas_raw:
        # Verifica se é tarefa de assinatura
        if 'Assinar Documento [Bloco #' in tarefa.tipo_tarefa:
            # Extrai número do bloco
            import re
            match = re.search(r'Bloco #(\d+)', tarefa.tipo_tarefa)
            if match:
                bloco_id = match.group(1)

                # Se já processamos este bloco, pula
                if bloco_id in blocos_processados:
                    continue

                # Marca bloco como processado
                blocos_processados.add(bloco_id)

                # Busca TODAS as tarefas deste bloco
                tarefas_bloco = [t for t in tarefas_raw if f'Bloco #{bloco_id}' in t.tipo_tarefa]

                # Cria objeto agrupado
                tarefa.is_grupo = True
                tarefa.tarefas_grupo = tarefas_bloco
                tarefa.total_grupo = len(tarefas_bloco)
                tarefa.concluidas_grupo = sum(1 for t in tarefas_bloco if t.concluida)

        tarefas.append(tarefa)

    # Logs de IA
    logs_ia = LogAI.query.filter_by(documento_id=id).order_by(
        LogAI.data_chamada.desc()
    ).limit(10).all()

    # Histórico de versões (apenas para triador/validador UGQ)
    historico_versoes = []
    pode_ver_historico = False
    if current_user.is_authenticated:
        pode_ver_historico = current_user.is_triador_ugq() or current_user.is_validador_ugq()
        if pode_ver_historico:
            historico_versoes = documento.obter_historico_versoes()

    return render_template(
        'documento_detalhe.html',
        documento=documento,
        tarefas=tarefas,
        logs_ia=logs_ia,
        usuario_participou=usuario_participou,
        historico_versoes=historico_versoes,
        pode_ver_historico=pode_ver_historico
    )


@view_bp.route('/documento/criar', methods=['GET', 'POST'])
@login_required
def documento_criar():
    """Criar novo documento"""
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        tipo_documento = request.form.get('tipo_documento')
        setor = request.form.get('setor')
        descricao = request.form.get('descricao')
        # NOVO WORKFLOW UGQ: Não precisa mais de chefia_imediata_id
        # O documento vai direto para o Triador UGQ

        # Upload do arquivo
        arquivo = request.files.get('arquivo')
        if not arquivo or arquivo.filename == '':
            flash('Arquivo é obrigatório', 'danger')
            return redirect(request.url)

        # Validar extensão
        extensao = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao not in Config.ALLOWED_EXTENSIONS_DOCUMENTO:
            flash(f'Extensão .{extensao} não permitida', 'danger')
            return redirect(request.url)

        # Salvar arquivo
        filename = secure_filename(arquivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_final = f"{timestamp}_{filename}"
        caminho_completo = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, filename_final)

        os.makedirs(Config.UPLOAD_FOLDER_DOCUMENTOS, exist_ok=True)
        arquivo.save(caminho_completo)

        # Criar documento
        # VALIDADE: Sistema define automaticamente baseado no tipo (2 ou 4 anos)
        documento = Documento(
            titulo=titulo,
            tipo_documento=tipo_documento,
            setor=setor,
            descricao=descricao,
            arquivo_original=filename_final,
            criador_id=current_user.id
            # WORKFLOW UGQ: Não precisa mais de chefia_imediata_id
            # VALIDADE: Será calculada automaticamente na publicação
        )

        # Calcular data de vencimento será feito automaticamente na publicação
        # baseado no tipo de documento (2 ou 4 anos)

        db.session.add(documento)
        db.session.commit()

        # ✅ PROCESSAR COM CELERY (ASSÍNCRONO) - Não bloqueia o request HTTP!
        processamento_agendado = False
        try:
            from tasks import processar_documento_ia
            processar_documento_ia.delay(documento.id)
            processamento_agendado = True
            flash(f'Documento {documento.codigo} criado com sucesso!', 'success')
            flash('🤖 Processamento IA iniciado em segundo plano. Você será notificado quando concluir.', 'info')
            logger.info(f"[CELERY] Tarefa de processamento IA agendada para documento {documento.id}")
        except ImportError:
            logger.warning("Celery não disponível - processamento IA não foi agendado")
            flash(f'Documento {documento.codigo} criado!', 'success')
        except Exception as e:
            logger.warning(f"Não foi possível agendar processamento IA: {str(e)}")
            flash(f'Documento {documento.codigo} criado!', 'success')

        # INICIA WORKFLOW UGQ OFICIAL EBSERH
        try:
            from app.services.workflow import WorkflowUGQ

            # Autor submete documento diretamente para a UGQ
            tarefa_criada = WorkflowUGQ.autor_submete_documento(documento)

            flash(f'✅ Documento submetido para análise da UGQ (Triador)', 'success')
            flash(f'📋 Tarefa criada: {tarefa_criada.tipo_tarefa}', 'info')
            logger.info(f"[WORKFLOW UGQ] Documento {documento.id} submetido para UGQ")
        except Exception as e:
            logger.error(f"Erro ao iniciar fluxo de aprovação: {str(e)}")
            flash('Documento criado, mas erro ao criar tarefa automática', 'warning')

        return redirect(url_for('view.documento_detalhe', id=documento.id))

    # GET: Busca gerentes para seleção de Chefia Imediata
    gerentes = Usuario.query.filter(
        Usuario.perfil.in_(['gerente', 'administrador']),
        Usuario.ativo == True
    ).order_by(Usuario.nome).all()

    # Busca tipos de documento e setores do banco
    from app.models.models import TipoDocumento, Setor
    tipos_documento = TipoDocumento.query.filter_by(ativo=True).order_by(TipoDocumento.codigo).all()
    setores = Setor.query.filter_by(ativo=True).order_by(Setor.nome).all()

    return render_template('documento_criar.html', gerentes=gerentes, tipos_documento=tipos_documento, setores=setores)


@view_bp.route('/documento/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def documento_editar(id):
    """Editar documento existente"""
    documento = Documento.query.get_or_404(id)

    # Verifica permissão
    if not documento.pode_editar(current_user):
        flash('Você não tem permissão para editar este documento', 'danger')
        return redirect(url_for('view.documento_detalhe', id=id))

    if request.method == 'POST':
        documento.titulo = request.form.get('titulo')
        documento.tipo_documento = request.form.get('tipo_documento')
        documento.setor = request.form.get('setor')
        documento.descricao = request.form.get('descricao')
        # VALIDADE: Calculada automaticamente baseado no tipo (2 ou 4 anos)

        # Campos avançados (apenas admin/triador/validador)
        if current_user.is_admin() or current_user.is_triador_ugq() or current_user.is_validador_ugq():
            abrangencia = request.form.get('abrangencia')
            if abrangencia:
                documento.abrangencia = abrangencia

        # Campos de operações avançadas (apenas admin/validador)
        if current_user.is_admin() or current_user.is_validador_ugq():
            status = request.form.get('status')
            if status:
                documento.status = status

            versao = request.form.get('versao')
            if versao:
                documento.versao = versao

            codigo_definitivo = request.form.get('codigo_definitivo')
            if codigo_definitivo:
                documento.codigo_definitivo = codigo_definitivo

            autores = request.form.get('autores')
            if autores:
                documento.autores = autores

        # Atualiza chefia se fornecida
        chefia_imediata_id = request.form.get('chefia_imediata_id', type=int)
        if chefia_imediata_id:
            documento.chefia_imediata_id = chefia_imediata_id

        # Upload de novo arquivo (opcional)
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename != '':
            # Validar extensão
            extensao = arquivo.filename.rsplit('.', 1)[1].lower()
            if extensao not in Config.ALLOWED_EXTENSIONS_DOCUMENTO:
                flash(f'Extensão .{extensao} não permitida', 'danger')
                return redirect(request.url)

            # Salvar novo arquivo
            filename = secure_filename(arquivo.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_final = f"{timestamp}_{filename}"
            caminho_completo = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, filename_final)

            os.makedirs(Config.UPLOAD_FOLDER_DOCUMENTOS, exist_ok=True)
            arquivo.save(caminho_completo)

            # Remove arquivo antigo
            if documento.arquivo_original:
                caminho_antigo = documento.get_caminho_arquivo()
                if caminho_antigo and os.path.exists(caminho_antigo):
                    try:
                        os.remove(caminho_antigo)
                    except:
                        pass

            documento.arquivo_original = filename_final

            # Reprocessa com IA se houver novo arquivo
            try:
                from app.services.ai_client import extract_text, classify_document, summarize_text, extract_authors

                resultado_extracao = extract_text(caminho_completo)
                documento.texto_extraido = resultado_extracao['texto']

                if documento.texto_extraido:
                    resultado_classificacao = classify_document(documento.texto_extraido)
                    resultado_resumo = summarize_text(documento.texto_extraido, max_length=500)

                    # Extrai autores
                    autores_list = extract_authors(documento.texto_extraido)
                    if autores_list:
                        documento.autores = ', '.join(autores_list)

                    metadados = {
                        'classificacao': resultado_classificacao,
                        'resumo': resultado_resumo,
                        'autores': autores_list,
                        'processado_em': datetime.utcnow().isoformat()
                    }
                    documento.set_metadados(metadados)
            except Exception as e:
                logger.error(f"Erro ao reprocessar IA: {str(e)}")

        db.session.commit()
        flash('Documento atualizado com sucesso!', 'success')
        return redirect(url_for('view.documento_detalhe', id=id))

    # GET: Busca gerentes para seleção de Chefia Imediata
    gerentes = Usuario.query.filter(
        Usuario.perfil.in_(['gerente', 'administrador']),
        Usuario.ativo == True
    ).order_by(Usuario.nome).all()

    # Busca dados do banco
    from app.models.models import TipoDocumento, Setor, Abrangencia
    tipos_documento = TipoDocumento.query.filter_by(ativo=True).order_by(TipoDocumento.codigo).all()
    abrangencias = Abrangencia.query.filter_by(ativo=True).order_by(Abrangencia.ordem).all()
    setores_db = Setor.query.filter_by(ativo=True).order_by(Setor.nome).all()
    setores = [s.nome for s in setores_db]

    # Se o setor atual não está na lista, adiciona
    if documento.setor and documento.setor not in setores:
        setores.append(documento.setor)
        setores.sort()

    return render_template('documento_editar.html', documento=documento, gerentes=gerentes, setores=setores, tipos_documento=tipos_documento, abrangencias=abrangencias)


@view_bp.route('/documento/<int:id>/download')
def documento_download(id):
    """Download do arquivo do documento - acesso público para documentos publicados"""
    documento = Documento.query.get_or_404(id)

    # Se documento NÃO está publicado, requer autenticação
    if documento.status != 'Publicado':
        if not current_user.is_authenticated:
            flash('Este documento requer autenticação', 'warning')
            return redirect(url_for('view.login'))
        # Verifica permissões para documentos não publicados
        if not current_user.is_admin() and documento.criador_id != current_user.id:
            flash('Sem permissão para acessar este documento', 'danger')
            return redirect(url_for('view.dashboard'))

    caminho_arquivo = documento.get_caminho_arquivo()
    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        if current_user.is_authenticated:
            flash('Arquivo não encontrado', 'danger')
            return redirect(url_for('view.documento_detalhe', id=id))
        return "Arquivo não encontrado", 404

    # Para documentos publicados, usa o PDF publicado
    codigo = documento.codigo_definitivo or documento.codigo_provisorio or documento.codigo_unico
    return send_file(
        caminho_arquivo,
        as_attachment=False,  # Permite visualização no navegador
        download_name=f"{codigo}.pdf"
    )


@view_bp.route('/documento/<int:id>/download_assinaturas')
@login_required
def documento_download_assinaturas(id):
    """Download do PDF de assinaturas do documento"""
    documento = Documento.query.get_or_404(id)

    if not documento.arquivo_final:
        flash('PDF de assinaturas não encontrado', 'danger')
        return redirect(url_for('view.documento_detalhe', id=id))

    # Caminho absoluto para o PDF de assinaturas
    caminho_pdf = os.path.join(Config.ASSINATURAS_FOLDER, documento.arquivo_final)

    if not os.path.exists(caminho_pdf):
        flash(f'Arquivo PDF de assinaturas não encontrado no caminho: {caminho_pdf}', 'danger')
        logger.error(f"PDF não encontrado: {caminho_pdf}")
        return redirect(url_for('view.documento_detalhe', id=id))

    return send_file(
        caminho_pdf,
        as_attachment=True,
        download_name=f"assinaturas_{documento.codigo_definitivo or documento.codigo_unico}.pdf"
    )


@view_bp.route('/documento/<int:id>/excluir', methods=['POST'])
@login_required
def documento_excluir(id):
    """Excluir documento (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.dashboard'))

    documento = Documento.query.get_or_404(id)

    # Excluir arquivo físico se existir
    try:
        caminho_arquivo = documento.get_caminho_arquivo()
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
    except Exception as e:
        flash(f'Erro ao excluir arquivo: {str(e)}', 'warning')

    # Excluir documento do banco
    db.session.delete(documento)
    db.session.commit()

    flash('Documento excluído com sucesso', 'success')
    return jsonify({'success': True})


# ============================================================================
# TAREFAS
# ============================================================================

@view_bp.route('/tarefas')
@login_required
def tarefas():
    """Lista de tarefas"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtros
    tipo = request.args.get('tipo')
    status = request.args.get('status')
    prioridade = request.args.get('prioridade')
    atrasadas = request.args.get('atrasadas')

    # NOVO: Primeiro, buscar documentos onde o usuário está envolvido
    # (como criador, responsável de tarefa, ou participante do fluxo)
    # OTIMIZADO: Usa subqueries ao invés de carregar objetos completos
    if current_user.is_admin():
        # Admin vê todos os documentos - usa subquery eficiente
        documentos_ids_subquery = db.session.query(Documento.id)
    else:
        # Busca documentos onde o usuário está envolvido - UNION de subqueries
        from sqlalchemy import union

        # 1. Documentos criados pelo usuário
        docs_criados_subquery = db.session.query(Documento.id).filter(
            Documento.criador_id == current_user.id
        )

        # 2. Documentos onde o usuário tem/teve tarefas
        docs_com_tarefas_subquery = db.session.query(Tarefa.documento_id).filter(
            Tarefa.responsavel_id == current_user.id
        )

        # UNION das duas queries
        documentos_ids_subquery = union(docs_criados_subquery, docs_com_tarefas_subquery)

    # NOVO: Busca TODAS as tarefas desses documentos (não só as do usuário)
    # Isso permite ver o fluxo completo - usa IN com subquery
    query = Tarefa.query.filter(Tarefa.documento_id.in_(documentos_ids_subquery))

    # Aplicar filtros
    if tipo:
        query = query.filter_by(tipo_tarefa=tipo)
    if status:
        # Converte status string para boolean concluida
        if status == 'pendente':
            query = query.filter_by(concluida=False)
        elif status == 'concluida':
            query = query.filter_by(concluida=True)
    if prioridade:
        query = query.filter_by(prioridade=prioridade)
    if atrasadas:
        query = query.filter(
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        )

    tarefas_list = query.order_by(Tarefa.prazo.asc()).all()

    # Agrupa tarefas por documento
    from collections import defaultdict
    tarefas_por_documento = defaultdict(list)

    for tarefa in tarefas_list:
        tarefas_por_documento[tarefa.documento_id].append(tarefa)

    # Cria lista de grupos ordenada por prioridade (documentos com tarefas pendentes primeiro)
    grupos_documentos = []
    for documento_id, tarefas_doc in tarefas_por_documento.items():
        documento = tarefas_doc[0].documento
        pendentes = sum(1 for t in tarefas_doc if not t.concluida)
        concluidas = sum(1 for t in tarefas_doc if t.concluida)

        # Determina status atual (última tarefa vigente)
        # Prioridade: pendente mais urgente, ou última concluída
        tarefa_atual = None
        for t in sorted(tarefas_doc, key=lambda x: (x.concluida, x.prazo)):
            if not t.concluida:
                tarefa_atual = t
                break

        if not tarefa_atual and tarefas_doc:
            # Se não tem pendente, pega a última concluída
            tarefas_concluidas = [t for t in tarefas_doc if t.concluida]
            if tarefas_concluidas:
                tarefa_atual = max(tarefas_concluidas, key=lambda t: t.data_conclusao or t.data_criacao)

        # Marca quais tarefas são do usuário atual
        tarefas_com_flag = []
        for t in tarefas_doc:
            tarefas_com_flag.append({
                'tarefa': t,
                'eh_minha': t.responsavel_id == current_user.id,
                'eh_meu_documento': documento.criador_id == current_user.id
            })

        # Ordena por data de criação (ordem cronológica do fluxo)
        # Tarefas mais antigas primeiro para mostrar o histórico correto
        tarefas_ordenadas = sorted(tarefas_com_flag, key=lambda t: t['tarefa'].data_criacao)

        grupos_documentos.append({
            'documento': documento,
            'tarefas': tarefas_ordenadas,
            'total': len(tarefas_doc),
            'pendentes': pendentes,
            'concluidas': concluidas,
            'tem_pendente': pendentes > 0,
            'tarefa_atual': tarefa_atual,
            'status_atual': tarefa_atual.tipo_tarefa if tarefa_atual else 'Sem tarefas',
            'minhas_pendentes': sum(1 for t in tarefas_doc if not t.concluida and t.responsavel_id == current_user.id)
        })

    # Ordena: documentos com pendentes primeiro, depois por número de pendentes
    grupos_documentos.sort(key=lambda g: (not g['tem_pendente'], -g['pendentes']))

    # Estatísticas - conta apenas tarefas onde o usuário é RESPONSÁVEL DIRETO
    # (não todas as tarefas dos documentos)
    stats = {
        'pendentes': Tarefa.query.filter_by(
            responsavel_id=current_user.id,
            concluida=False
        ).count(),
        'atrasadas': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        ).count(),
        'concluidas_mes': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
        ).count(),
        'total': Tarefa.query.filter_by(responsavel_id=current_user.id).count(),
        'documentos_envolvidos': len(documentos_ids)  # NOVO: mostra quantos documentos está acompanhando
    }

    return render_template('tarefas.html', grupos_documentos=grupos_documentos, stats=stats)


@view_bp.route('/tarefa/<int:id>')
@login_required
def tarefa_detalhe(id):
    """Detalhes da tarefa"""
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar permissão
    if not current_user.is_admin() and tarefa.responsavel_id != current_user.id:
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.tarefas'))

    # Se for tarefa de codificação, gerar código sugerido
    codigo_sugerido = None
    if tarefa.tipo_tarefa == 'Validar e Codificar Documento':
        from app.services.workflow import WorkflowUGQ
        # Usa abrangência do documento ou 'CHUFC' como padrão
        abrangencia = tarefa.documento.abrangencia or 'CHUFC'
        codigo_sugerido = WorkflowUGQ.gerar_proximo_codigo(
            tarefa.documento.tipo_documento,
            tarefa.documento.setor,
            abrangencia
        )

    return render_template('tarefa_detalhe.html', tarefa=tarefa, codigo_sugerido=codigo_sugerido)


@view_bp.route('/tarefa/criar', methods=['GET', 'POST'])
@login_required
def tarefa_criar():
    """Criar nova tarefa"""
    if not current_user.is_gerente_ou_superior():
        flash('Apenas gerentes e administradores podem criar tarefas', 'danger')
        return redirect(url_for('view.tarefas'))

    if request.method == 'POST':
        documento_id = request.form.get('documento_id', type=int)
        tipo_tarefa = request.form.get('tipo_tarefa')
        responsavel_id = request.form.get('responsavel_id', type=int)
        descricao = request.form.get('descricao')
        prazo = request.form.get('prazo')
        prioridade = request.form.get('prioridade', 'normal')

        # Validações
        if not documento_id or not tipo_tarefa or not responsavel_id:
            flash('Preencha todos os campos obrigatórios', 'danger')
            return redirect(request.url)

        # Converter prazo
        prazo_dt = None
        if prazo:
            prazo_dt = datetime.strptime(prazo, '%Y-%m-%d')

        # Criar tarefa
        tarefa = Tarefa(
            documento_id=documento_id,
            tipo_tarefa=tipo_tarefa,
            responsavel_id=responsavel_id,
            descricao=descricao,
            prazo=prazo_dt,
            prioridade=prioridade,
            criador_id=current_user.id
        )

        db.session.add(tarefa)
        db.session.commit()

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('view.tarefa_detalhe', id=tarefa.id))

    # Listar documentos e usuários para o formulário
    documentos = Documento.query.order_by(Documento.data_criacao.desc()).all()
    usuarios = Usuario.query.filter_by(ativo=True).order_by(Usuario.nome).all()

    # Pega documento_id da query string se fornecido
    documento_id_param = request.args.get('documento_id', type=int)

    return render_template(
        'tarefa_criar.html',
        documentos=documentos,
        usuarios=usuarios,
        documento_id_pre_selecionado=documento_id_param
    )


@view_bp.route('/tarefa/<int:id>/concluir', methods=['POST'])
@login_required
def tarefa_concluir(id):
    """Concluir tarefa"""
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.tarefa_detalhe', id=id))

    if tarefa.concluida:
        flash('Tarefa já foi concluída', 'warning')
        return redirect(url_for('view.tarefa_detalhe', id=id))

    # Obter parecer
    parecer = request.form.get('parecer', '').strip()

    # Obter decisão de aprovação (do formulário vem 'aprovado' = 'true' ou 'false')
    aprovado_str = request.form.get('aprovado')
    acao = request.form.get('acao')  # Compatibilidade com código antigo

    # Para tarefas de publicação, pode ter upload de arquivo PDF
    if tarefa.tipo_tarefa == 'Publicar':
        arquivo = request.files.get('arquivo_pdf')
        if arquivo and arquivo.filename:
            extensao = arquivo.filename.rsplit('.', 1)[1].lower()
            if extensao == 'pdf':
                filename = secure_filename(arquivo.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename_final = f"publicado_{timestamp}_{filename}"
                caminho_completo = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, filename_final)

                os.makedirs(Config.UPLOAD_FOLDER_DOCUMENTOS, exist_ok=True)
                arquivo.save(caminho_completo)

                # Atualizar arquivo publicado em PDF
                tarefa.documento.arquivo_publicado_pdf = filename_final

    # Concluir tarefa
    tarefa.concluida = True
    tarefa.data_conclusao = datetime.utcnow()
    tarefa.parecer = parecer or 'Tarefa concluída'

    # Define aprovação baseado no campo 'aprovado' do formulário
    if aprovado_str == 'true':
        tarefa.aprovado = True
    elif aprovado_str == 'false':
        tarefa.aprovado = False
    # Compatibilidade com código antigo que usa 'acao'
    elif acao == 'aprovar':
        tarefa.aprovado = True
    elif acao == 'rejeitar':
        tarefa.aprovado = False

    # ============================================================================
    # WORKFLOW UGQ: Retomar fluxo após correções
    # ============================================================================
    from app.services.workflow import WorkflowUGQ

    # Caso 1: AUTOR concluiu correção (após devolução do Triador/Validador)
    if tarefa.tipo_tarefa == Config.TAREFA_REALIZAR_CORRECAO:
        try:
            # Reenvia documento para Triador UGQ fazer nova triagem
            nova_tarefa = WorkflowUGQ.autor_reenvia_apos_correcao(tarefa)
            db.session.commit()
            flash(f'✅ Correção concluída! Documento reenviado para triagem pela UGQ', 'success')
            return redirect(url_for('view.tarefas'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao retomar workflow após correção: {str(e)}")
            flash(f'❌ Erro ao retomar workflow: {str(e)}', 'danger')
            return redirect(url_for('view.tarefa_detalhe', id=id))

    # Caso 2: VALIDADOR concluiu ajustes (após reprovação de aprovador)
    elif tarefa.tipo_tarefa == Config.TAREFA_REALIZAR_AJUSTES:
        try:
            # Retorna para o Validador fazer nova codificação/validação
            nova_tarefa = WorkflowUGQ.validador_reenvia_apos_ajustes(tarefa)
            db.session.commit()
            flash(f'✅ Ajustes concluídos! Documento pronto para nova validação', 'success')
            return redirect(url_for('view.tarefas'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao retomar workflow após ajustes: {str(e)}")
            flash(f'❌ Erro ao retomar workflow: {str(e)}', 'danger')
            return redirect(url_for('view.tarefa_detalhe', id=id))

    # ============================================================================
    # Tarefas genéricas (não-UGQ)
    # ============================================================================

    # Atualizar status do documento baseado no tipo de tarefa e aprovação
    if tarefa.aprovado:
        if tarefa.tipo_tarefa == 'Revisar':
            tarefa.documento.status = 'revisao'
        elif tarefa.tipo_tarefa == 'Validar':
            tarefa.documento.status = 'aprovado'
        elif tarefa.tipo_tarefa == 'Publicar':
            tarefa.documento.status = 'publicado'
            tarefa.documento.data_publicacao = datetime.utcnow()
    elif tarefa.aprovado is False:
        tarefa.documento.status = 'rascunho'

    db.session.commit()

    # ============================================================================
    # NOTA: Workflow UGQ é gerenciado pelas rotas específicas:
    #   - concluir_triagem → cria tarefa de codificação
    #   - codificar_documento → atualiza status
    #   - criar_bloco_assinatura → cria itens de assinatura
    #   - assinar_documento → valida assinaturas
    #   - publicar_documento → publica e adiciona à Lista Mestra
    # Esta função tarefa_concluir é para tarefas genéricas (não-UGQ)
    # ============================================================================

    flash('Tarefa concluída com sucesso!', 'success')
    return redirect(url_for('view.tarefas'))


# ============================================================================
# TEMPLATES
# ============================================================================

@view_bp.route('/templates-admin')
@login_required
def templates_admin():
    """Administração de Templates - Admin e Validadores UGQ"""
    if not (current_user.is_admin() or current_user.is_validador_ugq()):
        flash('Sem permissão para acessar administração de templates', 'error')
        return redirect(url_for('view.dashboard'))

    return render_template('templates_admin.html')


# ============================================================================
# USUÁRIOS
# ============================================================================

@view_bp.route('/usuarios')
@login_required
def usuarios():
    """Lista de usuários (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.dashboard'))

    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template('usuarios.html', usuarios=usuarios)


@view_bp.route('/usuario/criar', methods=['POST'])
@login_required
def usuario_criar():
    """Criar novo usuário (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.usuarios'))

    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    perfil = request.form.get('perfil')
    setor = request.form.get('setor')
    telefone = request.form.get('telefone', '').strip()
    whatsapp_ativo = request.form.get('whatsapp_ativo') == 'true'

    # Validações
    if Usuario.query.filter_by(email=email).first():
        flash('Email já cadastrado', 'danger')
        return redirect(url_for('view.usuarios'))

    # Criar usuário
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha),
        perfil=perfil,
        setor=setor,
        telefone=telefone if telefone else None,
        whatsapp_ativo=whatsapp_ativo
    )

    db.session.add(usuario)
    db.session.commit()

    flash(f'Usuário {nome} criado com sucesso!', 'success')
    return redirect(url_for('view.usuarios'))


@view_bp.route('/usuario/<int:id>/editar', methods=['POST'])
@login_required
def usuario_editar(id):
    """Editar usuário (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.usuarios'))

    usuario = Usuario.query.get_or_404(id)

    # Atualizar campos (email NÃO pode ser alterado - campo disabled no form)
    usuario.nome = request.form.get('nome')
    # usuario.email NÃO é atualizado (disabled no form, não vem no POST)
    usuario.perfil = request.form.get('perfil')
    usuario.setor = request.form.get('setor')

    # Campos WhatsApp
    telefone = request.form.get('telefone', '').strip()
    usuario.telefone = telefone if telefone else None
    usuario.whatsapp_ativo = request.form.get('whatsapp_ativo') == 'true'

    # Campo ativo
    usuario.ativo = request.form.get('ativo') == 'true'

    # Atualizar senha apenas se fornecida
    nova_senha = request.form.get('senha')
    if nova_senha:
        usuario.senha_hash = generate_password_hash(nova_senha)

    db.session.commit()

    flash(f'Usuário {usuario.nome} atualizado com sucesso!', 'success')
    return redirect(url_for('view.usuarios'))


@view_bp.route('/usuario/<int:id>/excluir', methods=['POST'])
@login_required
def usuario_excluir(id):
    """Excluir usuário (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.usuarios'))

    if id == current_user.id:
        flash('Você não pode excluir sua própria conta', 'danger')
        return redirect(url_for('view.usuarios'))

    usuario = Usuario.query.get_or_404(id)
    nome = usuario.nome

    db.session.delete(usuario)
    db.session.commit()

    flash(f'Usuário {nome} excluído com sucesso!', 'success')
    return redirect(url_for('view.usuarios'))


# ============================================================================
# PERFIL
# ============================================================================

@view_bp.route('/perfil')
@login_required
def perfil():
    """Perfil do usuário"""
    # Estatísticas do usuário
    stats = {
        'tarefas_pendentes': Tarefa.query.filter_by(
            responsavel_id=current_user.id,
            concluida=False
        ).count(),
        'tarefas_concluidas_mes': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
        ).count(),
        'documentos_criados': Documento.query.filter_by(
            criador_id=current_user.id
        ).count()
    }

    return render_template('perfil.html', stats=stats)


@view_bp.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    """Alterar senha do usuário"""
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')
    senha_confirma = request.form.get('senha_confirma')

    # Validações
    if not check_password_hash(current_user.senha_hash, senha_atual):
        flash('Senha atual incorreta', 'danger')
        return redirect(url_for('view.perfil'))

    if senha_nova != senha_confirma:
        flash('As senhas não coincidem', 'danger')
        return redirect(url_for('view.perfil'))

    if len(senha_nova) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres', 'danger')
        return redirect(url_for('view.perfil'))

    # Atualizar senha
    current_user.senha_hash = generate_password_hash(senha_nova)
    db.session.commit()

    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('view.perfil'))


# ============================================================================
# REPOSITÓRIO PÚBLICO
# ============================================================================

@view_bp.route('/repositorio-publico')
@login_required
def repositorio_publico():
    """Repositório de documentos públicos"""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Filtros
    query = Documento.query.filter_by(status='Publicado')
    busca = request.args.get('q')
    tipo = request.args.get('tipo')
    setor = request.args.get('setor')
    palavras_chave = request.args.get('palavras_chave')
    order_by = request.args.get('order_by', 'data')

    if busca:
        query = query.filter(
            (Documento.titulo.ilike(f'%{busca}%')) |
            (Documento.codigo_provisorio.ilike(f'%{busca}%')) |
            (Documento.codigo_definitivo.ilike(f'%{busca}%')) |
            (Documento.codigo_unico.ilike(f'%{busca}%')) |
            (Documento.descricao.ilike(f'%{busca}%')) |
            (Documento.texto_extraido.ilike(f'%{busca}%'))
        )
    if tipo:
        query = query.filter_by(tipo_documento=tipo)
    if setor:
        query = query.filter_by(setor=setor)
    if palavras_chave:
        # Busca em palavras-chave extraídas pela IA (armazenadas em metadados_json)
        # Proteção contra SQL injection via ILIKE - escapa caracteres especiais
        palavras_chave_safe = palavras_chave.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        query = query.filter(Documento.metadados_json.ilike(f'%{palavras_chave_safe}%'))

    # Ordenação
    if order_by == 'setor_tipo':
        query = query.order_by(Documento.setor.asc(), Documento.tipo_documento.asc(), Documento.data_publicacao.desc())
    elif order_by == 'tipo_setor':
        query = query.order_by(Documento.tipo_documento.asc(), Documento.setor.asc(), Documento.data_publicacao.desc())
    else:  # 'data'
        query = query.order_by(Documento.data_publicacao.desc())

    documentos = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Busca abrangências do banco
    from app.models.models import Abrangencia
    abrangencias = Abrangencia.query.filter_by(ativo=True).order_by(Abrangencia.ordem).all()

    return render_template('repositorio_publico.html', documentos=documentos, abrangencias=abrangencias)


@view_bp.route('/repositorio/download/<int:doc_id>')
def download_documento_publico(doc_id):
    """
    Rota de download público para documentos publicados.
    Usada pelo chatbot WhatsApp para enviar documentos.
    """
    import os
    from flask import send_file, abort, current_app

    documento = Documento.query.get_or_404(doc_id)

    # Só permite download de documentos publicados
    if documento.status != 'Publicado':
        abort(403, description="Documento não disponível para download público")

    # Determina o arquivo a ser enviado
    # Prioridade: PDF publicado > arquivo original
    # NÃO usar arquivo_final pois é o PDF de assinaturas
    full_path = documento.get_caminho_publicado() or documento.get_caminho_arquivo()

    if not full_path:
        abort(404, description="Arquivo não encontrado")

    if not os.path.exists(full_path):
        abort(404, description="Arquivo não encontrado no servidor")

    # Determina nome do arquivo para download
    codigo = documento.codigo_definitivo or documento.codigo_provisorio or f"Doc_{doc_id}"
    nome_arquivo = f"{codigo}.pdf"

    # Se o arquivo não é PDF, usa a extensão original
    _, ext = os.path.splitext(full_path)
    if ext and ext.lower() != '.pdf':
        nome_arquivo = f"{codigo}{ext}"

    return send_file(
        full_path,
        as_attachment=True,
        download_name=nome_arquivo
    )


@view_bp.route('/setor/<setor_nome>')
def setor_view(setor_nome):
    """
    Página dedicada ao setor com dashboard completo

    Exibe:
    - Estatísticas do setor
    - Gráficos (vencidos, tipos, status, timeline)
    - Lista de documentos com filtros
    - Documentos vencidos e perto de vencer
    """
    from urllib.parse import unquote
    setor_nome = unquote(setor_nome)

    # Busca tipos de documento do banco
    from app.models.models import TipoDocumento
    tipos_documento = TipoDocumento.query.filter_by(ativo=True).order_by(TipoDocumento.ordem).all()

    return render_template(
        'setor_dashboard.html',
        setor_nome=setor_nome,
        tipos_documento=tipos_documento
    )


# ============================================================================
# ROTAS DO WORKFLOW UGQ OFICIAL EBSERH
# ============================================================================

@view_bp.route('/tarefa/<int:tarefa_id>/concluir_triagem', methods=['POST'])
@login_required
def concluir_triagem(tarefa_id):
    """
    ETAPA 1: Triador UGQ conclui triagem (3 checkpoints)
    """
    from app.services.workflow import WorkflowUGQ

    tarefa = Tarefa.query.get_or_404(tarefa_id)

    # Verifica permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para concluir esta tarefa', 'danger')
        return redirect(url_for('view.tarefas'))

    # Pega dados do formulário
    acao = request.form.get('acao')  # 'aprovar' ou 'devolver'
    parecer = request.form.get('parecer')

    # Checkpoints
    checkpoint_1 = request.form.get('checkpoint_1')  # 'sim' ou 'nao'
    checkpoint_2 = request.form.get('checkpoint_2', 'nao_se_aplica')  # 'sim', 'nao', 'nao_se_aplica'
    checkpoint_3 = request.form.get('checkpoint_3')  # 'sim' ou 'nao'

    tarefa.parecer = parecer

    # Verifica se é um documento do tipo Manual (aceita MAN, Manual, MANUAL)
    tipo_doc = tarefa.documento.tipo_documento or ''
    eh_manual = tipo_doc in ['Manual', 'MAN', 'MANUAL'] or tipo_doc.upper().startswith('MAN')

    try:
        if acao == 'aprovar' and checkpoint_1 == 'nao' and checkpoint_3 == 'sim':
            # Todos checkpoints OK
            if eh_manual:
                # Manual precisa de validação do colegiado
                if checkpoint_2 == 'nao':
                    # Devolve
                    WorkflowUGQ.triador_devolve_ao_autor(tarefa, 'Manual precisa ser validado pelo Colegiado Executivo')
                    flash('❌ Documento devolvido ao autor: falta validação do Colegiado', 'warning')
                else:
                    # Aprova
                    WorkflowUGQ.triador_aprova_triagem(tarefa)
                    flash('✅ Triagem aprovada! Documento enviado para Validador UGQ', 'success')
            else:
                # Não é manual, aprova
                WorkflowUGQ.triador_aprova_triagem(tarefa)
                flash('✅ Triagem aprovada! Documento enviado para Validador UGQ', 'success')

        elif acao == 'devolver' or checkpoint_1 == 'sim' or checkpoint_3 == 'nao':
            # Devolver ao autor
            motivo = parecer
            if checkpoint_1 == 'sim':
                motivo = 'Documento já existe na Lista Mestra'
            elif checkpoint_3 == 'nao':
                motivo = f'Formatação fora do padrão. {parecer}'

            WorkflowUGQ.triador_devolve_ao_autor(tarefa, motivo)
            flash('❌ Documento devolvido ao autor para correção', 'warning')

        else:
            flash('❌ Erro: ação inválida', 'danger')

    except Exception as e:
        logger.error(f"Erro ao concluir triagem: {str(e)}")
        flash(f'Erro ao processar triagem: {str(e)}', 'danger')

    return redirect(url_for('view.tarefas'))


@view_bp.route('/tarefa/<int:tarefa_id>/codificar', methods=['GET', 'POST'])
@login_required
def codificar_documento(tarefa_id):
    """
    ETAPA 2: Validador UGQ codifica documento
    """
    from app.services.workflow import WorkflowUGQ
    from app.models.models import ListaMestra

    tarefa = Tarefa.query.get_or_404(tarefa_id)
    documento = tarefa.documento

    # Verifica permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para esta tarefa', 'danger')
        return redirect(url_for('view.tarefas'))

    if request.method == 'GET':
        # Não sugere código aqui - será gerado via JavaScript após selecionar abrangência
        return render_template('tarefa_detalhe.html',
            tarefa=tarefa,
            documento=documento,
            codigo_sugerido=None,  # Será gerado via AJAX após selecionar abrangência
            modo='codificar'
        )

    # POST: Processa codificação
    codigo_definitivo = request.form.get('codigo_definitivo')
    versao = request.form.get('versao', 'v1.0')
    observacoes_validacao = request.form.get('observacoes_validacao', '')
    abrangencia = request.form.get('abrangencia', '')

    # Valida abrangência
    if not abrangencia:
        flash('Abrangência é obrigatória', 'danger')
        return redirect(url_for('view.tarefa_detalhe', id=tarefa_id))

    try:
        WorkflowUGQ.validador_codifica_documento(
            tarefa,
            codigo_definitivo,
            versao,
            observacoes_validacao,
            abrangencia
        )

        flash(f'✅ Documento codificado: {codigo_definitivo}', 'success')
        flash('Agora crie o Bloco de Assinatura', 'info')

        return redirect(url_for('view.criar_bloco_assinatura', documento_id=documento.id))

    except Exception as e:
        logger.error(f"Erro ao codificar documento: {str(e)}")
        flash(f'Erro ao codificar: {str(e)}', 'danger')
        return redirect(url_for('view.tarefa_detalhe', id=tarefa_id))


@view_bp.route('/tarefa/<int:tarefa_id>/validador_devolver', methods=['POST'])
@login_required
def validador_devolver_documento(tarefa_id):
    """
    ETAPA 2/3: Validador UGQ devolve documento
    """
    from app.services.workflow import WorkflowUGQ

    tarefa = Tarefa.query.get_or_404(tarefa_id)
    documento = tarefa.documento

    # Verifica permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para esta ação', 'danger')
        return redirect(url_for('view.tarefas'))

    destino = request.form.get('destino')  # 'triador' ou 'autor'
    motivo = request.form.get('motivo')

    try:
        if destino == 'triador':
            WorkflowUGQ.validador_devolve_para_triador(documento, current_user.id, motivo)
            flash('📤 Documento devolvido para o Triador UGQ', 'warning')
        elif destino == 'autor':
            WorkflowUGQ.validador_devolve_para_autor(documento, current_user.id, motivo)
            flash('📤 Documento devolvido para o Autor', 'warning')
        else:
            flash('❌ Destino inválido', 'danger')

        # Marca tarefa atual como concluída
        tarefa.concluida = True
        tarefa.aprovado = False
        tarefa.data_conclusao = datetime.utcnow()
        tarefa.parecer = f'Devolvido para {destino}: {motivo}'
        db.session.commit()

    except Exception as e:
        logger.error(f"Erro ao devolver documento: {str(e)}")
        flash(f'Erro: {str(e)}', 'danger')

    return redirect(url_for('view.tarefas'))


@view_bp.route('/documento/<int:documento_id>/bloco_assinatura/criar', methods=['GET', 'POST'])
@login_required
def criar_bloco_assinatura(documento_id):
    """
    ETAPA 3: Validador UGQ cria Bloco de Assinatura
    """
    from app.services.workflow import WorkflowUGQ

    documento = Documento.query.get_or_404(documento_id)

    # Verifica se é Validador UGQ
    if current_user.perfil != Config.PERFIL_QUALIDADE_VALIDADOR and not current_user.is_admin():
        flash('Apenas Validador UGQ pode criar Bloco de Assinatura', 'danger')
        return redirect(url_for('view.documento_detalhe', id=documento_id))

    if request.method == 'GET':
        # Lista aprovadores disponíveis
        aprovadores = Usuario.query.filter(
            Usuario.perfil.in_([Config.PERFIL_GERENTE]),
            Usuario.ativo == True
        ).all()

        return render_template('documento_detalhe.html',
            documento=documento,
            aprovadores=aprovadores,
            modo='criar_bloco'
        )

    # POST: Cria bloco
    modo = request.form.get('modo', 'sequencial')
    observacoes = request.form.get('observacoes', '')

    # Coleta aprovadores
    aprovadores_ids = []
    ordem = 1
    while True:
        aprovador_id = request.form.get(f'aprovador_{ordem}', type=int)
        if not aprovador_id:
            break
        aprovadores_ids.append(aprovador_id)
        ordem += 1

    if not aprovadores_ids:
        flash('Adicione pelo menos um aprovador', 'danger')
        return redirect(request.url)

    try:
        bloco = WorkflowUGQ.validador_cria_bloco_assinatura(
            documento,
            current_user.id,
            aprovadores_ids,
            modo,
            observacoes
        )

        flash(f'✅ Bloco de Assinatura #{bloco.id} criado!', 'success')
        flash(f'📧 Tarefas enviadas para {len(aprovadores_ids)} aprovador(es)', 'info')

        return redirect(url_for('view.documento_detalhe', id=documento_id))

    except Exception as e:
        logger.error(f"Erro ao criar bloco: {str(e)}")
        flash(f'Erro: {str(e)}', 'danger')
        return redirect(request.url)


@view_bp.route('/tarefa/<int:tarefa_id>/assinar', methods=['POST'])
@login_required
def assinar_documento(tarefa_id):
    """
    ETAPA 3: Aprovador assina documento com verificação de senha
    """
    from app.services.workflow import WorkflowUGQ

    tarefa = Tarefa.query.get_or_404(tarefa_id)

    # Verifica permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para assinar este documento', 'danger')
        return redirect(url_for('view.tarefas'))

    acao = request.form.get('acao')  # 'aprovar', 'reprovar', ou 'devolver'
    parecer = request.form.get('parecer')
    senha = request.form.get('senha')  # Senha para confirmar assinatura

    # Captura IP e User-Agent
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')[:255]

    # Se a ação for devolver, chama função específica
    if acao == 'devolver':
        try:
            WorkflowUGQ.aprovador_devolve_para_validador(tarefa, parecer)
            flash('📤 Documento devolvido para o Validador UGQ', 'warning')
        except Exception as e:
            logger.error(f"Erro ao devolver documento: {str(e)}")
            flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('view.tarefas'))

    # Caso contrário, é assinatura normal (aprovar ou reprovar)
    aprovado = (acao == 'aprovar')

    try:
        resultado = WorkflowUGQ.aprovador_assina(
            tarefa,
            aprovado,
            parecer,
            senha=senha,
            ip_address=ip_address,
            user_agent=user_agent
        )

        if aprovado:
            if resultado.get('proximo') == 'publicacao':
                flash('🎉 Todos aprovaram! Documento enviado para publicação', 'success')
            elif resultado.get('proximo') == 'proximo_aprovador':
                flash('✅ Assinatura registrada! Enviado para próximo aprovador', 'success')
            elif resultado.get('proximo') == 'aguardando':
                pendentes = resultado.get('pendentes', 0)
                flash(f'✅ Assinatura registrada! Aguardando {pendentes} aprovador(es)', 'info')
        else:
            flash('❌ Documento reprovado. Devolvido para Validador UGQ', 'warning')

    except ValueError as e:
        # Erros de validação (senha incorreta, etc.)
        flash(f'❌ {str(e)}', 'danger')
    except Exception as e:
        logger.error(f"Erro ao assinar: {str(e)}")
        flash(f'Erro: {str(e)}', 'danger')

    return redirect(url_for('view.tarefas'))


@view_bp.route('/tarefa/<int:tarefa_id>/publicar', methods=['POST'])
@login_required
def publicar_documento(tarefa_id):
    """
    ETAPA 4: Validador UGQ publica documento
    """
    from app.services.workflow import WorkflowUGQ

    tarefa = Tarefa.query.get_or_404(tarefa_id)

    # Verifica permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Você não tem permissão para publicar', 'danger')
        return redirect(url_for('view.tarefas'))

    try:
        # Atualiza dados confirmados antes de publicar
        documento = tarefa.documento
        titulo_confirmado = request.form.get('titulo_confirmado', '').strip()
        autores_confirmados = request.form.get('autores_confirmados', '').strip()
        descricao_confirmada = request.form.get('descricao_confirmada', '').strip()

        if titulo_confirmado:
            documento.titulo = titulo_confirmado
        if autores_confirmados:
            documento.autores = autores_confirmados
        if descricao_confirmada:
            documento.descricao = descricao_confirmada

        db.session.commit()
        logger.info(f"[PUBLICACAO] Dados confirmados - Título: {titulo_confirmado}, Autores: {autores_confirmados}")

        documento = WorkflowUGQ.validador_publica_documento(tarefa)

        flash(f'🎉 Documento {documento.codigo_definitivo} publicado com sucesso!', 'success')
        flash('📊 Status: VIGENTE na Lista Mestra', 'info')

        return redirect(url_for('view.documento_detalhe', id=documento.id))

    except Exception as e:
        logger.error(f"Erro ao publicar: {str(e)}")
        flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('view.tarefa_detalhe', id=tarefa_id))


@view_bp.route('/documento/<int:id>/restaurar', methods=['POST'])
@login_required
def documento_restaurar_versao(id):
    """
    Restaura uma versão anterior do documento
    Apenas triadores e validadores UGQ podem restaurar versões
    """
    # Verifica permissão
    if not (current_user.is_triador_ugq() or current_user.is_validador_ugq()):
        flash('Apenas triadores e validadores UGQ podem restaurar versões', 'danger')
        return redirect(url_for('view.documento_detalhe', id=id))

    versao_antiga = Documento.query.get_or_404(id)
    motivo = request.form.get('motivo', 'Restauração de versão anterior')

    try:
        # Restaura a versão (cria nova versão baseada na antiga)
        nova_versao = versao_antiga.restaurar_versao(
            usuario_id=current_user.id,
            motivo=motivo
        )

        flash(f'✅ Versão {versao_antiga.versao or "antiga"} restaurada com sucesso!', 'success')
        flash(f'📝 Nova versão {nova_versao.versao} criada e enviada para análise', 'info')

        # Redireciona para a nova versão
        return redirect(url_for('view.documento_detalhe', id=nova_versao.id))

    except Exception as e:
        logger.error(f"Erro ao restaurar versão: {str(e)}")
        db.session.rollback()
        flash(f'Erro ao restaurar versão: {str(e)}', 'danger')
        return redirect(url_for('view.documento_detalhe', id=id))


# ============================================================================
# API: GERAÇÃO DE CÓDIGO DINÂMICO
# ============================================================================

@view_bp.route('/api/gerar-codigo', methods=['POST'])
@login_required
def api_gerar_codigo():
    """
    API para gerar código dinamicamente baseado em tipo, setor e abrangência
    """
    from flask import jsonify
    from app.services.workflow import WorkflowUGQ

    try:
        tipo = request.form.get('tipo')
        setor = request.form.get('setor')
        abrangencia = request.form.get('abrangencia')

        if not all([tipo, setor, abrangencia]):
            return jsonify({'error': 'Tipo, setor e abrangência são obrigatórios'}), 400

        codigo = WorkflowUGQ.gerar_proximo_codigo(tipo, setor, abrangencia)

        return jsonify({'codigo': codigo})

    except Exception as e:
        logger.error(f"Erro ao gerar código: {str(e)}")
        return jsonify({'error': str(e)}), 500
