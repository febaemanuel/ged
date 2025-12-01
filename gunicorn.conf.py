# ============================================
# Configuração do Gunicorn - GED EBSERH
# ============================================
import multiprocessing
import os

# Bind
bind = "0.0.0.0:5000"

# Workers
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"  # Async workers para melhor performance
worker_connections = 1000
max_requests = 1000  # Recicla worker após 1000 requests (previne memory leak)
max_requests_jitter = 100  # Adiciona jitter para evitar restart simultâneo

# Timeouts
timeout = 120  # 2 minutos
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Preload app (economiza memória)
preload_app = True

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "ged_ebserh"

# Server hooks
def on_starting(server):
    server.log.info("✅ Gunicorn iniciando...")

def when_ready(server):
    server.log.info(f"✅ Gunicorn pronto! {workers} workers ativos")

def on_exit(server):
    server.log.info("❌ Gunicorn encerrando...")
