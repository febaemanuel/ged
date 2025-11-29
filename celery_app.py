"""
Configuração do Celery para Sistema GED EBSERH
Background tasks e tarefas agendadas
"""
import os
from celery import Celery
from celery.schedules import crontab

# Configuração do broker (Redis)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Cria instância do Celery
celery = Celery(
    'ged',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks']  # Importa tasks.py automaticamente
)

# Configurações do Celery
celery.conf.update(
    # Serialização
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Timezone
    timezone='America/Fortaleza',
    enable_utc=True,

    # Retry e confiabilidade
    task_acks_late=True,  # Confirma tarefa só após conclusão
    task_reject_on_worker_lost=True,  # Rejeita tarefa se worker crashar
    task_track_started=True,  # Rastreia quando tarefa inicia

    # Resultados
    result_expires=3600,  # Resultados expiram após 1 hora
    result_extended=True,  # Armazena mais informações sobre resultados

    # Performance
    worker_prefetch_multiplier=1,  # Pega 1 tarefa por vez (melhor para tarefas longas)
    worker_max_tasks_per_child=1000,  # Recria worker após 1000 tarefas (previne memory leak)

    # Tarefas agendadas (Celery Beat)
    beat_schedule={
        # Verifica documentos vencidos todo dia às 2h da manhã
        'verificar-documentos-vencidos': {
            'task': 'tasks.verificar_documentos_vencidos',
            'schedule': crontab(hour=2, minute=0),
            'options': {'expires': 3600}  # Expira em 1h se não executar
        },

        # Backup diário às 3h da manhã
        'backup-banco-dados': {
            'task': 'tasks.backup_banco_dados',
            'schedule': crontab(hour=3, minute=0),
            'options': {'expires': 3600}
        },

        # Limpa logs antigos toda semana (domingo às 4h)
        'limpar-logs-antigos': {
            'task': 'tasks.limpar_logs_antigos',
            'schedule': crontab(hour=4, minute=0, day_of_week=0),
            'options': {'expires': 7200}
        },

        # Verifica documentos próximos de vencer (todo dia às 9h)
        'alertar-documentos-vencendo': {
            'task': 'tasks.alertar_documentos_vencendo',
            'schedule': crontab(hour=9, minute=0),
            'options': {'expires': 3600}
        },
    }
)

# Configuração de rotas de tarefas (opcional)
# Permite direcionar tarefas específicas para workers específicos
celery.conf.task_routes = {
    'tasks.processar_documento_ia': {'queue': 'ia'},  # Fila separada para IA
    'tasks.gerar_relatorio_pdf': {'queue': 'relatorios'},  # Fila separada para relatórios
    'tasks.*': {'queue': 'default'},  # Resto vai para fila padrão
}

if __name__ == '__main__':
    celery.start()
