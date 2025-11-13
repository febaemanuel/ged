# 🚀 COMECE AQUI - Sistema GED

## ⚡ Instalação Express (5 minutos)

### Passo 1: Instalar Requisitos
```bash
# Python 3.11+ e PostgreSQL devem estar instalados
python3 --version  # Deve mostrar 3.11 ou superior
psql --version     # Deve mostrar PostgreSQL instalado
```

**Não tem?** Veja [INSTALACAO_COMPLETA.md](INSTALACAO_COMPLETA.md) seção "PRÉ-REQUISITOS"

### Passo 2: Configurar Banco de Dados
```bash
# Entre no PostgreSQL
sudo -u postgres psql

# Execute estes 3 comandos:
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q
```

### Passo 3: Setup Automático
```bash
# Execute o script de setup
./setup.sh

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# Inicialize o banco
flask init-db
flask seed-db
```

### Passo 4: Executar
```bash
python app.py
```

✅ **PRONTO!** Acesse: http://localhost:5000/home

---

## 🔑 Credenciais de Acesso

| Perfil | Email | Senha |
|--------|-------|-------|
| **Administrador** | admin@example.com | admin123 |
| Gerente | gerente@example.com | gerente123 |
| Usuário | usuario@example.com | usuario123 |

---

## 🧪 Testar Rapidamente

```bash
# Teste automático
python test_api.py

# Ou teste manual com cURL
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","senha":"admin123"}'
```

---

## 📚 Documentação

- **INSTALACAO_COMPLETA.md** ← Guia passo a passo detalhado com troubleshooting
- **README.md** ← Documentação completa da API
- **QUICKSTART.md** ← Referência rápida de comandos
- **http://localhost:5000/home** ← Documentação web

---

## ✅ Verificar Instalação

```bash
./verificar_instalacao.sh
```

Este script verifica:
- ✅ Python 3.11+
- ✅ PostgreSQL rodando
- ✅ Dependências instaladas
- ✅ Banco configurado
- ✅ Arquivos do projeto

---

## 🆘 Problemas?

### Erro: "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "could not connect to database"
```bash
# PostgreSQL não está rodando
sudo systemctl start postgresql  # Linux
brew services start postgresql   # Mac
```

### Erro: "Port 5000 already in use"
```bash
# Matar processo na porta 5000
lsof -ti:5000 | xargs kill -9
```

**Mais problemas?** Consulte [INSTALACAO_COMPLETA.md](INSTALACAO_COMPLETA.md) seção "SOLUÇÃO DE PROBLEMAS"

---

## 📊 Próximos Passos

1. **Criar documento teste:**
   ```bash
   curl -X POST http://localhost:5000/documento/criar \
     -b cookies.txt \
     -F "titulo=Meu Primeiro POP" \
     -F "tipo_documento=POP" \
     -F "setor=TI" \
     -F "arquivo=@documento.txt"
   ```

2. **Gerar relatório PDF:**
   ```bash
   curl -X GET http://localhost:5000/relatorio/pdf/geral \
     -b cookies.txt \
     --output relatorio.pdf
   ```

3. **Importar Postman Collection:**
   - Abra Postman
   - Importe `GED_API.postman_collection.json`
   - Teste todos os endpoints visualmente

---

## 🎯 Funcionalidades Principais

✅ **Gerenciamento de Documentos** - POPs, Manuais, Protocolos
✅ **Fluxo de Aprovação** - Tarefas com prazos e pareceres
✅ **Integração com IA** - Extração, classificação, busca semântica
✅ **Relatórios PDF** - Tarefas, vencimentos, geral
✅ **4 Perfis de Usuário** - Comum, Gerente, Responsável, Admin
✅ **API REST Completa** - 40+ endpoints documentados

---

## 📖 Endpoints Mais Usados

```bash
# Autenticação
POST /auth/login
GET /auth/me

# Documentos
GET /documento/lista
POST /documento/criar
GET /documento/<id>
GET /documento/publico

# Tarefas
GET /tarefa/minhas
POST /tarefa/criar
POST /tarefa/<id>/concluir

# IA
POST /ia/extract/<id>
POST /ia/classify/<id>
POST /ia/search

# Relatórios
GET /relatorio/pdf/tarefas_atrasadas
GET /relatorio/pdf/geral
```

**Lista completa:** http://localhost:5000/home

---

## 💡 Dicas

- Use **Postman** para testar endpoints visualmente
- Consulte **logs/ged.log** para debugging
- Use `flask shell` para queries SQL diretas
- Configure **rotina automática** para `flask verificar-vencimentos`

---

## 🎉 Sistema 100% Funcional!

**26 arquivos** | **5.298+ linhas de código** | **Python 3.11+** | **Flask 3.0** | **PostgreSQL**

Desenvolvido com arquitetura modular, código documentado, testes automatizados e pronto para produção.

---

**Precisa de ajuda?** Consulte [INSTALACAO_COMPLETA.md](INSTALACAO_COMPLETA.md) para instruções detalhadas.
