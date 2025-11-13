"""
Rotas de Integração com IA do Sistema GED

Endpoints:
- POST /ia/extract/<id> - Extrai texto de documento
- POST /ia/classify/<id> - Classifica documento
- POST /ia/summarize/<id> - Gera resumo
- POST /ia/search - Busca semântica
- POST /ia/suggest_responsavel - Sugere responsável para tarefa

Todas as chamadas são registradas em LogAI para auditoria.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import time

from app.models import db, Documento, LogAI, Usuario
from app.services import (
    extract_text,
    classify_document,
    summarize_text,
    search_semantic,
    suggest_responsavel
)
from app.services.ai_client import AIClientError

bp = Blueprint('ia', __name__, url_prefix='/ia')


def registrar_log_ia(documento_id, funcao, parametros, resposta, sucesso=True, erro=None, tempo_ms=0):
    """
    Registra chamada à IA no banco de dados para auditoria

    Args:
        documento_id: ID do documento
        funcao: Nome da função de IA chamada
        parametros: Dicionário com parâmetros enviados
        resposta: Dicionário com resposta recebida
        sucesso: Se a chamada foi bem-sucedida
        erro: Mensagem de erro (se houver)
        tempo_ms: Tempo de resposta em milissegundos
    """
    import json

    log = LogAI(
        documento_id=documento_id,
        usuario_id=current_user.id,
        funcao_ia=funcao,
        parametros_json=json.dumps(parametros, ensure_ascii=False),
        resposta_json=json.dumps(resposta, ensure_ascii=False) if resposta else None,
        sucesso=sucesso,
        mensagem_erro=erro,
        tempo_resposta_ms=tempo_ms
    )

    db.session.add(log)
    db.session.commit()


def verificar_permissao_ia():
    """Verifica se o usuário pode usar funções de IA"""
    if not current_user.pode_usar_ia():
        return jsonify({'erro': 'Apenas Gerentes e Administradores podem usar funções de IA'}), 403
    return None


@bp.route('/extract/<int:id>', methods=['POST'])
@login_required
def extrair_texto(id):
    """
    Extrai texto de um documento usando IA

    Atualiza os campos texto_extraido e metadados_json do documento.

    Returns:
        JSON com texto extraído e metadados
    """
    # Verifica permissão
    erro_permissao = verificar_permissao_ia()
    if erro_permissao:
        return erro_permissao

    documento = Documento.query.get_or_404(id)

    if not documento.arquivo_original:
        return jsonify({'erro': 'Documento não possui arquivo original'}), 400

    # Caminho do arquivo
    caminho_arquivo = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        documento.arquivo_original
    )

    if not os.path.exists(caminho_arquivo):
        return jsonify({'erro': 'Arquivo não encontrado no servidor'}), 404

    try:
        start_time = time.time()

        # Chama API de IA
        resultado = extract_text(caminho_arquivo)

        tempo_ms = resultado.get('_tempo_resposta_ms', 0)

        # Atualiza documento
        documento.texto_extraido = resultado.get('texto', '')
        documento.set_metadados(resultado.get('metadados', {}))

        db.session.commit()

        # Registra log
        registrar_log_ia(
            documento_id=id,
            funcao='extract_text',
            parametros={'arquivo': documento.arquivo_original},
            resposta=resultado,
            sucesso=True,
            tempo_ms=tempo_ms
        )

        return jsonify({
            'mensagem': 'Texto extraído com sucesso',
            'texto': resultado.get('texto', ''),
            'entidades': resultado.get('entidades', {}),
            'metadados': resultado.get('metadados', {}),
            'tempo_ms': tempo_ms
        })

    except AIClientError as e:
        # Registra erro
        registrar_log_ia(
            documento_id=id,
            funcao='extract_text',
            parametros={'arquivo': documento.arquivo_original},
            resposta=None,
            sucesso=False,
            erro=str(e)
        )

        return jsonify({'erro': str(e)}), 500

    except Exception as e:
        current_app.logger.error(f"Erro ao extrair texto: {str(e)}")
        return jsonify({'erro': 'Erro interno ao processar documento'}), 500


@bp.route('/classify/<int:id>', methods=['POST'])
@login_required
def classificar_documento(id):
    """
    Classifica tipo de documento usando IA

    Atualiza o campo tipo_documento se ainda não estiver definido.

    Returns:
        JSON com tipo classificado e confiança
    """
    # Verifica permissão
    erro_permissao = verificar_permissao_ia()
    if erro_permissao:
        return erro_permissao

    documento = Documento.query.get_or_404(id)

    if not documento.texto_extraido:
        return jsonify({'erro': 'Documento não possui texto extraído. Execute /extract primeiro'}), 400

    try:
        # Chama API de IA
        resultado = classify_document(documento.texto_extraido)

        tempo_ms = resultado.get('_tempo_resposta_ms', 0)
        tipo_sugerido = resultado.get('tipo_documento')
        confianca = resultado.get('confianca', 0)

        # Atualiza documento se confiança for alta e tipo não definido
        atualizado = False
        if confianca >= 0.8 and not documento.tipo_documento:
            documento.tipo_documento = tipo_sugerido
            db.session.commit()
            atualizado = True

        # Registra log
        registrar_log_ia(
            documento_id=id,
            funcao='classify_document',
            parametros={'tamanho_texto': len(documento.texto_extraido)},
            resposta=resultado,
            sucesso=True,
            tempo_ms=tempo_ms
        )

        return jsonify({
            'mensagem': 'Documento classificado com sucesso',
            'tipo_documento': tipo_sugerido,
            'confianca': confianca,
            'caracteristicas': resultado.get('caracteristicas', []),
            'atualizado': atualizado,
            'tempo_ms': tempo_ms
        })

    except AIClientError as e:
        registrar_log_ia(
            documento_id=id,
            funcao='classify_document',
            parametros={},
            resposta=None,
            sucesso=False,
            erro=str(e)
        )
        return jsonify({'erro': str(e)}), 500


@bp.route('/summarize/<int:id>', methods=['POST'])
@login_required
def resumir_documento(id):
    """
    Gera resumo do documento usando IA

    Query params:
        - max_length: Tamanho máximo do resumo (padrão: 500)

    Returns:
        JSON com resumo, palavras-chave e tópicos principais
    """
    # Verifica permissão
    erro_permissao = verificar_permissao_ia()
    if erro_permissao:
        return erro_permissao

    documento = Documento.query.get_or_404(id)

    if not documento.texto_extraido:
        return jsonify({'erro': 'Documento não possui texto extraído. Execute /extract primeiro'}), 400

    max_length = request.args.get('max_length', 500, type=int)

    try:
        # Chama API de IA
        resultado = summarize_text(documento.texto_extraido, max_length=max_length)

        tempo_ms = resultado.get('_tempo_resposta_ms', 0)

        # Atualiza metadados do documento
        metadados = documento.get_metadados()
        metadados['resumo'] = resultado.get('resumo', '')
        metadados['palavras_chave'] = resultado.get('palavras_chave', [])
        metadados['topicos_principais'] = resultado.get('topicos_principais', [])
        documento.set_metadados(metadados)

        db.session.commit()

        # Registra log
        registrar_log_ia(
            documento_id=id,
            funcao='summarize_text',
            parametros={'max_length': max_length},
            resposta=resultado,
            sucesso=True,
            tempo_ms=tempo_ms
        )

        return jsonify({
            'mensagem': 'Resumo gerado com sucesso',
            'resumo': resultado.get('resumo', ''),
            'palavras_chave': resultado.get('palavras_chave', []),
            'topicos_principais': resultado.get('topicos_principais', []),
            'tempo_ms': tempo_ms
        })

    except AIClientError as e:
        registrar_log_ia(
            documento_id=id,
            funcao='summarize_text',
            parametros={'max_length': max_length},
            resposta=None,
            sucesso=False,
            erro=str(e)
        )
        return jsonify({'erro': str(e)}), 500


@bp.route('/search', methods=['POST'])
@login_required
def busca_semantica():
    """
    Busca semântica de documentos

    JSON body:
        - query: Consulta em linguagem natural
        - limit: Número máximo de resultados (padrão: 10)
        - filters: Filtros adicionais (tipo, setor, etc)

    Returns:
        JSON com resultados da busca semântica
    """
    # Verifica permissão
    erro_permissao = verificar_permissao_ia()
    if erro_permissao:
        return erro_permissao

    data = request.get_json()
    query = data.get('query')
    limit = data.get('limit', 10)
    filters = data.get('filters', {})

    if not query:
        return jsonify({'erro': 'Campo "query" é obrigatório'}), 400

    try:
        # Chama API de IA
        resultado = search_semantic(query, limit=limit, filters=filters)

        tempo_ms = resultado.get('_tempo_resposta_ms', 0)

        # Registra log (sem documento específico, usa None)
        log = LogAI(
            documento_id=None,
            usuario_id=current_user.id,
            funcao_ia='search_semantic',
            parametros_json=str({'query': query, 'limit': limit, 'filters': filters}),
            resposta_json=str(resultado),
            sucesso=True,
            tempo_resposta_ms=tempo_ms
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'mensagem': 'Busca realizada com sucesso',
            'resultados': resultado.get('resultados', []),
            'total': resultado.get('total', 0),
            'tempo_ms': tempo_ms
        })

    except AIClientError as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('/suggest_responsavel', methods=['POST'])
@login_required
def sugerir_responsavel():
    """
    Sugere responsável ideal para tarefa baseado em histórico

    JSON body:
        - tipo_documento: Tipo do documento
        - setor: Setor relacionado
        - descricao: Descrição da tarefa (opcional)

    Returns:
        JSON com responsável sugerido e alternativas
    """
    # Verifica permissão
    erro_permissao = verificar_permissao_ia()
    if erro_permissao:
        return erro_permissao

    data = request.get_json()
    tipo_documento = data.get('tipo_documento')
    setor = data.get('setor')
    descricao = data.get('descricao')

    if not tipo_documento or not setor:
        return jsonify({'erro': 'Campos "tipo_documento" e "setor" são obrigatórios'}), 400

    try:
        # Chama API de IA
        resultado = suggest_responsavel(tipo_documento, setor, descricao)

        tempo_ms = resultado.get('_tempo_resposta_ms', 0)

        # Registra log
        log = LogAI(
            documento_id=None,
            usuario_id=current_user.id,
            funcao_ia='suggest_responsavel',
            parametros_json=str({'tipo_documento': tipo_documento, 'setor': setor}),
            resposta_json=str(resultado),
            sucesso=True,
            tempo_resposta_ms=tempo_ms
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'mensagem': 'Sugestão gerada com sucesso',
            'responsavel_id': resultado.get('responsavel_id'),
            'nome': resultado.get('nome'),
            'confianca': resultado.get('confianca'),
            'justificativa': resultado.get('justificativa'),
            'alternativas': resultado.get('alternativas', []),
            'tempo_ms': tempo_ms
        })

    except AIClientError as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('/logs/<int:documento_id>', methods=['GET'])
@login_required
def listar_logs_ia(documento_id):
    """
    Lista logs de chamadas de IA para um documento

    Returns:
        JSON com histórico de chamadas de IA
    """
    # Verifica permissão
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para visualizar logs'}), 403

    documento = Documento.query.get_or_404(documento_id)

    logs = LogAI.query.filter_by(documento_id=documento_id).order_by(
        LogAI.data_chamada.desc()
    ).all()

    return jsonify({
        'documento': {
            'id': documento.id,
            'titulo': documento.titulo,
            'codigo': documento.codigo_provisorio or documento.codigo_definitivo
        },
        'logs': [{
            'id': log.id,
            'funcao_ia': log.funcao_ia,
            'usuario': log.usuario.nome,
            'data_chamada': log.data_chamada.isoformat(),
            'sucesso': log.sucesso,
            'mensagem_erro': log.mensagem_erro,
            'tempo_resposta_ms': log.tempo_resposta_ms
        } for log in logs],
        'total': len(logs)
    })


@bp.route('/stats', methods=['GET'])
@login_required
def estatisticas_ia():
    """
    Estatísticas de uso da IA
    Apenas para administradores
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem visualizar estatísticas'}), 403

    from sqlalchemy import func

    # Total de chamadas
    total_chamadas = LogAI.query.count()

    # Chamadas por função
    chamadas_por_funcao = db.session.query(
        LogAI.funcao_ia,
        func.count(LogAI.id).label('total')
    ).group_by(LogAI.funcao_ia).all()

    # Taxa de sucesso
    total_sucesso = LogAI.query.filter_by(sucesso=True).count()
    taxa_sucesso = (total_sucesso / total_chamadas * 100) if total_chamadas > 0 else 0

    # Tempo médio de resposta
    tempo_medio = db.session.query(func.avg(LogAI.tempo_resposta_ms)).scalar() or 0

    return jsonify({
        'total_chamadas': total_chamadas,
        'total_sucesso': total_sucesso,
        'total_erro': total_chamadas - total_sucesso,
        'taxa_sucesso': round(taxa_sucesso, 2),
        'tempo_medio_ms': round(tempo_medio, 2),
        'chamadas_por_funcao': {
            funcao: total for funcao, total in chamadas_por_funcao
        }
    })
