"""
Rate Limiter para proteger contra ataques de força bruta
"""
import time
from collections import defaultdict
from threading import Lock
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


class InMemoryRateLimiter:
    """
    Rate limiter simples em memória
    Para produção, considere usar Redis para persistência entre restarts
    """

    def __init__(self):
        self.attempts = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
        self.lock = Lock()

    def is_rate_limited(self, identifier: str, max_attempts: int, window_seconds: int) -> tuple[bool, int]:
        """
        Verifica se o identificador (IP, email, etc) está limitado

        Args:
            identifier: Identificador único (IP, email, etc)
            max_attempts: Número máximo de tentativas permitidas
            window_seconds: Janela de tempo em segundos

        Returns:
            Tupla (is_limited, remaining_attempts)
        """
        with self.lock:
            now = time.time()
            cutoff = now - window_seconds

            # Remove tentativas antigas fora da janela de tempo
            self.attempts[identifier] = [
                timestamp for timestamp in self.attempts[identifier]
                if timestamp > cutoff
            ]

            current_attempts = len(self.attempts[identifier])

            if current_attempts >= max_attempts:
                # Calcula tempo até a próxima tentativa
                oldest_attempt = min(self.attempts[identifier])
                retry_after = int(oldest_attempt + window_seconds - now)
                return True, retry_after

            # Adiciona tentativa atual
            self.attempts[identifier].append(now)

            remaining = max_attempts - (current_attempts + 1)
            return False, remaining

    def clear(self, identifier: str):
        """Remove tentativas registradas para o identificador"""
        with self.lock:
            if identifier in self.attempts:
                del self.attempts[identifier]

    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """
        Remove entradas antigas para liberar memória
        Executar periodicamente em background
        """
        with self.lock:
            now = time.time()
            cutoff = now - max_age_seconds

            keys_to_delete = []
            for identifier, timestamps in self.attempts.items():
                # Remove timestamps antigos
                self.attempts[identifier] = [t for t in timestamps if t > cutoff]

                # Se não sobrou nenhum timestamp, marca para remoção
                if not self.attempts[identifier]:
                    keys_to_delete.append(identifier)

            for key in keys_to_delete:
                del self.attempts[key]


# Instância global do rate limiter
_rate_limiter = InMemoryRateLimiter()


def rate_limit(max_attempts: int = 5, window_seconds: int = 300, identifier_func=None):
    """
    Decorator para aplicar rate limiting em rotas

    Args:
        max_attempts: Número máximo de tentativas
        window_seconds: Janela de tempo em segundos
        identifier_func: Função que retorna o identificador (default: IP address)

    Exemplo:
        @rate_limit(max_attempts=5, window_seconds=300)
        @bp.route('/login', methods=['POST'])
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determina o identificador (IP por padrão)
            if identifier_func:
                identifier = identifier_func()
            else:
                # Usa IP do cliente
                identifier = request.remote_addr or 'unknown'

            # Verifica rate limit
            is_limited, value = _rate_limiter.is_rate_limited(
                identifier,
                max_attempts,
                window_seconds
            )

            if is_limited:
                retry_after = value
                return jsonify({
                    'erro': f'Muitas tentativas. Tente novamente em {retry_after} segundos.',
                    'retry_after': retry_after
                }), 429

            # Executa função normalmente
            response = f(*args, **kwargs)

            # Se login foi bem-sucedido (status 200), limpa contador
            if hasattr(response, 'status_code') and response.status_code == 200:
                _rate_limiter.clear(identifier)

            return response

        return decorated_function
    return decorator


def clear_rate_limit(identifier: str):
    """Limpa rate limit para um identificador específico"""
    _rate_limiter.clear(identifier)


def cleanup_rate_limiter():
    """Limpa entradas antigas do rate limiter"""
    _rate_limiter.cleanup_old_entries()
