"""
Cliente para integração com API externa de IA

Este módulo é responsável por se comunicar com a API de IA externa,
enviando dados e recebendo resultados processados.

Funções disponíveis:
- extract_text: Extrai texto de documentos (.doc, .odt, .pdf)
- classify_document: Classifica o tipo de documento
- summarize_text: Gera resumo do conteúdo
- search_semantic: Busca semântica de documentos
- suggest_responsavel: Sugere responsável baseado em histórico
"""

import requests
import logging
import time
from flask import current_app

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Exceção customizada para erros da API de IA"""
    pass


def _get_api_config():
    """Retorna configurações da API de IA"""
    return {
        'base_url': current_app.config.get('AI_API_BASE_URL'),
        'api_key': current_app.config.get('AI_API_KEY'),
        'timeout': current_app.config.get('AI_API_TIMEOUT', 30)
    }


def _make_request(endpoint, method='POST', files=None, json_data=None):
    """
    Realiza requisição à API de IA com tratamento de erros

    Args:
        endpoint: Endpoint da API (ex: '/extract')
        method: Método HTTP (POST, GET)
        files: Dicionário de arquivos para upload
        json_data: Dados JSON para enviar

    Returns:
        dict: Resposta da API em JSON

    Raises:
        AIClientError: Em caso de erro na comunicação
    """
    config = _get_api_config()
    url = f"{config['base_url']}{endpoint}"

    headers = {}
    if config['api_key']:
        headers['Authorization'] = f"Bearer {config['api_key']}"

    try:
        start_time = time.time()

        if method == 'POST':
            response = requests.post(
                url,
                files=files,
                json=json_data,
                headers=headers,
                timeout=config['timeout']
            )
        else:
            response = requests.get(
                url,
                headers=headers,
                timeout=config['timeout']
            )

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Verifica se a requisição foi bem-sucedida
        response.raise_for_status()

        result = response.json()
        result['_tempo_resposta_ms'] = elapsed_ms

        logger.info(f"Chamada à IA bem-sucedida: {endpoint} ({elapsed_ms}ms)")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"Timeout na chamada à API de IA: {endpoint}")
        raise AIClientError(f"Timeout ao chamar API de IA (>{config['timeout']}s)")

    except requests.exceptions.ConnectionError:
        logger.error(f"Erro de conexão com API de IA: {endpoint}")
        raise AIClientError("Erro de conexão com API de IA")

    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP na API de IA: {e.response.status_code} - {endpoint}")
        raise AIClientError(f"Erro HTTP {e.response.status_code}: {e.response.text}")

    except Exception as e:
        logger.error(f"Erro inesperado na API de IA: {str(e)}")
        raise AIClientError(f"Erro ao comunicar com API de IA: {str(e)}")


def extract_text(file_path):
    """
    Extrai texto de um documento

    Args:
        file_path: Caminho do arquivo (.doc, .odt, .pdf)

    Returns:
        dict: {
            'texto': str,
            'entidades': dict,
            'metadados': dict
        }

    Example:
        >>> result = extract_text('/path/to/document.pdf')
        >>> print(result['texto'])
    """
    logger.info(f"Extraindo texto do arquivo: {file_path}")

    with open(file_path, 'rb') as f:
        files = {'file': f}
        result = _make_request('/api/ai/extract', files=files)

    return result


def classify_document(text):
    """
    Classifica o tipo de documento baseado no conteúdo

    Args:
        text: Texto do documento

    Returns:
        dict: {
            'tipo_documento': str ('POP', 'Manual', 'Protocolo'),
            'confianca': float (0.0 a 1.0),
            'caracteristicas': list
        }

    Example:
        >>> result = classify_document("Este é um procedimento operacional...")
        >>> print(result['tipo_documento'])
        'POP'
    """
    logger.info(f"Classificando documento (texto com {len(text)} caracteres)")

    json_data = {'texto': text}
    result = _make_request('/api/ai/classify', json_data=json_data)

    return result


def summarize_text(text, max_length=500):
    """
    Gera resumo do texto

    Args:
        text: Texto completo do documento
        max_length: Tamanho máximo do resumo em caracteres

    Returns:
        dict: {
            'resumo': str,
            'palavras_chave': list,
            'topicos_principais': list
        }

    Example:
        >>> result = summarize_text("Longo texto do documento...")
        >>> print(result['resumo'])
    """
    logger.info(f"Gerando resumo de texto ({len(text)} caracteres)")

    json_data = {
        'texto': text,
        'max_length': max_length
    }
    result = _make_request('/api/ai/summarize', json_data=json_data)

    return result


def search_semantic(query, limit=10, filters=None):
    """
    Busca semântica de documentos

    Args:
        query: Consulta em linguagem natural
        limit: Número máximo de resultados
        filters: Filtros adicionais (tipo, setor, etc)

    Returns:
        dict: {
            'resultados': [
                {
                    'documento_id': int,
                    'titulo': str,
                    'similaridade': float,
                    'trecho_relevante': str
                },
                ...
            ],
            'total': int
        }

    Example:
        >>> result = search_semantic("procedimentos de segurança")
        >>> for doc in result['resultados']:
        ...     print(f"{doc['titulo']}: {doc['similaridade']}")
    """
    logger.info(f"Realizando busca semântica: '{query}'")

    json_data = {
        'query': query,
        'limit': limit,
        'filters': filters or {}
    }
    result = _make_request('/api/ai/search', json_data=json_data)

    return result


def suggest_responsavel(tipo_documento, setor, descricao=None):
    """
    Sugere responsável ideal para uma tarefa baseado em histórico

    Args:
        tipo_documento: Tipo do documento (POP, Manual, Protocolo)
        setor: Setor relacionado
        descricao: Descrição adicional da tarefa

    Returns:
        dict: {
            'responsavel_id': int,
            'nome': str,
            'confianca': float,
            'justificativa': str,
            'alternativas': [
                {'responsavel_id': int, 'nome': str, 'confianca': float},
                ...
            ]
        }

    Example:
        >>> result = suggest_responsavel('POP', 'Qualidade')
        >>> print(f"Sugestão: {result['nome']} ({result['confianca']:.2f})")
    """
    logger.info(f"Sugerindo responsável para {tipo_documento} - {setor}")

    json_data = {
        'tipo_documento': tipo_documento,
        'setor': setor,
        'descricao': descricao
    }
    result = _make_request('/api/ai/suggest', json_data=json_data)

    return result


def analyze_quality(text, tipo_documento):
    """
    Analisa qualidade e conformidade do documento

    Args:
        text: Texto do documento
        tipo_documento: Tipo do documento

    Returns:
        dict: {
            'score_qualidade': float (0-100),
            'problemas': [
                {'tipo': str, 'descricao': str, 'severidade': str},
                ...
            ],
            'sugestoes': [str, ...],
            'conformidade_padrao': bool
        }
    """
    logger.info(f"Analisando qualidade do documento {tipo_documento}")

    json_data = {
        'texto': text,
        'tipo_documento': tipo_documento
    }
    result = _make_request('/api/ai/analyze_quality', json_data=json_data)

    return result


def generate_code_suggestion(tipo_documento, setor, ano):
    """
    Gera sugestão de código definitivo baseado em padrões

    Args:
        tipo_documento: Tipo do documento
        setor: Setor do documento
        ano: Ano de publicação

    Returns:
        dict: {
            'codigo_sugerido': str,
            'formato': str,
            'ultimo_usado': str
        }
    """
    logger.info(f"Gerando sugestão de código para {tipo_documento}")

    json_data = {
        'tipo_documento': tipo_documento,
        'setor': setor,
        'ano': ano
    }
    result = _make_request('/api/ai/generate_code', json_data=json_data)

    return result
