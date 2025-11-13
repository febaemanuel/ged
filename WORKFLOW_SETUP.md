# 🔄 Configuração do Workflow Automático - Sistema GED

## 📋 Visão Geral

Este documento descreve como configurar o **Workflow Automático de Aprovação** seguindo o padrão EBSERH.

---

## 🚀 Passo a Passo de Instalação

### **1. Configurar Banco de Dados PostgreSQL**

Certifique-se que o PostgreSQL está rodando e crie o banco:

```bash
# Conecte no PostgreSQL
psql -U postgres

# Crie o usuário
CREATE USER ged_user WITH PASSWORD 'ged_password';

# Crie o banco
CREATE DATABASE ged_db OWNER ged_user;

# Defina encoding UTF-8
ALTER DATABASE ged_db SET client_encoding TO 'UTF8';

# Saia
\q
```

### **2. Configurar Variáveis de Ambiente**

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o `.env` e configure:

```env
# Banco de Dados
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db?client_encoding=utf8

# API DeepSeek (IA)
AI_API_BASE_URL=https://api.deepseek.com
AI_API_KEY=sk-sua-chave-aqui
AI_API_MODEL=deepseek-chat
AI_API_TIMEOUT=30

# Flask
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development
```

### **3. Instalar Dependências Python**

```bash
pip install -r requirements.txt
```

### **4. Inicializar Banco de Dados**

Este comando cria **todas as tabelas** e **10 usuários** prontos para testar o workflow:

```bash
python init_database.py
```

**Usuários criados:**
- 1 Administrador
- 3 Gerentes (Produção, Qualidade, Operações)
- 3 Responsáveis Internos (Validadores)
- 3 Usuários Comuns (Autores)

### **5. Aplicar Migração do Workflow**

Este comando adiciona o campo `chefia_imediata_id` necessário para o workflow:

```bash
python aplicar_migracao.py
```

### **6. Iniciar o Servidor**

```bash
python run.py
```

Acesse: **http://localhost:5000**

---

## 👥 Usuários Criados

### 🔴 **ADMINISTRADOR** (Gestão Documental - Publica)
```
Email: admin@example.com
Senha: admin123
Papel: Publica documentos após aprovação final
```

### 🔵 **GERENTES** (Chefia Imediata + Aprovador Final)
```
maria.silva@example.com / gerente123 (Produção)
joao.santos@example.com / gerente123 (Qualidade)
carlos.mendes@example.com / gerente123 (Operações)

Papel:
- Análise inicial como Chefia Imediata
- Aprovação final como Superintendência
```

### 🟢 **RESPONSÁVEIS INTERNOS** (Validadores Técnicos)
```
ana.costa@example.com / resp123 (Qualidade)
  → Valida PADRONIZAÇÃO (formatação, templates, logos)

pedro.oliveira@example.com / resp123 (Produção)
  → Valida CONTEÚDO TÉCNICO de documentos da Produção

lucia.ferreira@example.com / resp123 (Operações)
  → Valida CONTEÚDO TÉCNICO de documentos de Operações
```

### ⚪ **USUÁRIOS COMUNS** (Autores)
```
rafael.alves@example.com / usuario123 (Produção)
fernanda.lima@example.com / usuario123 (Operações)
usuario@example.com / usuario123 (Operações - Padrão)

Papel: Criam documentos e selecionam Chefia Imediata
```

---

## 📋 Fluxo Automático (5 Etapas)

```
1. AUTOR (Usuário Comum)
   ├─ Cria documento
   ├─ Seleciona Chefia Imediata
   └─ ✅ Sistema cria tarefa "Analisar"
          ⬇️

2. CHEFIA IMEDIATA (Gerente)
   ├─ Analisa pertinência
   ├─ Aprova/Reprova
   └─ ✅ Se aprovado → Cria "Validar Conteúdo"
          ⬇️

3. ESPECIALISTA (Responsável Interno)
   ├─ Valida conteúdo técnico
   ├─ Aprova/Reprova
   └─ ✅ Se aprovado → Cria "Validar Padronização"
          ⬇️

4. QUALIDADE (Responsável Interno - Qualidade)
   ├─ Valida formatação
   ├─ Aprova/Reprova
   └─ ✅ Se aprovado → Cria "Aprovar"
          ⬇️

5. APROVADOR (Gerente Superior)
   ├─ Aprovação final
   ├─ Aprova/Reprova
   └─ ✅ Se aprovado → Cria "Publicar"
          ⬇️

6. ADMIN (Gestão Documental)
   ├─ Faz upload do PDF final
   ├─ Publica documento
   └─ ✅ Código definitivo gerado!
```

---

## 🧪 Testando o Fluxo Completo

### **Cenário 1: Fluxo Completo com Sucesso**

1. **Login como `rafael.alves@example.com`** (Usuário Comum - Produção)
   - Acesse `/documento/criar`
   - Preencha os dados
   - Selecione **Maria Silva** como Chefia Imediata
   - Faça upload de um arquivo PDF
   - Clique "Criar Documento"
   - ✅ Tarefa "Analisar" criada para Maria

2. **Logout e Login como `maria.silva@example.com`** (Gerente - Produção)
   - Acesse "Minhas Tarefas"
   - Veja tarefa "Analisar"
   - Escreva parecer: "Documento pertinente"
   - Marque: ✅ Aprovado
   - ✅ Tarefa "Validar Conteúdo" criada para Pedro (Resp. Interno - Produção)

3. **Logout e Login como `pedro.oliveira@example.com`** (Resp. Interno - Produção)
   - Acesse "Minhas Tarefas"
   - Veja tarefa "Validar Conteúdo"
   - Escreva parecer: "Conteúdo técnico correto"
   - Marque: ✅ Aprovado
   - ✅ Tarefa "Validar Padronização" criada para Ana (Resp. Interno - Qualidade)

4. **Logout e Login como `ana.costa@example.com`** (Resp. Interno - Qualidade)
   - Acesse "Minhas Tarefas"
   - Veja tarefa "Validar Padronização"
   - Escreva parecer: "Formatação conforme padrão"
   - Marque: ✅ Aprovado
   - ✅ Tarefa "Aprovar" criada para Maria (Gerente - Aprovador Final)

5. **Logout e Login como `maria.silva@example.com`** (Gerente - Aprovador)
   - Acesse "Minhas Tarefas"
   - Veja tarefa "Aprovar"
   - Revise todo o histórico de aprovações
   - Escreva parecer: "Aprovado para publicação"
   - Marque: ✅ Aprovado
   - ✅ Tarefa "Publicar" criada para Admin

6. **Logout e Login como `admin@example.com`** (Administrador)
   - Acesse "Minhas Tarefas"
   - Veja tarefa "Publicar"
   - Faça upload do PDF final
   - Clique "Concluir Publicação"
   - ✅ **DOCUMENTO PUBLICADO!**
   - Código definitivo gerado (ex: POP-PROD-001-2025)

### **Cenário 2: Reprovação e Correção**

1. Login como `rafael.alves@example.com` (Usuário Comum)
   - Cria documento com erro proposital

2. Login como `maria.silva@example.com` (Gerente)
   - Vê tarefa "Analisar"
   - Escreve parecer: "Falta descrição detalhada"
   - Marque: ❌ Reprovado
   - ✅ Tarefa "Realizar Correção" criada para Rafael (Autor)

3. Login como `rafael.alves@example.com` (Usuário)
   - Vê tarefa "Realizar Correção"
   - Lê parecer da Maria
   - Faz as correções necessárias
   - Reenvia documento
   - ✅ Fluxo reinicia do começo

---

## 🔧 Estrutura Técnica

### **Arquivos Principais**

```
app/
├── services/
│   └── workflow.py           # Lógica do workflow automático
├── routes/
│   ├── routes_view.py        # Criação de documentos + workflow
│   └── routes_tarefa.py      # Conclusão de tarefas + workflow
├── models/
│   └── models.py             # Campo chefia_imediata_id
└── templates/
    └── documento_criar.html  # Dropdown de seleção de chefia

migrations/
└── add_chefia_imediata_workflow.sql  # Migração do banco

config.py                     # TIPOS_TAREFA configurados
init_database.py              # Cria 10 usuários
aplicar_migracao.py           # Aplica migração
```

### **Tabelas do Banco**

```sql
-- Tabela documentos (modificada)
documentos
  ├── chefia_imediata_id → usuarios.id  (NOVO)
  ├── criador_id → usuarios.id
  └── status (Novo, Em Análise, Aprovado, Publicado)

-- Tabela tarefas
tarefas
  ├── tipo_tarefa (Analisar, Validar Conteúdo, etc)
  ├── responsavel_id → usuarios.id
  ├── criador_id → usuarios.id
  ├── aprovado (true/false/null)
  └── parecer (texto)
```

---

## ❓ FAQ

### **P: O que acontece se eu não tiver Responsável Interno no setor?**
R: O sistema busca qualquer Responsável Interno disponível de outro setor.

### **P: Posso pular etapas do workflow?**
R: Não. O fluxo é obrigatório e sequencial seguindo padrão EBSERH.

### **P: E se eu reprovar um documento?**
R: O sistema cria automaticamente uma tarefa "Realizar Correção" para o autor original.

### **P: Preciso criar tarefas manualmente?**
R: Não! O workflow cria automaticamente quando você conclui uma tarefa com aprovação.

### **P: Como sei em que etapa está o documento?**
R: Veja o campo "Status" do documento e a timeline de tarefas na página de detalhes.

### **P: Posso ter mais de uma Chefia Imediata?**
R: Não. O autor seleciona UMA chefia que fará a análise inicial.

---

## 🎯 Próximos Passos

Após configurar tudo:

1. ✅ Teste o fluxo completo
2. ✅ Crie novos usuários conforme necessário
3. ✅ Configure notificações por email (opcional)
4. ✅ Ajuste prazos no `workflow.py` se necessário
5. ✅ Personalize setores conforme sua organização

---

## 📧 Suporte

Se encontrar problemas:

1. Verifique se todas as migrações foram aplicadas
2. Verifique se há usuários com perfil `responsavel_interno`
3. Verifique os logs do Flask
4. Verifique se o campo `chefia_imediata_id` existe na tabela `documentos`

---

**Sistema pronto para produção!** 🚀
