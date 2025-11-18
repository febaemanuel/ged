"""
Validadores de segurança para o Sistema GED
"""
import re
from typing import Tuple


def validar_senha_forte(senha: str) -> Tuple[bool, str]:
    """
    Valida senha forte segundo NIST SP 800-63B

    Critérios:
    - Mínimo 8 caracteres
    - Máximo 128 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial

    Args:
        senha: Senha a ser validada

    Returns:
        tuple: (bool, str) - (é_válida, mensagem_erro)
    """
    if not senha:
        return False, 'Senha é obrigatória'

    if len(senha) < 8:
        return False, 'Senha deve ter no mínimo 8 caracteres'

    if len(senha) > 128:
        return False, 'Senha deve ter no máximo 128 caracteres'

    if not re.search(r'[A-Z]', senha):
        return False, 'Senha deve conter pelo menos uma letra maiúscula'

    if not re.search(r'[a-z]', senha):
        return False, 'Senha deve conter pelo menos uma letra minúscula'

    if not re.search(r'[0-9]', senha):
        return False, 'Senha deve conter pelo menos um número'

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', senha):
        return False, 'Senha deve conter pelo menos um caractere especial (!@#$%^&*...)'

    # Lista de senhas mais comuns (adicione mais conforme necessário)
    SENHAS_COMUNS = [
        '12345678', 'password', 'Password1', 'Admin123', 'Admin@123',
        'qwerty123', 'Abc12345', 'password123', 'Password123',
        '1234567890', 'Qwerty123', 'Welcome1', 'Welcome@1'
    ]

    if senha in SENHAS_COMUNS:
        return False, 'Senha muito comum. Escolha uma senha mais segura e única'

    # Verifica padrões sequenciais simples
    if re.search(r'(012|123|234|345|456|567|678|789|890)', senha):
        return False, 'Senha contém sequência numérica previsível (ex: 123, 456)'

    if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk)', senha, re.IGNORECASE):
        return False, 'Senha contém sequência alfabética previsível (ex: abc, def)'

    return True, 'OK'


def validar_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email segundo RFC 5322 (simplificado)

    Args:
        email: Email a ser validado

    Returns:
        tuple: (bool, str) - (é_válido, mensagem_erro)
    """
    if not email:
        return False, 'Email é obrigatório'

    if len(email) > 120:
        return False, 'Email muito longo (máximo 120 caracteres)'

    # Regex simplificado baseado em RFC 5322
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, 'Formato de email inválido. Use o formato: usuario@exemplo.com'

    # Validações adicionais
    if '..' in email:
        return False, 'Email não pode conter pontos consecutivos'

    if email.startswith('.') or email.endswith('.'):
        return False, 'Email não pode começar ou terminar com ponto'

    # Valida parte local (antes do @)
    local_part = email.split('@')[0]
    if len(local_part) > 64:
        return False, 'Parte local do email (antes do @) muito longa (máximo 64 caracteres)'

    # Valida domínio (depois do @)
    domain_part = email.split('@')[1]
    if len(domain_part) > 253:
        return False, 'Domínio do email (depois do @) muito longo (máximo 253 caracteres)'

    return True, 'OK'


def validar_arquivo_permitido(filename: str, file_stream=None) -> Tuple[bool, str]:
    """
    Valida se arquivo é permitido (extensão E magic bytes)

    Args:
        filename: Nome do arquivo
        file_stream: Stream do arquivo (opcional, para validação de magic bytes)

    Returns:
        tuple: (bool, str) - (é_válido, mensagem_erro)
    """
    ALLOWED_EXTENSIONS = {'doc', 'docx', 'odt', 'pdf'}

    # 1. Verifica extensão
    if '.' not in filename:
        return False, 'Arquivo sem extensão'

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f'Extensão .{ext} não permitida. Use: {", ".join(ALLOWED_EXTENSIONS)}'

    # 2. Se file_stream fornecido, valida magic bytes
    if file_stream:
        try:
            import magic

            file_stream.seek(0)  # Volta ao início
            file_header = file_stream.read(1024)
            file_stream.seek(0)  # Volta novamente

            mime = magic.from_buffer(file_header, mime=True)

            # MIME types permitidos
            ALLOWED_MIMES = {
                'application/pdf',  # PDF
                'application/msword',  # DOC
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
                'application/vnd.oasis.opendocument.text',  # ODT
            }

            if mime not in ALLOWED_MIMES:
                return False, (
                    f'Tipo de arquivo não permitido: {mime}. '
                    f'Esperado: PDF, DOC, DOCX ou ODT. '
                    f'Verifique se o arquivo não foi renomeado incorretamente.'
                )

            # 3. Valida tamanho
            file_stream.seek(0, 2)  # Vai ao final
            size = file_stream.tell()
            file_stream.seek(0)  # Volta ao início

            MAX_SIZE = 16 * 1024 * 1024  # 16 MB
            if size > MAX_SIZE:
                size_mb = size / (1024 * 1024)
                return False, f'Arquivo muito grande: {size_mb:.1f}MB. Máximo permitido: 16MB'

        except ImportError:
            # python-magic não instalado, apenas valida extensão
            pass
        except Exception as e:
            return False, f'Erro ao validar arquivo: {str(e)}'

    return True, 'OK'


def sanitizar_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres perigosos

    Args:
        filename: Nome do arquivo

    Returns:
        str: Nome sanitizado
    """
    from werkzeug.utils import secure_filename
    return secure_filename(filename)


def validar_path_seguro(base_dir: str, filepath: str) -> Tuple[bool, str]:
    """
    Valida que um caminho de arquivo está dentro do diretório base (previne path traversal)

    Args:
        base_dir: Diretório base permitido
        filepath: Caminho do arquivo a validar

    Returns:
        tuple: (bool, str) - (é_seguro, mensagem_erro)
    """
    import os

    # Normaliza caminhos
    base_dir_abs = os.path.abspath(base_dir)
    filepath_abs = os.path.abspath(filepath)

    # Verifica se o caminho do arquivo está dentro do diretório base
    if not filepath_abs.startswith(base_dir_abs + os.sep):
        return False, 'Caminho de arquivo inválido (path traversal detectado)'

    return True, 'OK'


def validar_numero_telefone(telefone: str) -> Tuple[bool, str]:
    """
    Valida número de telefone no formato internacional

    Args:
        telefone: Número de telefone

    Returns:
        tuple: (bool, str) - (é_válido, mensagem_erro)
    """
    if not telefone:
        return False, 'Telefone é obrigatório'

    # Remove espaços, parênteses, hífens
    telefone_limpo = re.sub(r'[\s\(\)\-]', '', telefone)

    # Deve começar com +
    if not telefone_limpo.startswith('+'):
        return False, 'Telefone deve começar com + seguido do código do país (ex: +5585999999999)'

    # Deve conter apenas + e dígitos
    if not re.match(r'^\+\d+$', telefone_limpo):
        return False, 'Telefone deve conter apenas números após o +'

    # Tamanho mínimo e máximo
    if len(telefone_limpo) < 10:
        return False, 'Telefone muito curto (mínimo 10 caracteres com código do país)'

    if len(telefone_limpo) > 20:
        return False, 'Telefone muito longo (máximo 20 caracteres)'

    return True, 'OK'
