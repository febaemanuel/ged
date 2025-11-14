# DETALHES DOS ARQUIVOS CRÍTICOS

## Mapa Rápido do Código

### 1. app/models/models.py

#### Modelos UGQ
| Modelo | Linhas | Descrição |
|--------|--------|-----------|
| ListaMestra | 346-369 | Controle de códigos definitivos |
| BlocoAssinatura | 372-422 | Bloco para assinatura, com métodos de validação |
| ItemBlocoAssinatura | 424-457 | Item do bloco, representa cada aprovador |
| ValidacaoUGQ | 460-480 | Registro de validação técnica |

#### Métodos Importantes de BlocoAssinatura
```python
total_aprovadores()        # Retorna total de aprovadores
aprovadores_aprovaram()    # Retorna quantos aprovaram
aprovadores_pendentes()    # Retorna pendentes
todos_aprovaram()          # Verifica se todos aprovaram
algum_reprovou()          # Verifica se alguém reprovou
```

---

### 2. app/services/workflow.py

#### Classe WorkflowUGQ - Métodos Implementados

```python
class WorkflowUGQ:
    # ETAPA 0
    @classmethod
    def autor_submete_documento(cls, documento)
    
    # ETAPA 1
    @classmethod
    def triador_devolve_ao_autor(cls, tarefa, motivo)
    
    @classmethod
    def triador_aprova_triagem(cls, tarefa)
    
    # ETAPA 2
    @classmethod
    def gerar_proximo_codigo(cls, tipo, setor)
    
    @classmethod
    def validador_codifica_documento(cls, tarefa, codigo_definitivo, versao, observacoes)
    
    # ETAPA 3
    @classmethod
    def validador_cria_bloco_assinatura(cls, documento, validador_id, aprovadores_ids, modo, observacoes)
    
    @classmethod
    def aprovador_assina(cls, tarefa, aprovado, parecer)
    
    @classmethod
    def _finalizar_bloco_assinatura(cls, bloco, documento)
    
    # ETAPA 4
    @classmethod
    def validador_publica_documento(cls, tarefa)
```

---

### 3. app/routes/routes_view.py

#### Rotas UGQ Implementadas

```python
# ETAPA 1: Triagem
@view_bp.route('/tarefa/<int:tarefa_id>/concluir_triagem', methods=['POST'])
def concluir_triagem(tarefa_id):
    """Triador UGQ conclui triagem (3 checkpoints)"""
    # Checkpoint 1: Documento já existe?
    # Checkpoint 2: Manual validado pelo Colegiado?
    # Checkpoint 3: Formatação OK?
    
    # ETAPA 2: Codificação
@view_bp.route('/tarefa/<int:tarefa_id>/codificar', methods=['GET', 'POST'])
def codificar_documento(tarefa_id):
    """Validador UGQ codifica documento e cria ListaMestra"""
    # GET: Sugere código
    # POST: Processa, cria ListaMestra e ValidacaoUGQ
    
# ETAPA 3a: Criar Bloco
@view_bp.route('/documento/<int:documento_id>/bloco_assinatura/criar', methods=['GET', 'POST'])
def criar_bloco_assinatura(documento_id):
    """Validador UGQ cria bloco com aprovadores"""
    # GET: Lista aprovadores
    # POST: Cria bloco, adiciona aprovadores, cria tarefas
    
# ETAPA 3b: Assinar
@view_bp.route('/tarefa/<int:tarefa_id>/assinar', methods=['POST'])
def assinar_documento(tarefa_id):
    """Aprovador assina e aprova/reprova"""
    # Modo sequencial: próximo aprovador
    # Modo concomitante: verifica se todos aprovaram
    
# ETAPA 4: Publicação
@view_bp.route('/tarefa/<int:tarefa_id>/publicar', methods=['POST'])
def publicar_documento(tarefa_id):
    """Validador UGQ publica documento (VIGENTE)"""
    # Atualiza ListaMestra
    # Arquiva versão anterior
```

---

### 4. app/templates/tarefa_detalhe.html

#### Formulários por Tipo de Tarefa

| Linhas | Tipo de Tarefa | Etapa | Formulário |
|--------|---|---|---|
| 100-192 | "Documento Recebido" | 1 | Triagem (3 checkpoints) |
| 195-228 | modo=='codificar' | 2 | Codificação |
| 231-255 | "Assinar Documento" | 3 | Assinatura |
| 258-284 | "Publicar Documento Aprovado" | 4 | Publicação |
| 287-331 | Outros (antigos) | N/A | Workflow Antigo |

---

### 5. app/templates/documento_detalhe.html

#### Seção de Bloco de Assinatura

| Linhas | Conteúdo |
|--------|----------|
| 307-395 | Seção "Criar Bloco de Assinatura" |
| 317 | Formulário POST para criar_bloco_assinatura |
| 318-343 | Seleção de modo (sequencial/concomitante) |
| 346-375 | Lista dinâmica de aprovadores (JavaScript) |
| 372-374 | Botão para adicionar aprovador |
| 397-440 | Funções JavaScript (adicionarAprovador, removerAprovador) |

---

### 6. config.py

#### Perfis UGQ

```python
PERFIL_QUALIDADE_TRIADOR = 'qualidade_triador'        # linha 75
PERFIL_QUALIDADE_VALIDADOR = 'qualidade_validador'    # linha 76
```

#### Status de Documentos UGQ

```python
STATUS_EM_TRIAGEM = 'Em Triagem'            # linha 90
STATUS_EM_VALIDACAO = 'Em Validação'        # linha 91
STATUS_EM_CORRECAO = 'Em Correção'          # linha 92
STATUS_VALIDADO = 'Validado'                # linha 93
STATUS_EM_APROVACAO = 'Em Aprovação'        # linha 94
STATUS_EM_AJUSTES = 'Em Ajustes'            # linha 95
STATUS_PUBLICADO = 'Publicado'              # linha 97
STATUS_VIGENTE = 'Vigente'                  # linha 100
```

#### Tipos de Tarefas UGQ

```python
TAREFA_DOCUMENTO_RECEBIDO = 'Documento Recebido'                   # linha 111
TAREFA_TRIAGEM = 'Triagem de Documento'                            # linha 114
TAREFA_VALIDAR_CODIFICAR = 'Validar e Codificar Documento'        # linha 117
TAREFA_GESTAO_BLOCO = 'Gestão do Bloco de Assinatura'             # linha 120
TAREFA_ASSINAR = 'Assinar Documento'                               # linha 121
TAREFA_PUBLICAR_APROVADO = 'Publicar Documento Aprovado'          # linha 124
TAREFA_REALIZAR_CORRECAO = 'Realizar Correção'                    # linha 127
TAREFA_REALIZAR_AJUSTES = 'Realizar Ajustes'                      # linha 128
```

---

### 7. app/__init__.py

#### Blueprints Registrados

```python
from app.routes import (
    auth_bp,           # Autenticação
    documento_bp,      # Documentos (API)
    tarefa_bp,        # Tarefas (API)
    ia_bp,            # Inteligência Artificial
    dashboard_bp,     # Dashboard (API)
    view_bp,          # Views HTML (UGQ aqui!)
    busca_bp          # Busca
)

app.register_blueprint(auth_bp)
app.register_blueprint(documento_bp)
app.register_blueprint(tarefa_bp)
app.register_blueprint(ia_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(view_bp)          # ← view_bp do UGQ
app.register_blueprint(busca_bp)
```

---

## ❌ ARQUIVO COM PROBLEMA

### app/routes/routes_tarefa.py

**Problema**: Importa WorkflowGED que não existe

```python
# Linha 288
from app.services.workflow import WorkflowGED  # ❌ ERRO!

# Linha 290
proxima_tarefa = WorkflowGED.proximo_passo(tarefa)  # ❌ ERRO!
```

**Localização exata**:
- Função: `tarefa_finalizar()` 
- Linhas: 287-302

**Afeta**: Apenas workflow antigo (deprecated)

---

### app/routes/routes_view.py

**Problema**: Importa WorkflowGED que não existe

```python
# Linha 629
from app.services.workflow import WorkflowGED  # ❌ ERRO!

# Linha 632
proxima_tarefa = WorkflowGED.proximo_passo(tarefa)  # ❌ ERRO!
```

**Localização exata**:
- Função: `tarefa_concluir()`
- Linhas: 627-643

**Afeta**: Apenas workflow antigo (deprecated)

---

## FLUXO VISUAL DO WORKFLOW UGQ

```
ETAPA 0: AUTOR
├─ Cria documento
└─ WorkflowUGQ.autor_submete_documento()
   └─ Cria tarefa "Documento Recebido" para Triador

ETAPA 1: TRIADOR UGQ
├─ Recebe tarefa "Documento Recebido"
├─ Verifica 3 checkpoints:
│  ├─ CP1: Documento já existe na Lista Mestra?
│  ├─ CP2: Manual validado pelo Colegiado? (só se Manual)
│  └─ CP3: Formatação OK?
├─ Se REPROVA algum checkpoint:
│  └─ WorkflowUGQ.triador_devolve_ao_autor()
│     └─ Cria tarefa "Realizar Correção" para Autor
└─ Se APROVA tudo:
   └─ WorkflowUGQ.triador_aprova_triagem()
      └─ Cria tarefa "Validar e Codificar" para Validador

ETAPA 2: VALIDADOR UGQ (Codificação)
├─ Recebe tarefa "Validar e Codificar"
├─ WorkflowUGQ.gerar_proximo_codigo()
│  └─ Sugere código: TIPO.SETOR-NNN
├─ WorkflowUGQ.validador_codifica_documento()
│  ├─ Cria ListaMestra com código definitivo
│  ├─ Cria ValidacaoUGQ com dados de validação
│  └─ Atualiza status: STATUS_VALIDADO
└─ Redirect para criar_bloco_assinatura

ETAPA 3a: VALIDADOR UGQ (Bloco de Assinatura)
├─ GET /documento/<id>/bloco_assinatura/criar
│  └─ Lista aprovadores disponíveis
└─ POST /documento/<id>/bloco_assinatura/criar
   ├─ Seleciona modo: sequencial ou concomitante
   ├─ Seleciona aprovadores (em ordem)
   └─ WorkflowUGQ.validador_cria_bloco_assinatura()
      ├─ Cria BlocoAssinatura
      ├─ Adiciona ItemBlocoAssinatura para cada aprovador
      ├─ Se SEQUENCIAL: cria tarefa apenas para 1º aprovador
      ├─ Se CONCOMITANTE: cria tarefa para todos
      └─ Atualiza status: STATUS_EM_APROVACAO

ETAPA 3b: APROVADORES (Assinatura)
├─ Recebem tarefa "Assinar Documento [Bloco #N]"
└─ POST /tarefa/<id>/assinar
   └─ WorkflowUGQ.aprovador_assina()
      ├─ Se REPOVA:
      │  ├─ Cancela bloco
      │  ├─ Atualiza status: STATUS_EM_AJUSTES
      │  └─ Cria tarefa "Realizar Ajustes" para Validador
      └─ Se APROVA:
         ├─ Se SEQUENCIAL:
         │  ├─ Se há próximo aprovador:
         │  │  └─ Cria tarefa para próximo
         │  └─ Se é último:
         │     └─ Finaliza bloco
         └─ Se CONCOMITANTE:
            ├─ Se todos aprovaram:
            │  └─ Finaliza bloco
            │     └─ WorkflowUGQ._finalizar_bloco_assinatura()
            │        ├─ Atualiza status: STATUS_APROVADO
            │        └─ Cria tarefa "Publicar Documento Aprovado"
            └─ Se ainda há pendentes:
               └─ Aguarda próximo aprovador

ETAPA 4: VALIDADOR UGQ (Publicação)
├─ Recebe tarefa "Publicar Documento Aprovado"
└─ POST /tarefa/<id>/publicar
   └─ WorkflowUGQ.validador_publica_documento()
      ├─ Atualiza status: STATUS_PUBLICADO
      ├─ Atualiza ListaMestra.status: VIGENTE
      ├─ Arquiva versão anterior (STATUS_OBSOLETO)
      └─ FIM DO WORKFLOW
```

---

## CHECKLIST DE TESTE DO WORKFLOW

Para testar o workflow UGQ completo, siga este checklist:

```
[ ] 1. Criar usuário com perfil 'qualidade_triador'
[ ] 2. Criar usuário com perfil 'qualidade_validador'
[ ] 3. Criar usuário com perfil 'gerente' (para aprovadores)
[ ] 4. Usuário comum cria documento
[ ] 5. Triador recebe tarefa "Documento Recebido"
    [ ] 5a. Triador verifica 3 checkpoints
    [ ] 5b. Triador aprova (todos checkpoints OK)
[ ] 6. Validador recebe tarefa "Validar e Codificar"
    [ ] 6a. Validador gera código
    [ ] 6b. Validador confirma codificação
[ ] 7. Página documento_detalhe mostra opção "Criar Bloco"
    [ ] 7a. Validador seleciona modo (sequencial/concomitante)
    [ ] 7b. Validador seleciona aprovadores
[ ] 8. Aprovadores recebem tarefas
    [ ] 8a. Aprovador 1 assina e aprova (sequencial)
    [ ] 8b. Aprovador 2 recebe tarefa
    [ ] 8c. Aprovador 2 assina e aprova
[ ] 9. Validador recebe tarefa "Publicar"
    [ ] 9a. Validador clica "Publicar Documento"
    [ ] 9b. Status muda para "Publicado"
    [ ] 9c. ListaMestra.status muda para "VIGENTE"
[ ] 10. Versão anterior está marcada como OBSOLETO
[ ] 11. Testar fluxo de reprovação
    [ ] 11a. Aprovador reprova
    [ ] 11b. Bloco volta para STATUS_EM_AJUSTES
    [ ] 11c. Validador recebe tarefa "Realizar Ajustes"
```

