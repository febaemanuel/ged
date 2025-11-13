# 📊 Status da Implementação do Workflow UGQ

## ✅ COMPLETAMENTE IMPLEMENTADO (Partes 1, 2 e 3)

### 🗄️ Banco de Dados e Modelos (100%)
- ✅ Migration SQL completa (`migrations/add_workflow_ugq.sql`)
- ✅ 4 novas tabelas criadas
- ✅ 4 novos modelos no `app/models/models.py`
- ✅ Campos adicionados em tabelas existentes
- ✅ Views e funções SQL
- ✅ Script de aplicação: `aplicar_migracao_ugq.py`

### ⚙️ Configuração (100%)
- ✅ 2 novos perfis de usuário (`config.py`)
- ✅ 8 novos status de documentos
- ✅ 8 novos tipos de tarefa

### 🔄 Workflow Service (100%)
- ✅ `app/services/workflow.py` completamente reescrito (650+ linhas)
- ✅ ETAPA 0: Autor submete documento
- ✅ ETAPA 1: Triador UGQ (3 checkpoints)
- ✅ ETAPA 2: Validador codifica
- ✅ ETAPA 3: Bloco de Assinatura (sequencial/concomitante)
- ✅ ETAPA 4: Validador publica

### 👥 Usuários de Teste (100%)
- ✅ `init_database.py` atualizado
- ✅ Triador UGQ: `triador.ugq@example.com` / `ugq123`
- ✅ Validador UGQ: `validador.ugq@example.com` / `ugq123`

---

## ⚠️ PENDENTE (Parte 4 - Interface)

### 🌐 Rotas HTTP
Precisam ser criadas em `app/routes/routes_view.py`:

```python
# Rota de submissão (Autor)
@view_bp.route('/documento/criar', methods=['POST'])
def documento_criar_ugq():
    # Chama: WorkflowUGQ.autor_submete_documento(documento)
    pass

# Rota de triagem (Triador UGQ)
@view_bp.route('/tarefa/<int:tarefa_id>/concluir_triagem', methods=['POST'])
def concluir_triagem():
    # Chama: WorkflowUGQ.triador_aprova_triagem() ou triador_devolve_ao_autor()
    pass

# Rota de codificação (Validador UGQ)
@view_bp.route('/tarefa/<int:tarefa_id>/codificar', methods=['GET', 'POST'])
def codificar_documento():
    # GET: Mostra formulário com código sugerido
    # POST: Chama WorkflowUGQ.validador_codifica_documento()
    # Redireciona para criar_bloco_assinatura()
    pass

# Rota de bloco de assinatura (Validador UGQ)
@view_bp.route('/documento/<int:documento_id>/bloco_assinatura/criar', methods=['GET', 'POST'])
def criar_bloco_assinatura():
    # GET: Mostra formulário (selecionar aprovadores, modo)
    # POST: Chama WorkflowUGQ.validador_cria_bloco_assinatura()
    pass

# Rota de assinatura (Aprovadores)
@view_bp.route('/tarefa/<int:tarefa_id>/assinar', methods=['POST'])
def assinar_documento():
    # Chama: WorkflowUGQ.aprovador_assina()
    pass

# Rota de publicação (Validador UGQ)
@view_bp.route('/tarefa/<int:tarefa_id>/publicar', methods=['POST'])
def publicar_documento():
    # Chama: WorkflowUGQ.validador_publica_documento()
    pass
```

### 🎨 Templates HTML
Precisam ser criados em `app/templates/`:

1. **`tarefa_triagem.html`** - Formulário de triagem com 3 checkpoints
2. **`tarefa_codificar.html`** - Formulário de codificação + Lista Mestra
3. **`bloco_assinatura_criar.html`** - Gestão do bloco (selecionar aprovadores)
4. **`tarefa_assinar.html`** - Interface de assinatura (aprovar/reprovar)
5. **`tarefa_publicar.html`** - Interface de publicação

---

## 🚀 Como Usar Agora

### 1. Aplicar Migration
```bash
python aplicar_migracao_ugq.py
```

### 2. Criar Usuários UGQ
```bash
# Se já existem usuários, delete e recrie:
# psql -d ged_db -c "DROP TABLE usuarios CASCADE; DROP TABLE documentos CASCADE; DROP TABLE tarefas CASCADE; DROP TABLE logs_ia CASCADE;"

python init_database.py
```

### 3. Testar Workflow Programaticamente (Python Shell)
```python
from app import create_app, db
from app.models import Usuario, Documento
from app.services.workflow import WorkflowUGQ

app = create_app()
with app.app_context():
    # ETAPA 0: Autor cria documento
    autor = Usuario.query.filter_by(email='usuario@example.com').first()
    documento = Documento(
        titulo='POP de Teste UGQ',
        tipo_documento='POP',
        setor='Operacoes',
        criador_id=autor.id,
        descricao='Teste do workflow UGQ'
    )
    db.session.add(documento)
    db.session.commit()

    # Submete para UGQ
    tarefa = WorkflowUGQ.autor_submete_documento(documento)
    print(f"✅ Tarefa criada: {tarefa.tipo_tarefa}")
    print(f"📊 Responsável: {tarefa.responsavel.nome}")

    # ETAPA 1: Triador aprova
    WorkflowUGQ.triador_aprova_triagem(tarefa)

    # E assim por diante...
```

---

## 📋 Checklist de Próximos Passos

### Imediato
- [ ] Criar rotas HTTP em `routes_view.py`
- [ ] Criar templates HTML
- [ ] Testar fluxo completo E2E via interface web

### Melhorias Futuras
- [ ] Adicionar validação de formulários
- [ ] Adicionar notificações por email
- [ ] Adicionar logs de auditoria mais detalhados
- [ ] Adicionar relatórios de workflow
- [ ] Adicionar dashboard específico da UGQ

---

## 🎯 Resumo

**Status Geral: 75% Completo**

✅ Backend completo e funcional (workflow, models, banco)
⚠️ Frontend pendente (rotas e templates)

O sistema já está **totalmente funcional via código Python**, mas precisa de **interfaces web** para uso prático.

---

**Última atualização:** 2025-01-13
**Commits realizados:** 3 (Migration+Models, Workflow, Init)
