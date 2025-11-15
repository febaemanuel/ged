"""
Utilitários de Segurança
Funções para prevenir vulnerabilidades comuns
"""
import os
import re
from pathlib import Path
from typing import Optional
from sqlalchemy import text


def sanitize_like_pattern(user_input: str) -> str:
    """
    Sanitiza input do usuário para uso em queries ILIKE/LIKE
    Previne SQL injection escapando caracteres especiais

    Args:
        user_input: String fornecida pelo usuário

    Returns:
        String sanitizada segura para uso em ILIKE
    """
    if not user_input:
        return ""

    # Escapa caracteres especiais do LIKE: %, _, \
    sanitized = user_input.replace('\\', '\\\\')
    sanitized = sanitized.replace('%', '\\%')
    sanitized = sanitized.replace('_', '\\_')

    # Remove caracteres potencialmente perigosos
    # Permite apenas: letras, números, espaços, hífen, ponto, underline
    sanitized = re.sub(r'[^\w\s\-\.]', '', sanitized)

    # Limita tamanho para prevenir DoS
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()


def safe_ilike_filter(column, user_input: str):
    """
    Cria filtro ILIKE seguro usando bind parameters

    Args:
        column: Coluna SQLAlchemy
        user_input: Input do usuário

    Returns:
        Expressão SQLAlchemy segura
    """
    if not user_input:
        return None

    sanitized = sanitize_like_pattern(user_input)
    if not sanitized:
        return None

    # Usa .ilike() com % adicionado aqui, não no input do usuário
    return column.ilike(f'%{sanitized}%')


def validate_file_path(file_path: str, allowed_directory: str) -> bool:
    """
    Valida que o caminho do arquivo está dentro do diretório permitido
    Previne path traversal attacks

    Args:
        file_path: Caminho do arquivo a validar
        allowed_directory: Diretório base permitido

    Returns:
        True se o caminho é seguro, False caso contrário
    """
    if not file_path or not allowed_directory:
        return False

    try:
        # Resolve caminhos absolutos e normaliza
        file_abs = Path(file_path).resolve()
        dir_abs = Path(allowed_directory).resolve()

        # Verifica se o arquivo está dentro do diretório permitido
        # usando .is_relative_to() ou verificação manual para Python < 3.9
        try:
            return file_abs.is_relative_to(dir_abs)
        except AttributeError:
            # Fallback para Python < 3.9
            try:
                file_abs.relative_to(dir_abs)
                return True
            except ValueError:
                return False
    except (ValueError, OSError):
        return False


def get_safe_file_path(filename: str, base_directory: str) -> Optional[str]:
    """
    Constrói caminho de arquivo seguro dentro do diretório base

    Args:
        filename: Nome do arquivo (pode vir do banco de dados)
        base_directory: Diretório base permitido

    Returns:
        Caminho completo seguro ou None se inválido
    """
    if not filename or not base_directory:
        return None

    # Remove qualquer tentativa de path traversal do filename
    # Pega apenas o nome do arquivo (sem diretórios)
    safe_filename = os.path.basename(filename)

    # Constrói caminho completo
    full_path = os.path.join(base_directory, safe_filename)

    # Valida que está dentro do diretório permitido
    if validate_file_path(full_path, base_directory):
        return full_path

    return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida força da senha

    Requisitos:
    - Mínimo 12 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial

    Args:
        password: Senha a validar

    Returns:
        Tupla (is_valid, error_message)
    """
    if not password:
        return False, "Senha não pode ser vazia"

    if len(password) < 12:
        return False, "Senha deve ter no mínimo 12 caracteres"

    if not re.search(r'[A-Z]', password):
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not re.search(r'[a-z]', password):
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        return False, "Senha deve conter pelo menos um caractere especial (!@#$%^&*...)"

    # Verifica senhas comuns
    common_passwords = [
        'password123!', 'Admin@123456', 'P@ssw0rd1234',
        'Welcome@2024', 'Senha@123456'
    ]
    if password in common_passwords:
        return False, "Senha muito comum. Escolha uma senha mais forte"

    return True, ""


def sanitize_log_data(data: dict) -> dict:
    """
    Remove dados sensíveis de dicionários antes de logar

    Args:
        data: Dicionário com dados

    Returns:
        Dicionário com dados sensíveis mascarados
    """
    sensitive_keys = [
        'senha', 'password', 'api_key', 'token', 'secret',
        'authorization', 'auth', 'credential', 'key'
    ]

    sanitized = data.copy()

    for key in sanitized:
        # Verifica se a chave contém palavras sensíveis (case-insensitive)
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = '***REDACTED***'

    return sanitized


def generate_csrf_token() -> str:
    """
    Gera token CSRF seguro

    Returns:
        Token CSRF aleatório
    """
    import secrets
    return secrets.token_urlsafe(32)
