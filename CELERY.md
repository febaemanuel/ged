# Background Tasks com Celery - Sistema GED EBSERH

## Visão Geral

O sistema GED utiliza **Celery** com **Redis** para executar tarefas em background, melhorando a performance e experiência do usuário.

### O que são Background Tasks?

Tarefas que levam tempo para executar (processamento de IA, geração de PDFs, envio de emails) são executadas em segundo plano, permitindo que o usuário continue trabalhando enquanto a tarefa é processada.

## Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Flask     │────▶│    Redis    │◀────│   Celery    │
│   (Web)     │     │  (Broker)   │     │  (Worker)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                                        │
      │                                        │
      └────────────────────┬───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │  (Database) │
                    └─────────────┘
```

### Componentes

1. **Redis**: Broker de mensagens (fila de tarefas)
2. **Celery Worker**: Processa tarefas em background
3. **Celery Beat**: Agendador de tarefas periódicas (cron)
4. **Flower**: Interface web de monitoramento (opcional)

## Tarefas Implementadas

### 📄 Processamento de Documentos

#### `processar_documento_ia(documento_id)`
- **Quando**: Executado automaticamente ao criar documento
- **O que faz**:
  - Extrai texto do PDF/DOCX/ODT
  - Analisa com IA DeepSeek
  - Extrai metadados automaticamente
  - Salva log da operação
- **Retry**: 3 tentativas com backoff exponencial
- **Tempo estimado**: 10-30 segundos

#### `gerar_pdf_publicado(documento_id)`
- **Quando**: Ao publicar documento (opcional)
- **O que faz**:
  - Gera PDF com cabeçalho e metadados
  - Adiciona código definitivo
  - Formata para impressão
- **Tempo estimado**: 5-15 segundos

### ⏰ Tarefas Agendadas (Cron)

#### `verificar_documentos_vencidos()`
- **Frequência**: Diariamente às 2h da manhã
- **O que faz**:
  - Verifica documentos com data_vencimento < hoje
  - Marca como Obsoleto
  - Notifica criadores via email

#### `alertar_documentos_vencendo()`
- **Frequência**: Diariamente às 9h da manhã
- **O que faz**:
  - Verifica documentos vencendo em 30 dias
  - Envia alertas para responsáveis
  - Facilita planejamento de revisões

#### `backup_banco_dados()`
- **Frequência**: Diariamente às 3h da manhã
- **O que faz**:
  - Realiza backup PostgreSQL com pg_dump
  - Salva em `/app/backups/ged_backup_YYYY-MM-DD.sql`
  - Remove backups antigos (> 7 dias)
- **Importante**: Monte volume para persistir backups!

#### `limpar_logs_antigos()`
- **Frequência**: Semanalmente aos domingos às 4h
- **O que faz**:
  - Remove logs de IA > 90 dias
  - Remove logs de WhatsApp > 90 dias
  - Libera espaço no banco

### 📧 Notificações

#### `enviar_notificacao_email(usuario_id, assunto, mensagem)`
- **Quando**: Chamado por outras funções
- **O que faz**:
  - Envia email via SMTP configurado
  - Retry automático em caso de falha
- **Retry**: 3 tentativas com 5 minutos de intervalo

#### `enviar_notificacoes_setor(setor, assunto, mensagem)`
- **Quando**: Notificações em massa
- **O que faz**:
  - Busca todos usuários do setor
  - Agenda email para cada um (em paralelo)

### 📊 Relatórios

#### `gerar_relatorio_pdf(tipo_relatorio, parametros)`
- **Quando**: Ao solicitar relatório pesado
- **O que faz**:
  - Gera relatórios mensais/anuais
  - Processa grandes volumes de dados
  - Retorna PDF pronto para download
- **Tipos**: 'mensal', 'anual'
- **Tempo estimado**: 30-120 segundos

## Uso no Código

### Disparar Tarefa em Background

```python
from tasks import processar_documento_ia

# Dispara tarefa e continua execução
processar_documento_ia.delay(documento.id)
```

### Aguardar Resultado (Síncrono)

```python
from tasks import processar_documento_ia

# Executa e aguarda resultado
resultado = processar_documento_ia(documento.id)
```

### Verificar Status da Tarefa

```python
from celery.result import AsyncResult

# Verifica status
task = AsyncResult(task_id)
print(task.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(task.result)  # Resultado quando concluída
```

## Configuração

### Variáveis de Ambiente (.env)

```bash
# Redis
REDIS_URL=redis://redis:6379/0

# Flower (monitoramento)
FLOWER_PORT=5555
FLOWER_USER=admin
FLOWER_PASSWORD=admin_CHANGE_IN_PRODUCTION

# Email (para notificações)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-aplicativo
```

### Docker Compose

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs do worker
docker-compose logs -f celery_worker

# Ver logs do beat (cron)
docker-compose logs -f celery_beat

# Reiniciar worker após mudanças no código
docker-compose restart celery_worker
```

### Habilitar Flower (Monitoramento Web)

1. No `docker-compose.yml`, descomente a seção `flower`
2. Configure usuário/senha no `.env`
3. Acesse: `http://localhost:5555`

## Monitoramento

### Logs

```bash
# Ver todas as tarefas executadas
docker-compose logs celery_worker | grep "Task"

# Ver tarefas agendadas (beat)
docker-compose logs celery_beat | grep "Scheduler"

# Ver tarefas com erro
docker-compose logs celery_worker | grep "ERROR"
```

### Flower (Interface Web)

![Flower Dashboard](https://flower.readthedocs.io/en/latest/_images/dashboard.png)

Acesse `http://localhost:5555` para:
- Ver tarefas em execução
- Histórico de tarefas
- Estatísticas de performance
- Workers ativos
- Fila de tarefas

### Comandos Úteis

```bash
# Inspecionar workers ativos
docker exec ged_celery_worker celery -A celery_app inspect active

# Ver tarefas agendadas
docker exec ged_celery_worker celery -A celery_app inspect scheduled

# Ver estatísticas
docker exec ged_celery_worker celery -A celery_app inspect stats

# Limpar fila de tarefas
docker exec ged_celery_worker celery -A celery_app purge
```

## Troubleshooting

### Worker não inicia

```bash
# Verificar logs
docker-compose logs celery_worker

# Verificar se Redis está rodando
docker-compose ps redis
docker exec ged_redis redis-cli ping  # Deve retornar PONG
```

### Tarefas não são executadas

1. Verificar se worker está rodando:
```bash
docker-compose ps celery_worker
```

2. Verificar conexão com Redis:
```bash
docker exec ged_web python -c "from celery_app import celery; print(celery.broker_url)"
```

3. Verificar fila de tarefas:
```bash
docker exec ged_celery_worker celery -A celery_app inspect active
```

### Tarefas falhando

1. Ver logs detalhados:
```bash
docker-compose logs celery_worker | tail -100
```

2. Testar tarefa manualmente:
```python
# No shell Flask
from tasks import processar_documento_ia
resultado = processar_documento_ia(1)  # Executa síncrono
print(resultado)
```

### Tarefas agendadas não executam

1. Verificar se Beat está rodando:
```bash
docker-compose ps celery_beat
docker-compose logs celery_beat
```

2. Verificar timezone:
```bash
docker exec ged_celery_beat python -c "from celery_app import celery; print(celery.conf.timezone)"
# Deve retornar: America/Fortaleza
```

## Performance

### Concorrência

Por padrão, worker executa **4 tarefas em paralelo**. Para alterar:

```yaml
# docker-compose.yml
celery_worker:
  command: celery -A celery_app worker --loglevel=info --concurrency=8
```

### Filas Separadas

Tarefas pesadas podem usar filas dedicadas:

```python
# celery_app.py já configurado com:
# - ia: Processamento IA
# - relatorios: Geração de relatórios
# - default: Outras tarefas

# Iniciar worker para fila específica
celery -A celery_app worker -Q ia --loglevel=info
```

### Memory Leak Prevention

Worker reinicia após 1000 tarefas (configurado):

```python
# celery_app.py
worker_max_tasks_per_child=1000
```

## Desenvolvimento

### Adicionar Nova Tarefa

1. Edite `tasks.py`:

```python
@celery.task(base=FlaskTask, bind=True, max_retries=3)
def minha_nova_tarefa(self, parametro):
    """Descrição da tarefa"""
    try:
        # Seu código aqui
        return {'status': 'success', 'resultado': 'dados'}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

2. Use na rota:

```python
from tasks import minha_nova_tarefa

@app.route('/executar')
def executar():
    minha_nova_tarefa.delay('parametro')
    return {'mensagem': 'Tarefa agendada'}
```

3. Reinicie worker:

```bash
docker-compose restart celery_worker
```

### Adicionar Tarefa Agendada

1. Edite `celery_app.py`:

```python
beat_schedule={
    'minha-tarefa-diaria': {
        'task': 'tasks.minha_nova_tarefa',
        'schedule': crontab(hour=10, minute=0),  # 10h da manhã
        'args': ('parametro',)
    },
}
```

2. Reinicie beat:

```bash
docker-compose restart celery_beat
```

## Exemplos de Crontab

```python
from celery.schedules import crontab

# A cada 15 minutos
crontab(minute='*/15')

# Todo dia às 8h
crontab(hour=8, minute=0)

# Segunda a sexta às 9h
crontab(hour=9, minute=0, day_of_week='1-5')

# Primeiro dia do mês às 1h
crontab(hour=1, minute=0, day_of_month='1')

# A cada hora
crontab(minute=0)
```

## Recursos Adicionais

- [Documentação Celery](https://docs.celeryproject.org/)
- [Flower Docs](https://flower.readthedocs.io/)
- [Redis Docs](https://redis.io/docs/)

## Segurança

1. **NUNCA** exponha Redis publicamente (porta 6379)
2. Configure senha do Flower em produção
3. Use HTTPS para Flower em produção
4. Limite recursos do Redis (configurado em docker-compose.yml):
   ```yaml
   command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
   ```

## Backup

O volume `backups` deve ser montado em produção para persistir backups:

```yaml
volumes:
  backups:
    driver: local
    driver_opts:
      type: none
      device: /caminho/no/host/backups
      o: bind
```

Ou usar backup externo:

```bash
# Copiar backups para outro servidor
rsync -avz /var/lib/docker/volumes/ged_backups/ backup-server:/backups/ged/
```

---

**Documentação atualizada**: 2025-11-29
**Versão Celery**: 5.3.4
**Versão Redis**: 7-alpine
