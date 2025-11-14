# TESTE DE ASSINATURA - DIAGNÓSTICO COMPLETO

## 🔍 LOGS DETALHADOS ADICIONADOS

Foram adicionados logs detalhados que aparecem no **console do servidor Flask** (stderr).

Os logs mostram:
1. Quando um aprovador assina
2. Quantos aprovadores já assinaram vs. total
3. Status de cada item do bloco
4. Se a verificação de "todos aprovaram" passou
5. Se _finalizar_bloco_assinatura foi chamado
6. Se a tarefa de publicação foi criada
7. Se o commit foi realizado

## 📋 COMO TESTAR

### 1. Reinicie o servidor Flask

```bash
# Se estiver rodando com flask run:
# Pare com Ctrl+C e rode novamente:
flask run

# Se estiver rodando com python:
python run.py

# Se estiver rodando em background:
pkill -f "flask run" && flask run
```

### 2. Faça o teste de assinatura

1. Acesse o sistema
2. Crie um documento ou use um existente
3. Passe pelas etapas até chegar nas assinaturas
4. **ASSINE COM TODOS OS APROVADORES**
5. **OLHE O CONSOLE DO SERVIDOR FLASK**

### 3. O que você verá no console

Se tudo estiver funcionando, você verá algo assim:

```
[WORKFLOW] ================================================================================
[WORKFLOW] ETAPA 3: Aprovador assina documento
[WORKFLOW] Decisão: APROVADO
[WORKFLOW] ================================================================================
[WORKFLOW] Bloco ID: 1, Item ID: 2, Modo: concomitante
[WORKFLOW] Aprovador: Maria Silva, Ordem: 2
[WORKFLOW] 🔍 VERIFICANDO STATUS DO BLOCO CONCOMITANTE
[WORKFLOW] Total de aprovadores: 2
[WORKFLOW] Já aprovaram: 2
[WORKFLOW] Pendentes: 0
[WORKFLOW]    Item #1 - João Santos: Aprovado
[WORKFLOW]    Item #2 - Maria Silva: Aprovado
[WORKFLOW] 🧮 Verificando: 2 == 2 and 0 == 0
[WORKFLOW] 🎉 TODOS APROVARAM! Chamando _finalizar_bloco_assinatura
[WORKFLOW] ================================================================================
[WORKFLOW] 🎉 FINALIZANDO BLOCO DE ASSINATURA
[WORKFLOW] 📄 Documento: POP.Operacoes-001
[WORKFLOW] 📦 Bloco ID: 1
[WORKFLOW] ================================================================================
[WORKFLOW] 👤 Validador: Validador UGQ (ID: 3)
[WORKFLOW] 📝 Criando tarefa de publicação...
[WORKFLOW] ➕ Tarefa criada (ainda não adicionada à sessão)
[WORKFLOW] 📋 Detalhes da tarefa:
[WORKFLOW]    - documento_id: 1
[WORKFLOW]    - criador_id: 3
[WORKFLOW]    - responsavel_id: 3
[WORKFLOW]    - tipo_tarefa: Publicar Documento Aprovado
[WORKFLOW]    - concluida: False
[WORKFLOW] ✅ Tarefa adicionada à sessão
[WORKFLOW] 💾 Fazendo commit...
[WORKFLOW] ✅ COMMIT REALIZADO COM SUCESSO!
[WORKFLOW] 🎊 TAREFA DE PUBLICAÇÃO CRIADA E COMMITADA!
[WORKFLOW]    ID da tarefa: #5
[WORKFLOW]    Responsável: Validador UGQ (ID: 3)
[WORKFLOW]    Tipo: Publicar Documento Aprovado
[WORKFLOW] ================================================================================
```

### 4. Se NÃO aparecer "TODOS APROVARAM"

Se você ver:

```
[WORKFLOW] Total de aprovadores: 2
[WORKFLOW] Já aprovaram: 1  <-- AQUI ESTÁ O PROBLEMA
[WORKFLOW] Pendentes: 1
[WORKFLOW] ⏳ Aguardando 1 aprovador(es)
```

Significa que o item NÃO foi marcado como "Aprovado" no banco de dados antes de fazer a verificação.

### 5. Se DER ERRO

Se aparecer:

```
[WORKFLOW] ❌ ERRO em _finalizar_bloco_assinatura: <mensagem>
```

Então o problema está na função de finalização. O erro completo aparecerá no console.

## 🚨 ENVIE OS LOGS

**COPIE E COLE TODO O OUTPUT DO CONSOLE** que aparecer quando você assinar com o segundo aprovador.

Isso vai mostrar exatamente onde o problema está!

## 🔧 VERIFICAÇÃO ADICIONAL NO BANCO DE DADOS

Se quiser verificar diretamente no banco:

```bash
# Acesse o banco SQLite (se for SQLite)
sqlite3 instance/ged.db

# Ou PostgreSQL
psql -d ged

# Execute:
SELECT id, ordem, status, aprovador_id FROM itens_bloco_assinatura WHERE bloco_id = 1;
SELECT id, tipo_tarefa, responsavel_id, concluida FROM tarefas WHERE documento_id = 1 ORDER BY id DESC;
```

Isso mostra:
1. Status de cada item de assinatura
2. Todas as tarefas criadas para o documento
