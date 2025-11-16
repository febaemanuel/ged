# 🚀 Instalação Rápida - Novas Funcionalidades

## ⚠️ IMPORTANTE: Criar/Atualizar Banco de Dados

As novas funcionalidades adicionaram 2 novas tabelas ao banco de dados:
- `templates_documento`
- `comentarios`

### Opção 1: Criar Banco do Zero (Recomendado para desenvolvimento)

```bash
# Ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Crie o banco de dados completo
python init_database.py
```

Isso vai:
- Criar todas as tabelas (incluindo as novas)
- Criar 12 usuários de teste com diferentes perfis
- Configurar dados iniciais

### Opção 2: Apenas Adicionar Novas Tabelas (Se já tem banco)

```python
python
>>> from app import create_app
>>> from app.models import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     print("✅ Tabelas criadas!")
>>> exit()
```

---

## 🎯 Como Testar as Novas Funcionalidades

### 1. **Dashboard Executivo**

**Acesso:**
- Login como: `admin@ged.com` ou `validador@ged.com` (senha: `senha123`)
- Menu: **Gestão** → **Dashboard Executivo**

**O que testar:**
- ✅ Clique nos cards de métricas
- ✅ Veja modais com documentos filtrados
- ✅ Teste filtros de 30/60/90 dias para documentos vencendo
- ✅ Verifique documentos vencidos
- ✅ Clique em "Documentos por Tipo" (POP, Manual, Protocolo)

**URL direta:** `http://localhost:5000/dashboard-executivo`

---

### 2. **Templates de Documentos**

**Acesso:**
- Login como: `admin@ged.com` ou `validador@ged.com`
- Menu: **Gestão** → **Templates**

**Como criar um template:**
1. Clique em "Novo Template"
2. Preencha:
   - Nome: "Template POP Padrão EBSERH"
   - Tipo: POP
   - Descrição: "Template padrão com formatação EBSERH"
   - Setor: (deixe vazio para global)
   - Arquivo: Faça upload de um .docx formatado
3. Clique "Criar Template"

**Como usar o template:**
1. Vá em **Documentos** → **Novo Documento**
2. Selecione o tipo (POP)
3. Aparecerá o seletor de templates
4. Escolha um template da lista
5. O arquivo do template será usado automaticamente

**URL direta:** `http://localhost:5000/templates-admin`

---

### 3. **Sistema de Comentários**

**Acesso:**
- Abra qualquer documento: **Documentos** → clique em qualquer documento

**Como usar:**
1. Role até a seção "Comentários e Discussões"
2. Digite um comentário
3. Use `@email@dominio.com` para mencionar alguém
4. Clique "Enviar Comentário"
5. Teste responder a comentários existentes

**Recursos:**
- ✅ Threads de respostas
- ✅ @Menções com notificações
- ✅ Editar/deletar seus comentários
- ✅ Comentários por seção do documento

---

## 📊 Endpoints da API

### Templates
```bash
# Listar templates
GET http://localhost:5000/template/lista

# Criar template
POST http://localhost:5000/template/criar
Content-Type: multipart/form-data
Body: nome, tipo_documento, descricao, setor, arquivo

# Baixar template
GET http://localhost:5000/template/download/<id>

# Editar template
PUT http://localhost:5000/template/<id>
Content-Type: application/json
Body: {"nome": "...", "descricao": "...", "ativo": true}

# Deletar template
DELETE http://localhost:5000/template/<id>
```

### Comentários
```bash
# Listar comentários de um documento
GET http://localhost:5000/comentario/documento/<doc_id>

# Criar comentário
POST http://localhost:5000/comentario/criar
Content-Type: application/json
Body: {"documento_id": 1, "texto": "Ótimo! @admin@ged.com", "secao": "Introdução"}

# Responder comentário
POST http://localhost:5000/comentario/<id>/responder
Content-Type: application/json
Body: {"texto": "Concordo!"}

# Editar comentário
PUT http://localhost:5000/comentario/<id>
Content-Type: application/json
Body: {"texto": "Texto editado"}

# Deletar comentário
DELETE http://localhost:5000/comentario/<id>
```

### Dashboard Executivo
```bash
# Estatísticas gerais
GET http://localhost:5000/dashboard-executivo/estatisticas

# Documentos por tipo
GET http://localhost:5000/dashboard-executivo/documentos-por-tipo

# Documentos vencidos
GET http://localhost:5000/dashboard-executivo/documentos-vencidos

# Documentos vencendo (30/60/90 dias)
GET http://localhost:5000/dashboard-executivo/documentos-vencendo?dias=30

# Documentos por status
GET http://localhost:5000/dashboard-executivo/documentos-por-status

# Resumo de tarefas
GET http://localhost:5000/dashboard-executivo/tarefas-resumo

# Timeline de criação (12 meses)
GET http://localhost:5000/dashboard-executivo/timeline-criacao

# Usuários ativos
GET http://localhost:5000/dashboard-executivo/usuarios-ativos
```

---

## 🔐 Usuários de Teste

Após rodar `init_database.py`, você terá estes usuários:

| Email | Senha | Perfil | O que pode fazer |
|-------|-------|--------|------------------|
| `admin@ged.com` | `senha123` | Administrador | Tudo |
| `validador@ged.com` | `senha123` | Validador UGQ | Dashboard Executivo, Templates |
| `triador@ged.com` | `senha123` | Triador UGQ | Triagem de documentos |
| `gerente@ged.com` | `senha123` | Gerente | Aprovar documentos |
| `usuario@ged.com` | `senha123` | Comum | Criar documentos, comentar |

---

## 🐛 Solução de Problemas

### Erro: "cannot import name 'TemplateDocumento'"
**Solução:** Certifique-se de que está com o código mais recente:
```bash
git pull origin claude/brainstorm-app-features-01YMPgLNsa4NhweUsxaZShAw
```

### Erro: "Table doesn't exist"
**Solução:** Recrie o banco de dados:
```bash
python init_database.py
```

### Templates não aparecem na criação de documentos
**Solução:**
1. Crie pelo menos 1 template em `/templates-admin`
2. Certifique-se de que o template está marcado como "Ativo"
3. Verifique se o tipo do template corresponde ao tipo do documento

### Comentários não carregam
**Solução:**
1. Abra o console do navegador (F12)
2. Verifique se há erros de JavaScript
3. Certifique-se de que a tabela `comentarios` foi criada

### Dashboard Executivo mostra "-" em tudo
**Solução:**
1. Crie alguns documentos de teste
2. Adicione tarefas e prazos
3. Aguarde alguns segundos para o carregamento das estatísticas

---

## 📝 Checklist de Verificação

Após instalação, verifique:

- [ ] Banco de dados criado com sucesso
- [ ] Login funciona com `admin@ged.com`
- [ ] Menu "Gestão" aparece no navbar
- [ ] Dashboard Executivo abre e mostra cards
- [ ] Clicar nos cards abre modais
- [ ] Página de Templates abre
- [ ] Consegue criar um template
- [ ] Template aparece na criação de documentos
- [ ] Comentários aparecem na página de documento
- [ ] Consegue criar e responder comentários
- [ ] @Menções funcionam

---

## 🚀 Iniciar o Servidor

```bash
# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Inicie o servidor
python app.py

# Acesse no navegador
http://localhost:5000
```

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `NOVAS_FUNCIONALIDADES.md` - Descrição completa das funcionalidades
- `README.md` - Documentação geral do sistema
- `WORKFLOW_SETUP.md` - Configuração do workflow UGQ

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs em `logs/ged.log`
2. Consulte a documentação
3. Abra uma issue no repositório

---

**Última atualização:** 2025-11-16
**Versão:** 2.0 - Novas Funcionalidades Implementadas ✅
