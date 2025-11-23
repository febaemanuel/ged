"""
Rotas de Documentos do Sistema GED

Endpoints:
- GET /documentos - Lista documentos
- GET /documento/<id> - Visualiza documento e timeline
- POST /documento/criar - Cria novo documento
- PUT /documento/<id> - Atualiza documento
- DELETE /documento/<id> - Remove documento
- GET /documento/<id>/download - Download do arquivo
- GET /publico - Repositório público de documentos publicados
"""

from flask import Blueprint, request, jsonify, send_file, current_app, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from datetime import datetime
import os
import logging

from app.models import db, Documento, Tarefa, Usuario

# Logger para este módulo
logger = logging.getLogger(__name__)

bp = Blueprint('documento', __name__, url_prefix='/api/documento')

# Blueprint adicional para rotas de API de documentos (plural)
bp_api = Blueprint('documentos_api', __name__, url_prefix='/api/documentos')


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/lista', methods=['GET'])
@login_required
def listar_documentos():
    """
    Lista documentos com filtros opcionais

    Query params:
        - status: Filtrar por status
        - tipo: Filtrar por tipo de documento
        - setor: Filtrar por setor
        - page: Página (paginação)
        - per_page: Itens por página
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Documento.query

    # Filtros
    if not current_user.is_admin():
        # Usuários comuns veem apenas seus documentos
        if current_user.perfil == 'comum':
            query = query.filter_by(criador_id=current_user.id)
        # Gerentes veem documentos do seu setor
        elif current_user.setor:
            query = query.filter_by(setor=current_user.setor)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    setor = request.args.get('setor')
    if setor:
        query = query.filter_by(setor=setor)

    # Ordenação
    query = query.order_by(Documento.data_criacao.desc())

    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documentos = pagination.items

    return jsonify({
        'documentos': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'tipo_documento': doc.tipo_documento,
            'codigo_provisorio': doc.codigo_provisorio,
            'codigo_definitivo': doc.codigo_definitivo,
            'status': doc.status,
            'data_criacao': doc.data_criacao.isoformat() if doc.data_criacao else None,
            'data_publicacao': doc.data_publicacao.isoformat() if doc.data_publicacao else None,
            'criador': doc.criador.nome if doc.criador else None,
            'esta_vencido': doc.esta_vencido(),
            'dias_ate_vencimento': doc.dias_ate_vencimento()
        } for doc in documentos],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@login_required
def visualizar_documento(id):
    """
    Visualiza detalhes do documento e timeline de tarefas

    Returns:
        JSON com informações completas do documento e histórico
    """
    documento = Documento.query.get_or_404(id)

    # Verifica permissão de visualização
    if not current_user.is_admin() and not current_user.is_gerente_ou_superior():
        if documento.criador_id != current_user.id:
            return jsonify({'erro': 'Sem permissão para visualizar este documento'}), 403

    # Timeline de tarefas
    tarefas = Tarefa.query.filter_by(documento_id=id).order_by(Tarefa.data_criacao.desc()).all()

    timeline = []
    for tarefa in tarefas:
        timeline.append({
            'id': tarefa.id,
            'tipo': tarefa.tipo_tarefa,
            'criador': tarefa.criador.nome,
            'responsavel': tarefa.responsavel.nome,
            'data_criacao': tarefa.data_criacao.isoformat(),
            'data_conclusao': tarefa.data_conclusao.isoformat() if tarefa.data_conclusao else None,
            'concluida': tarefa.concluida,
            'parecer': tarefa.parecer,
            'aprovado': tarefa.aprovado,
            'esta_atrasada': tarefa.esta_atrasada()
        })

    return jsonify({
        'documento': {
            'id': documento.id,
            'titulo': documento.titulo,
            'tipo_documento': documento.tipo_documento,
            'descricao': documento.descricao,
            'setor': documento.setor,
            'codigo_provisorio': documento.codigo_provisorio,
            'codigo_definitivo': documento.codigo_definitivo,
            'status': documento.status,
            'versao': documento.versao,
            'data_criacao': documento.data_criacao.isoformat(),
            'data_publicacao': documento.data_publicacao.isoformat() if documento.data_publicacao else None,
            'data_vencimento': documento.data_vencimento.isoformat() if documento.data_vencimento else None,
            'validade_anos': documento.validade_anos,
            'criador': documento.criador.nome,
            'arquivo_original': documento.arquivo_original,
            'arquivo_publicado': documento.arquivo_publicado_pdf,
            'metadados': documento.get_metadados(),
            'esta_vencido': documento.esta_vencido(),
            'dias_ate_vencimento': documento.dias_ate_vencimento()
        },
        'timeline': timeline
    })


@bp.route('/criar', methods=['POST'])
@login_required
def criar_documento():
    """
    Cria novo documento

    Form data:
        - titulo: Título do documento
        - tipo_documento: POP, Manual ou Protocolo
        - descricao: Descrição (opcional)
        - setor: Setor responsável
        - arquivo: Arquivo do documento (.doc, .odt)
        - validade_anos: Anos de validade (padrão: 5)
    """
    # Validação
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Arquivo não enviado'}), 400

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400

    if not allowed_file(arquivo.filename):
        return jsonify({'erro': 'Tipo de arquivo não permitido'}), 400

    titulo = request.form.get('titulo')
    tipo_documento = request.form.get('tipo_documento')
    descricao = request.form.get('descricao', '')
    setor = request.form.get('setor') or current_user.setor
    # VALIDADE: Calculada automaticamente baseado no tipo (2 ou 4 anos)

    if not titulo or not tipo_documento:
        return jsonify({'erro': 'Título e tipo de documento são obrigatórios'}), 400

    if tipo_documento not in current_app.config['TIPOS_DOCUMENTO']:
        return jsonify({'erro': 'Tipo de documento inválido'}), 400

    # Salva arquivo
    filename = secure_filename(arquivo.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    nome_arquivo = f"{timestamp}_{filename}"
    caminho_arquivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
    arquivo.save(caminho_arquivo)

    # Cria documento
    # VALIDADE: Será calculada automaticamente na publicação
    documento = Documento(
        titulo=titulo,
        tipo_documento=tipo_documento,
        descricao=descricao,
        setor=setor,
        arquivo_original=nome_arquivo,
        criador_id=current_user.id,
        status='Novo'
    )

    db.session.add(documento)
    db.session.commit()

    return jsonify({
        'mensagem': 'Documento criado com sucesso',
        'documento': {
            'id': documento.id,
            'codigo_provisorio': documento.codigo_provisorio,
            'titulo': documento.titulo,
            'status': documento.status
        }
    }), 201


@bp.route('/<int:id>', methods=['PUT'])
@login_required
def atualizar_documento(id):
    """
    Atualiza informações do documento

    JSON body:
        - titulo
        - descricao
        - setor
        - tipo_documento
        - versao_anterior_id (apenas para triadores/validadores)
    """
    from config import Config

    documento = Documento.query.get_or_404(id)

    # Verifica permissão
    if not documento.pode_editar(current_user):
        return jsonify({'erro': 'Sem permissão para editar este documento'}), 403

    data = request.get_json()

    if 'titulo' in data:
        documento.titulo = data['titulo']
    if 'descricao' in data:
        documento.descricao = data['descricao']
    if 'setor' in data:
        documento.setor = data['setor']
    if 'tipo_documento' in data and data['tipo_documento'] in current_app.config['TIPOS_DOCUMENTO']:
        documento.tipo_documento = data['tipo_documento']

    # Marcar como nova versão (apenas triador/validador)
    if 'versao_anterior_id' in data:
        if not (current_user.is_triador_ugq() or current_user.is_validador_ugq()):
            return jsonify({'erro': 'Apenas Triador ou Validador UGQ podem marcar versões'}), 403

        doc_anterior_id = data['versao_anterior_id']
        doc_anterior = Documento.query.get(doc_anterior_id)

        if not doc_anterior:
            return jsonify({'erro': 'Documento anterior não encontrado'}), 404

        if doc_anterior.status != Config.STATUS_PUBLICADO:
            return jsonify({'erro': 'Documento anterior precisa estar Publicado'}), 400

        documento.versao_anterior_id = doc_anterior_id

        # Incrementa a versão baseada na anterior
        if doc_anterior.versao:
            try:
                # Extrai número da versão (ex: v1.0 -> 1.0)
                versao_str = doc_anterior.versao.replace('v', '').replace('V', '')
                partes = versao_str.split('.')
                if len(partes) >= 1:
                    major = int(partes[0])
                    documento.versao = f'v{major + 1}.0'
            except:
                documento.versao = 'v2.0'

    db.session.commit()

    return jsonify({'mensagem': 'Documento atualizado com sucesso'})


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def deletar_documento(id):
    """
    Remove documento (apenas se status = Novo ou Cancelado)
    """
    documento = Documento.query.get_or_404(id)

    # Apenas admin ou criador podem deletar
    if not current_user.is_admin() and documento.criador_id != current_user.id:
        return jsonify({'erro': 'Sem permissão para deletar este documento'}), 403

    # Apenas documentos Novo ou Cancelado podem ser deletados
    if documento.status not in ['Novo', 'Cancelado']:
        return jsonify({'erro': 'Apenas documentos "Novo" ou "Cancelado" podem ser deletados'}), 400

    # Remove arquivo físico
    if documento.arquivo_original:
        caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.arquivo_original)
        if os.path.exists(caminho):
            os.remove(caminho)

    if documento.arquivo_publicado_pdf:
        caminho = os.path.join(current_app.config['PUBLISHED_FOLDER'], documento.arquivo_publicado_pdf)
        if os.path.exists(caminho):
            os.remove(caminho)

    db.session.delete(documento)
    db.session.commit()

    return jsonify({'mensagem': 'Documento deletado com sucesso'})


@bp.route('/<int:id>/download/<tipo>', methods=['GET'])
@login_required
def download_arquivo(id, tipo):
    """
    Download do arquivo do documento

    Args:
        tipo: 'original' ou 'publicado'
    """
    documento = Documento.query.get_or_404(id)

    if tipo == 'original':
        if not documento.arquivo_original:
            return jsonify({'erro': 'Arquivo original não encontrado'}), 404
        caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.arquivo_original)
        nome_download = documento.arquivo_original
    elif tipo == 'publicado':
        if not documento.arquivo_publicado_pdf:
            return jsonify({'erro': 'Arquivo publicado não encontrado'}), 404
        caminho = os.path.join(current_app.config['PUBLISHED_FOLDER'], documento.arquivo_publicado_pdf)
        nome_download = documento.arquivo_publicado_pdf
    else:
        return jsonify({'erro': 'Tipo de arquivo inválido'}), 400

    if not os.path.exists(caminho):
        return jsonify({'erro': 'Arquivo não encontrado no servidor'}), 404

    return send_file(caminho, as_attachment=True, download_name=nome_download)


@bp.route('/<int:id>/substituir_arquivo', methods=['POST'])
@login_required
def substituir_arquivo(id):
    """
    Substitui o arquivo de um documento (apenas Triador UGQ ou Validador UGQ)

    Permite que triadores e validadores alterem o arquivo durante o processo de análise
    sem precisar criar uma nova versão do documento.

    Form data:
        - arquivo: Novo arquivo do documento (.doc, .docx, .odt, .pdf)
        - motivo: Motivo da substituição (opcional)

    Permissões:
        - Triador UGQ: pode alterar durante triagem
        - Validador UGQ: pode alterar durante validação

    Returns:
        JSON com mensagem de sucesso e informações do novo arquivo
    """
    from config import Config
    import logging

    logger = logging.getLogger(__name__)
    documento = Documento.query.get_or_404(id)

    # Verifica permissão: apenas Triador UGQ ou Validador UGQ
    if not (current_user.is_triador_ugq() or current_user.is_validador_ugq()):
        return jsonify({'erro': 'Apenas Triador UGQ ou Validador UGQ podem substituir arquivos'}), 403

    # Verifica se o documento está em status permitido para edição
    status_permitidos = [
        Config.STATUS_NOVO,
        Config.STATUS_EM_TRIAGEM,
        Config.STATUS_EM_VALIDACAO,
        Config.STATUS_EM_CORRECAO
    ]

    if documento.status not in status_permitidos:
        return jsonify({
            'erro': f'Documento no status "{documento.status}" não pode ter o arquivo substituído. Status permitidos: {", ".join(status_permitidos)}'
        }), 400

    # Verifica se foi enviado um arquivo
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo foi enviado'}), 400

    arquivo = request.files['arquivo']

    if arquivo.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400

    # Valida extensão do arquivo
    if not allowed_file(arquivo.filename):
        extensoes_permitidas = ', '.join(current_app.config['ALLOWED_EXTENSIONS'])
        return jsonify({
            'erro': f'Tipo de arquivo não permitido. Extensões aceitas: {extensoes_permitidas}'
        }), 400

    motivo = request.form.get('motivo', 'Arquivo substituído pelo validador/triador')

    try:
        # Salva o arquivo antigo como backup (opcional)
        arquivo_antigo = documento.arquivo_original

        # Salva o novo arquivo
        filename = secure_filename(arquivo.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"{timestamp}_{filename}"
        caminho_arquivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)

        # Garante que o diretório existe
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Salva o novo arquivo
        arquivo.save(caminho_arquivo)

        # Atualiza o documento
        documento.arquivo_original = nome_arquivo

        # Registra a alteração em um log ou observação
        if hasattr(documento, 'observacoes'):
            observacao_atual = documento.observacoes or ''
            nova_observacao = f"{observacao_atual}\n[{datetime.utcnow().strftime('%d/%m/%Y %H:%M')}] Arquivo substituído por {current_user.nome}. Motivo: {motivo}"
            documento.observacoes = nova_observacao

        db.session.commit()

        logger.info(f"Arquivo do documento {documento.id} substituído por {current_user.nome}")

        # Envia notificação para o autor original (se houver)
        if documento.criador and documento.criador_id != current_user.id:
            from app.models import Notificacao
            notificacao = Notificacao(
                usuario_id=documento.criador_id,
                documento_id=documento.id,
                tipo='atualizacao',
                titulo='Arquivo do Documento Substituído',
                mensagem=f'O arquivo do documento "{documento.titulo}" foi substituído por {current_user.nome}. Motivo: {motivo}'
            )
            db.session.add(notificacao)
            db.session.commit()

            # Envia e-mail
            try:
                from app.services.email_service import EmailService
                EmailService.enviar_notificacao_tarefa(
                    usuario_id=documento.criador_id,
                    tipo_tarefa='Atualização de Documento',
                    documento_titulo=documento.titulo,
                    documento_codigo=documento.codigo_provisorio or documento.codigo_unico
                )
            except Exception as e:
                logger.warning(f"Erro ao enviar e-mail: {str(e)}")

        return jsonify({
            'mensagem': 'Arquivo substituído com sucesso',
            'arquivo_anterior': arquivo_antigo,
            'arquivo_novo': nome_arquivo,
            'substituido_por': current_user.nome,
            'data_substituicao': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao substituir arquivo: {str(e)}")
        return jsonify({'erro': f'Erro ao substituir arquivo: {str(e)}'}), 500


@bp.route('/hierarquia', methods=['GET'])
def get_hierarquia():
    """
    Retorna estrutura hierárquica de setores e tipos com contadores
    Usado para popular a sidebar de navegação

    Returns:
        JSON com estrutura: {"Setor (ABRANG)": {total: X, tipos: {tipo: count}, abrangencia: "ABRANG"}}
    """
    # Consulta otimizada com GROUP BY incluindo abrangência
    query_result = db.session.query(
        Documento.setor,
        Documento.abrangencia,
        Documento.tipo_documento,
        db.func.count(Documento.id).label('count')
    ).filter(
        Documento.status == 'Publicado'
    ).group_by(
        Documento.setor,
        Documento.abrangencia,
        Documento.tipo_documento
    ).all()

    # Organiza em estrutura hierárquica com abrangência
    hierarquia = {}
    total_geral = 0

    for setor, abrangencia, tipo, count in query_result:
        setor_nome = setor or 'Sem Setor'
        abrang = abrangencia or 'CHUFC'  # Default CHUFC se não definido

        # Chave única: "Setor (ABRANG)" para setores com mesmo nome em abrangências diferentes
        chave = f"{setor_nome} ({abrang})"

        if chave not in hierarquia:
            hierarquia[chave] = {
                'total': 0,
                'tipos': {},
                'abrangencia': abrang,
                'setor_original': setor_nome
            }

        hierarquia[chave]['tipos'][tipo] = count
        hierarquia[chave]['total'] += count
        total_geral += count

    # Ordena setores por nome (alfabético) e depois por abrangência
    hierarquia_ordenada = dict(sorted(
        hierarquia.items(),
        key=lambda x: (x[1]['setor_original'], x[1]['abrangencia'])
    ))

    return jsonify({
        'hierarquia': hierarquia_ordenada,
        'total_geral': total_geral
    })


@bp.route('/publico', methods=['GET'])
def repositorio_publico():
    """
    Repositório público de documentos publicados e válidos
    Acesso livre (sem autenticação)

    Query params:
        - q: Busca por título
        - tipo: Filtro por tipo de documento
        - setor: Filtro por setor
        - palavras_chave: Busca por palavras-chave da IA
        - page: Página
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)  # Aumentado para 30 (lazy loading)

    # FIX: Corrigido status para 'Publicado' (Config.STATUS_PUBLICADO)
    query = Documento.query.filter_by(status='Publicado')

    # Apenas documentos válidos (não vencidos)
    query = query.filter(
        (Documento.data_vencimento == None) | (Documento.data_vencimento > datetime.utcnow())
    )

    # Filtros
    q = request.args.get('q')
    if q:
        # Busca expandida: título, código ou texto extraído
        query = query.filter(
            db.or_(
                Documento.titulo.ilike(f'%{q}%'),
                Documento.codigo_definitivo.ilike(f'%{q}%'),
                Documento.codigo_provisorio.ilike(f'%{q}%'),
                Documento.texto_extraido.ilike(f'%{q}%')
            )
        )

    # Busca por palavras-chave extraídas pela IA
    palavras_chave = request.args.get('palavras_chave')
    if palavras_chave:
        query = query.filter(Documento.metadados_json.ilike(f'%{palavras_chave}%'))

    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    setor = request.args.get('setor')
    if setor:
        query = query.filter_by(setor=setor)

    # Filtro por abrangência
    abrangencia = request.args.get('abrangencia')
    if abrangencia:
        query = query.filter_by(abrangencia=abrangencia)

    # Ordenação: agrupa por setor e tipo, depois por data
    order_by = request.args.get('order_by', 'setor_tipo')
    if order_by == 'data':
        query = query.order_by(Documento.data_publicacao.desc())
    elif order_by == 'setor_tipo':
        # Organiza por Setor > Tipo > Data
        query = query.order_by(
            Documento.setor.asc(),
            Documento.tipo_documento.asc(),
            Documento.data_publicacao.desc()
        )
    elif order_by == 'tipo_setor':
        # Organiza por Tipo > Setor > Data
        query = query.order_by(
            Documento.tipo_documento.asc(),
            Documento.setor.asc(),
            Documento.data_publicacao.desc()
        )

    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documentos = pagination.items

    # Extrai metadados para exibição
    import json

    def parse_metadados(doc):
        """Extrai metadados do documento"""
        try:
            metadados = json.loads(doc.metadados_json) if doc.metadados_json else {}
            resumo_obj = metadados.get('resumo', {})

            # O resumo pode ser um objeto ou string
            if isinstance(resumo_obj, dict):
                resumo_texto = resumo_obj.get('resumo', '')
                palavras_chave = resumo_obj.get('palavras_chave', [])
                topicos_principais = resumo_obj.get('topicos_principais', [])
            else:
                resumo_texto = resumo_obj if isinstance(resumo_obj, str) else ''
                palavras_chave = metadados.get('palavras_chave', [])
                topicos_principais = metadados.get('topicos_principais', [])

            # Remove pareceres vazios tipo "ok", "aprovado", etc
            import re
            if resumo_texto:
                resumo_texto = re.sub(r'\b(ok|aprovado|certo)\b\s*', '', resumo_texto, flags=re.IGNORECASE).strip()

            return {
                'palavras_chave': palavras_chave,
                'resumo': resumo_texto,
                'topicos_principais': topicos_principais
            }
        except Exception as e:
            return {'palavras_chave': [], 'resumo': '', 'topicos_principais': []}

    # Estatísticas do repositório (para organização visual)
    stats_por_setor = db.session.query(
        Documento.setor, db.func.count(Documento.id)
    ).filter_by(status='Publicado').group_by(Documento.setor).all()

    stats_por_tipo = db.session.query(
        Documento.tipo_documento, db.func.count(Documento.id)
    ).filter_by(status='Publicado').group_by(Documento.tipo_documento).all()

    return jsonify({
        'documentos': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'titulo_completo': doc.titulo_completo,
            'tipo_documento': doc.tipo_documento,
            'codigo_definitivo': doc.codigo_definitivo,
            'codigo': doc.codigo_provisorio or doc.codigo_unico,
            'setor': doc.setor,
            'abrangencia': doc.abrangencia or 'CHUFC',
            'data_publicacao': doc.data_publicacao.isoformat(),
            'data_vencimento': doc.data_vencimento.isoformat() if doc.data_vencimento else None,
            'versao': doc.versao,
            'metadados': parse_metadados(doc)
        } for doc in documentos],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'stats': {
            'por_setor': {setor: count for setor, count in stats_por_setor},
            'por_tipo': {tipo: count for tipo, count in stats_por_tipo}
        }
    })


@bp.route('/<int:id>/mudar_status', methods=['POST'])
@login_required
def mudar_status(id):
    """
    Muda status do documento

    JSON body:
        - novo_status: Novo status do documento
        - motivo: Justificativa da mudança
    """
    documento = Documento.query.get_or_404(id)

    # Apenas gerentes ou superior podem mudar status
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para alterar status'}), 403

    data = request.get_json()
    novo_status = data.get('novo_status')
    motivo = data.get('motivo', '')

    if not novo_status:
        return jsonify({'erro': 'Novo status não informado'}), 400

    documento.status = novo_status
    db.session.commit()

    return jsonify({
        'mensagem': 'Status alterado com sucesso',
        'novo_status': novo_status
    })


@bp.route('/<int:id>/nova_versao', methods=['POST'])
@login_required
def criar_nova_versao(id):
    """
    Cria nova versão de um documento (triador/validador pode alterar e criar nova versão)

    Usado quando:
    - Documento já está publicado e precisa ser revisado
    - Triador/Validador quer fazer alterações que geram nova versão

    Form data:
        - arquivo: Novo arquivo do documento (opcional, se não enviar mantém o anterior)
        - motivo: Motivo da revisão
        - alteracoes: Descrição das alterações

    Returns:
        - Novo documento criado (versão incrementada)
        - Documento anterior marcado como Obsoleto
    """
    from app.models import ListaMestra, Notificacao
    from config import Config
    import shutil

    documento_original = Documento.query.get_or_404(id)

    # Verifica permissão: Triador UGQ ou Validador UGQ
    if not (current_user.is_triador_ugq() or current_user.is_validador_ugq()):
        return jsonify({'erro': 'Apenas Triador UGQ ou Validador UGQ podem criar nova versão'}), 403

    # Extrai dados do formulário
    motivo = request.form.get('motivo', 'Revisão do documento')
    alteracoes = request.form.get('alteracoes', '')
    arquivo_novo = request.files.get('arquivo')

    # Incrementa versão
    versao_atual = documento_original.versao or 'v1.0'
    try:
        major, minor = versao_atual.replace('v', '').split('.')
        nova_versao = f"v{int(major)}.{int(minor) + 1}"
    except:
        nova_versao = 'v2.0'

    # Cria novo documento (nova versão)
    novo_documento = Documento(
        titulo=request.form.get('titulo', documento_original.titulo),
        tipo_documento=request.form.get('tipo_documento', documento_original.tipo_documento),
        setor=request.form.get('setor', documento_original.setor),
        descricao=request.form.get('descricao', documento_original.descricao),
        versao=nova_versao,
        versao_anterior_id=documento_original.id,
        criador_id=current_user.id,
        chefia_imediata_id=documento_original.chefia_imediata_id,
        validade_anos=documento_original.validade_anos,
        status=Config.STATUS_NOVO  # Inicia como Novo, vai passar pelo workflow novamente
    )

    # Se enviou arquivo novo, usa ele. Senão, copia o arquivo anterior
    if arquivo_novo and arquivo_novo.filename != '':
        # Validar extensão
        extensao = arquivo_novo.filename.rsplit('.', 1)[1].lower()
        if extensao not in Config.ALLOWED_EXTENSIONS_DOCUMENTO:
            return jsonify({'erro': f'Extensão .{extensao} não permitida'}), 400

        # Salvar novo arquivo
        filename = secure_filename(arquivo_novo.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename_final = f"{timestamp}_{filename}"
        caminho_completo = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, filename_final)

        os.makedirs(Config.UPLOAD_FOLDER_DOCUMENTOS, exist_ok=True)
        arquivo_novo.save(caminho_completo)

        novo_documento.arquivo_original = filename_final
    else:
        # Copia arquivo anterior
        if documento_original.arquivo_original:
            arquivo_original_path = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, documento_original.arquivo_original)
            if os.path.exists(arquivo_original_path):
                novo_nome = f"v{nova_versao}_{documento_original.arquivo_original}"
                novo_caminho = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, novo_nome)
                shutil.copy2(arquivo_original_path, novo_caminho)
                novo_documento.arquivo_original = novo_nome

    # Mantém código definitivo (mesmo POP.SETOR-XXX, só muda a versão)
    if documento_original.codigo_definitivo:
        novo_documento.codigo_definitivo = documento_original.codigo_definitivo

    db.session.add(novo_documento)

    # Marca documento anterior como Obsoleto
    documento_original.status = Config.STATUS_OBSOLETO

    # Atualiza Lista Mestra
    lista_mestra_antiga = ListaMestra.query.filter_by(documento_id=documento_original.id).first()
    if lista_mestra_antiga:
        lista_mestra_antiga.status = 'OBSOLETO'

    # Cria notificação para o autor original
    notificacao = Notificacao(
        usuario_id=documento_original.criador_id,
        documento_id=novo_documento.id,
        tipo='revisao',
        titulo='Nova Versão do Seu Documento',
        mensagem=f'Uma nova versão ({nova_versao}) do documento "{documento_original.titulo}" foi criada por {current_user.nome}. Motivo: {motivo}'
    )
    db.session.add(notificacao)

    # NOVO: Cria tarefa para Triador UGQ automaticamente
    from app.services.workflow import WorkflowUGQ
    try:
        WorkflowUGQ.autor_submete_documento(novo_documento)
    except Exception as e:
        # Se falhar, pelo menos salva o documento
        pass

    db.session.commit()

    # Envia e-mail para o autor original
    try:
        from app.services.email_service import EmailService
        EmailService.enviar_notificacao_nova_versao(
            usuario_id=documento_original.criador_id,
            documento_titulo=documento_original.titulo,
            codigo_original=documento_original.codigo_definitivo or documento_original.codigo_unico,
            nova_versao=nova_versao,
            motivo=motivo,
            criador_nome=current_user.nome
        )
    except Exception as e:
        # Se falhar o envio do e-mail, não interrompe o processo
        logger.warning(f"Erro ao enviar e-mail de nova versão: {str(e)}")

    return jsonify({
        'mensagem': 'Nova versão criada com sucesso!',
        'documento_novo_id': novo_documento.id,
        'versao_nova': nova_versao,
        'versao_anterior': versao_atual,
        'status': novo_documento.status
    }), 201


# ============================================================================
# ROTA DE BUSCA DE DOCUMENTOS (para Checkpoint 1)
# ============================================================================

@bp_api.route('/buscar', methods=['GET'])
@login_required
def buscar_documentos():
    """
    Busca documentos por termo (usado no Checkpoint 1 de triagem)

    Query params:
        - q: Termo de busca (título, código)
        - limit: Número máximo de resultados (padrão: 15)

    Returns:
        Lista de documentos encontrados com informações básicas
    """
    termo = request.args.get('q', '').strip()
    limit = request.args.get('limit', 15, type=int)

    if not termo or len(termo) < 3:
        return jsonify([])

    # Query base
    query = Documento.query

    # Busca por título ou código
    query = query.filter(
        or_(
            Documento.titulo.ilike(f'%{termo}%'),
            Documento.codigo_provisorio.ilike(f'%{termo}%'),
            Documento.codigo_definitivo.ilike(f'%{termo}%'),
            Documento.codigo_unico.ilike(f'%{termo}%')
        )
    )

    # Aplica filtros de permissão
    if not current_user.is_admin():
        if current_user.perfil == 'comum':
            # Usuários comuns veem apenas seus documentos
            query = query.filter_by(criador_id=current_user.id)
        elif current_user.setor and not current_user.is_triador_ugq() and not current_user.is_validador_ugq():
            # Usuários de setor veem documentos do setor ou próprios
            query = query.filter(
                or_(
                    Documento.setor == current_user.setor,
                    Documento.criador_id == current_user.id
                )
            )
        # Triadores e Validadores UGQ veem todos os documentos

    # Ordena por data de criação (mais recentes primeiro) e limita resultados
    documentos = query.order_by(Documento.data_criacao.desc()).limit(limit).all()

    # Prepara resposta
    resultados = []
    for doc in documentos:
        resultado = {
            'id': doc.id,
            'titulo': doc.titulo,
            'codigo': doc.codigo,
            'codigo_unico': doc.codigo_unico,
            'tipo_documento': doc.tipo_documento,
            'status': doc.status,
            'versao': doc.versao or 'v1.0',
            'data_criacao': doc.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'criador': doc.criador.nome if doc.criador else 'Desconhecido',
            'setor': doc.setor or 'Não definido'
        }
        resultados.append(resultado)

    return jsonify(resultados)


@bp.route('/setor/<setor_nome>/dashboard', methods=['GET'])
def get_setor_dashboard(setor_nome):
    """
    Retorna dashboard completo de um setor com estatísticas e gráficos

    Args:
        setor_nome: Nome do setor

    Returns:
        JSON com:
        - estatisticas_gerais: totais, vencidos, perto de vencer
        - documentos_por_tipo: contagem por tipo de documento
        - documentos_por_status: contagem por status
        - timeline_publicacoes: publicações nos últimos 12 meses
        - documentos_vencidos: lista de documentos vencidos
        - documentos_perto_vencer: lista próximos de vencer (90 dias)
        - documentos_recentes: últimos 10 documentos publicados
    """
    from datetime import timedelta
    import json

    # Decodifica nome do setor (URL encoded)
    from urllib.parse import unquote
    setor_nome = unquote(setor_nome)

    # Query base: documentos publicados do setor
    base_query = Documento.query.filter_by(
        setor=setor_nome,
        status='Publicado'
    )

    # ===== ESTATÍSTICAS GERAIS =====
    total_documentos = base_query.count()

    # Documentos vencidos
    documentos_vencidos = base_query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < datetime.utcnow()
    ).all()

    # Documentos perto de vencer (próximos 90 dias)
    data_limite_90dias = datetime.utcnow() + timedelta(days=90)
    documentos_perto_vencer = base_query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento >= datetime.utcnow(),
        Documento.data_vencimento <= data_limite_90dias
    ).all()

    # Documentos vigentes (não vencidos)
    documentos_vigentes = base_query.filter(
        (Documento.data_vencimento == None) |
        (Documento.data_vencimento > datetime.utcnow())
    ).count()

    # ===== DOCUMENTOS POR TIPO =====
    docs_por_tipo = db.session.query(
        Documento.tipo_documento,
        db.func.count(Documento.id).label('count')
    ).filter(
        Documento.setor == setor_nome,
        Documento.status == 'Publicado'
    ).group_by(Documento.tipo_documento).all()

    # ===== DOCUMENTOS POR STATUS (todos os status do setor) =====
    docs_por_status = db.session.query(
        Documento.status,
        db.func.count(Documento.id).label('count')
    ).filter(
        Documento.setor == setor_nome
    ).group_by(Documento.status).all()

    # ===== TIMELINE DE PUBLICAÇÕES (últimos 12 meses) =====
    data_12_meses_atras = datetime.utcnow() - timedelta(days=365)

    # Usando to_char para PostgreSQL (strftime é apenas SQLite)
    publicacoes_timeline = db.session.query(
        db.func.to_char(Documento.data_publicacao, 'YYYY-MM').label('mes'),
        db.func.count(Documento.id).label('count')
    ).filter(
        Documento.setor == setor_nome,
        Documento.status == 'Publicado',
        Documento.data_publicacao >= data_12_meses_atras
    ).group_by(db.func.to_char(Documento.data_publicacao, 'YYYY-MM')).order_by('mes').all()

    # ===== DOCUMENTOS RECENTES =====
    docs_recentes = base_query.order_by(
        Documento.data_publicacao.desc()
    ).limit(10).all()

    # ===== HELPER FUNCTION: Parse Metadados =====
    def parse_metadados(doc):
        try:
            metadados = json.loads(doc.metadados_json) if doc.metadados_json else {}
            resumo_obj = metadados.get('resumo', {})

            if isinstance(resumo_obj, dict):
                resumo_texto = resumo_obj.get('resumo', '')
                palavras_chave = resumo_obj.get('palavras_chave', [])
            else:
                resumo_texto = resumo_obj if isinstance(resumo_obj, str) else ''
                palavras_chave = metadados.get('palavras_chave', [])

            return {
                'palavras_chave': palavras_chave,
                'resumo': resumo_texto[:200] + '...' if len(resumo_texto) > 200 else resumo_texto
            }
        except:
            return {'palavras_chave': [], 'resumo': ''}

    # ===== MONTA RESPOSTA =====
    return jsonify({
        'setor': setor_nome,
        'estatisticas_gerais': {
            'total_documentos': total_documentos,
            'documentos_vencidos': len(documentos_vencidos),
            'documentos_perto_vencer': len(documentos_perto_vencer),
            'documentos_vigentes': documentos_vigentes
        },
        'documentos_por_tipo': {
            tipo: count for tipo, count in docs_por_tipo
        },
        'documentos_por_status': {
            status: count for status, count in docs_por_status
        },
        'timeline_publicacoes': [
            {'mes': mes, 'count': count} for mes, count in publicacoes_timeline
        ],
        'documentos_vencidos': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'tipo_documento': doc.tipo_documento,
            'codigo': doc.codigo_definitivo or doc.codigo_provisorio or doc.codigo_unico,
            'data_vencimento': doc.data_vencimento.isoformat(),
            'dias_vencido': (datetime.utcnow() - doc.data_vencimento).days,
            'versao': doc.versao,
            'metadados': parse_metadados(doc)
        } for doc in documentos_vencidos],
        'documentos_perto_vencer': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'tipo_documento': doc.tipo_documento,
            'codigo': doc.codigo_definitivo or doc.codigo_provisorio or doc.codigo_unico,
            'data_vencimento': doc.data_vencimento.isoformat(),
            'dias_ate_vencimento': doc.dias_ate_vencimento(),
            'versao': doc.versao,
            'metadados': parse_metadados(doc)
        } for doc in documentos_perto_vencer],
        'documentos_recentes': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'tipo_documento': doc.tipo_documento,
            'codigo': doc.codigo_definitivo or doc.codigo_provisorio or doc.codigo_unico,
            'data_publicacao': doc.data_publicacao.isoformat(),
            'versao': doc.versao,
            'metadados': parse_metadados(doc)
        } for doc in docs_recentes]
    })
