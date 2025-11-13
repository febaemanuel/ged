"""
Cliente para integração com API externa de IA (DeepSeek)

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
import os
from flask import current_app

logger = logging.getLogger(__name__)

# Importa OpenAI para DeepSeek (compatível)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("Biblioteca openai não instalada. Funcionalidades de IA estarão limitadas.")


class AIClientError(Exception):
    """Exceção customizada para erros da API de IA"""
    pass


def _get_api_config():
    """Retorna configurações da API de IA"""
    return {
        'base_url': current_app.config.get('AI_API_BASE_URL'),
        'api_key': current_app.config.get('AI_API_KEY'),
        'timeout': current_app.config.get('AI_API_TIMEOUT', 30),
        'model': current_app.config.get('AI_API_MODEL', 'deepseek-chat')
    }


def _get_openai_client():
    """Retorna cliente OpenAI configurado para DeepSeek"""
    if not OPENAI_AVAILABLE:
        raise AIClientError("Biblioteca openai não instalada. Execute: pip install openai")

    config = _get_api_config()
    return OpenAI(
        api_key=config['api_key'],
        base_url=config['base_url']
    )


def _call_deepseek(system_prompt, user_prompt, temperature=0.7, retries=3):
    """
    Faz chamada ao DeepSeek usando requisições HTTP diretas com retry logic

    Args:
        system_prompt: Instrução de sistema
        user_prompt: Prompt do usuário
        temperature: Temperatura para geração (0.0 a 1.0)
        retries: Número de tentativas em caso de erro

    Returns:
        str: Resposta da IA
    """
    config = _get_api_config()
    delay = 2  # Delay inicial em segundos

    for attempt in range(retries):
        try:
            start_time = time.time()

            # URL da API DeepSeek
            url = f"{config['base_url']}/v1/chat/completions"

            # Headers da requisição
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }

            # Corpo da requisição
            data = {
                "model": config['model'],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 2000
            }

            # Faz a requisição HTTP POST
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=config['timeout']
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Verifica se foi bem-sucedido
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                logger.info(f"Chamada DeepSeek bem-sucedida na tentativa {attempt + 1} ({elapsed_ms}ms)")
                return result
            else:
                raise AIClientError(f"DeepSeek retornou status {response.status_code}: {response.text}")

        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1}/{retries} falhou: {str(e)}")

            if attempt < retries - 1:
                # Espera com backoff exponencial antes de tentar novamente
                wait_time = delay * (2 ** attempt)
                logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
            else:
                # Última tentativa falhou
                logger.error(f"Todas as {retries} tentativas falharam ao chamar DeepSeek")
                raise AIClientError(f"Erro ao comunicar com DeepSeek após {retries} tentativas: {str(e)}")


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
    Extrai texto de um documento (.doc, .docx, .odt, .pdf)

    Args:
        file_path: Caminho do arquivo

    Returns:
        dict: {
            'texto': str,
            'metadados': dict,
            'num_paginas': int (se aplicável)
        }

    Example:
        >>> result = extract_text('/path/to/document.pdf')
        >>> print(result['texto'])
    """
    logger.info(f"Extraindo texto do arquivo: {file_path}")

    if not os.path.exists(file_path):
        raise AIClientError(f"Arquivo não encontrado: {file_path}")

    extensao = file_path.lower().split('.')[-1]
    texto = ""
    metadados = {}

    try:
        if extensao == 'pdf':
            # Extrai texto de PDF
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            metadados['num_paginas'] = len(reader.pages)
            for page in reader.pages:
                texto += page.extract_text() + "\n"

        elif extensao in ['doc', 'docx']:
            # Extrai texto de Word
            from docx import Document
            doc = Document(file_path)
            metadados['num_paragrafos'] = len(doc.paragraphs)
            for para in doc.paragraphs:
                texto += para.text + "\n"

        elif extensao == 'odt':
            # Extrai texto de ODT
            from odf import text, teletype
            from odf.opendocument import load
            textdoc = load(file_path)
            allparas = textdoc.getElementsByType(text.P)
            for para in allparas:
                texto += teletype.extractText(para) + "\n"

        else:
            raise AIClientError(f"Extensão não suportada: {extensao}")

        metadados['tamanho_caracteres'] = len(texto)
        metadados['tamanho_palavras'] = len(texto.split())

        return {
            'texto': texto.strip(),
            'metadados': metadados
        }

    except ImportError as e:
        logger.error(f"Biblioteca necessária não instalada: {str(e)}")
        raise AIClientError(f"Biblioteca de processamento não instalada: {str(e)}")
    except Exception as e:
        logger.error(f"Erro ao extrair texto: {str(e)}")
        raise AIClientError(f"Erro ao extrair texto: {str(e)}")


def _clean_json_response(text):
    """
    Limpa resposta do DeepSeek removendo markdown e texto extra

    Args:
        text: Texto bruto da resposta

    Returns:
        str: JSON limpo
    """
    import re
    import json

    # Remove markdown code blocks (```json ... ``` ou ``` ... ```)
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    # Tenta encontrar JSON válido na resposta
    # Procura por { ... } ou [ ... ]
    json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # Se não encontrou, retorna o texto limpo
    return text.strip()


def classify_document(text):
    """
    Classifica o tipo de documento baseado no conteúdo usando DeepSeek

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

    system_prompt = """Você é um especialista em classificação de documentos técnicos.
Analise o texto e classifique em uma das categorias:
- POP (Procedimento Operacional Padrão): instruções passo a passo para realizar tarefas
- Manual: documentação técnica, guias de uso, manuais de equipamentos
- Protocolo: regras, normas, diretrizes, acordos

Responda APENAS em formato JSON válido, sem markdown:
{
    "tipo_documento": "POP" ou "Manual" ou "Protocolo",
    "confianca": 0.0 a 1.0,
    "caracteristicas": ["lista", "de", "características"]
}"""

    # Limita texto para não exceder tokens
    texto_limitado = text[:3000] if len(text) > 3000 else text
    user_prompt = f"Classifique este documento:\n\n{texto_limitado}"

    try:
        result_text = _call_deepseek(system_prompt, user_prompt, temperature=0.3)

        # Limpa resposta e parse JSON
        import json
        json_limpo = _clean_json_response(result_text)
        logger.info(f"JSON limpo: {json_limpo[:200]}")  # Log para debug
        result = json.loads(json_limpo)

        return result

    except json.JSONDecodeError as e:
        logger.warning(f"DeepSeek retornou resposta inválida: {str(e)}, resposta: {result_text[:500]}")
        return {
            'tipo_documento': 'Manual',
            'confianca': 0.5,
            'caracteristicas': ['Classificação manual necessária']
        }
    except Exception as e:
        logger.error(f"Erro na classificação: {str(e)}")
        raise AIClientError(f"Erro ao classificar documento: {str(e)}")


def summarize_text(text, max_length=500):
    """
    Gera resumo do texto usando DeepSeek

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

    system_prompt = """Você é um especialista em análise e resumo de documentos técnicos.
Analise o texto COMPLETO e forneça um resumo conciso, palavras-chave e tópicos principais.

Responda APENAS em formato JSON válido, sem markdown:
{
    "resumo": "resumo conciso do documento",
    "palavras_chave": ["palavra1", "palavra2", "palavra3"],
    "topicos_principais": ["tópico 1", "tópico 2", "tópico 3"]
}"""

    # Limita texto para não exceder tokens (mas envia o máximo possível)
    texto_limitado = text[:8000] if len(text) > 8000 else text
    user_prompt = f"Resuma este documento (máximo {max_length} caracteres no resumo):\n\n{texto_limitado}"

    try:
        result_text = _call_deepseek(system_prompt, user_prompt, temperature=0.5)

        # Limpa resposta e parse JSON
        import json
        json_limpo = _clean_json_response(result_text)
        logger.info(f"JSON limpo (resumo): {json_limpo[:200]}")  # Log para debug
        result = json.loads(json_limpo)

        # Limita resumo ao tamanho máximo
        if len(result.get('resumo', '')) > max_length:
            result['resumo'] = result['resumo'][:max_length] + '...'

        return result

    except json.JSONDecodeError as e:
        logger.warning(f"DeepSeek retornou resposta inválida: {str(e)}, resposta: {result_text[:500]}")
        return {
            'resumo': text[:max_length] + '...' if len(text) > max_length else text,
            'palavras_chave': [],
            'topicos_principais': []
        }
    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {str(e)}")
        raise AIClientError(f"Erro ao gerar resumo: {str(e)}")


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
