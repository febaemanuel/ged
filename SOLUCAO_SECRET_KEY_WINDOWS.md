# ✅ Solução: Erro "SECRET_KEY não definida" no Windows

## 🎯 Solução Rápida (1 minuto)

Você está vendo este erro:
```
✗ Erro ao carregar configuração: SECRET_KEY não definida!
```

### Método 1: Automático (Recomendado) ⚡

**Execute no seu terminal (CMD ou PowerShell):**

```cmd
python criar_env.py
```

✅ **Pronto!** O script vai:
- Gerar uma `SECRET_KEY` segura automaticamente
- Criar o arquivo `.env` com todas as configurações
- Mostrar os próximos passos

### Método 2: Manual (Se o automático não funcionar) 🔧

**Passo 1**: Gere uma SECRET_KEY:

```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

**Resultado (exemplo)**:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Passo 2**: Copie o arquivo de exemplo:

**CMD:**
```cmd
copy .env.example .env
```

**PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Passo 3**: Edite o arquivo `.env` com o Bloco de Notas:

```cmd
notepad .env
```

**Passo 4**: Encontre a linha:
```env
SECRET_KEY=your-secret-key-change-in-production
```

**Passo 5**: Substitua por sua SECRET_KEY gerada no Passo 1:
```env
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Passo 6**: Salve e feche o arquivo (Ctrl+S)

---

## 🚀 Próximos Passos

Após criar o arquivo `.env`:

### 1. Configure o Banco de Dados

**No arquivo `.env`, localize a linha:**
```env
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db?client_encoding=utf8
```

**Ajuste as credenciais** do seu PostgreSQL (usuário, senha, etc)

### 2. Execute as Migrações

```cmd
python aplicar_migracao.py
```

### 3. Inicie a Aplicação

```cmd
python app.py
```

### 4. Acesse o Sistema

Abra seu navegador em: **http://127.0.0.1:5000**

---

## 🔧 Configurações Opcionais

Você pode configurar depois:

### WhatsApp (Evolution API)
Veja: `GUIA_EVOLUTION_API.md`

### E-mail SMTP
Edite no `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-aplicativo
```

### API de IA (DeepSeek)
Edite no `.env`:
```env
AI_API_KEY=sk-your-api-key-here
```

---

## ❌ Problemas Comuns

### "python: command not found"

**Solução**: Use `python3` ao invés de `python`:
```cmd
python3 criar_env.py
```

### "No module named 'secrets'"

**Causa**: Python muito antigo (< 3.6)

**Solução**: Atualize o Python para 3.8+:
https://www.python.org/downloads/

### "Acesso negado" ao criar .env

**Solução**: Execute como Administrador:
1. Clique com botão direito no CMD/PowerShell
2. Selecione "Executar como administrador"

### Arquivo .env não aparece no explorador

**Causa**: Windows oculta arquivos que começam com ponto

**Solução**: No Explorador de Arquivos:
1. Clique em "Exibir"
2. Marque "Itens ocultos"

---

## ✅ Verificação Rápida

Após criar o `.env`, verifique se funciona:

```cmd
python criar_env.py
```

**Saída esperada:**
```
⚠️  Arquivo .env já existe. Deseja sobrescrever? (s/N): n
❌ Operação cancelada
```

Se aparecer isso, seu `.env` está criado! ✅

---

## 🎯 Checklist Final

- [ ] Arquivo `.env` criado
- [ ] `SECRET_KEY` configurada (64 caracteres)
- [ ] `DATABASE_URL` configurada (PostgreSQL)
- [ ] PostgreSQL instalado e rodando
- [ ] Banco de dados `ged_db` criado
- [ ] Migrações executadas (`python aplicar_migracao.py`)
- [ ] Aplicação iniciando sem erros (`python app.py`)

---

## 📚 Documentação Completa

Para guia completo de instalação, veja:
- **`CONFIGURACAO_INICIAL.md`** - Guia completo de instalação
- **`GUIA_EVOLUTION_API.md`** - Setup do WhatsApp
- **`COMO_USAR_DIAGNOSTICO.md`** - Diagnóstico de problemas

---

## 🆘 Ainda com Problemas?

1. **Verifique se Python está instalado**:
   ```cmd
   python --version
   ```
   Deve mostrar: `Python 3.8.x` ou superior

2. **Verifique se está no diretório correto**:
   ```cmd
   dir
   ```
   Deve listar: `criar_env.py`, `.env.example`, `app.py`, etc

3. **Ative o ambiente virtual** (se estiver usando):
   ```cmd
   venv\Scripts\activate
   ```

4. **Execute o diagnóstico** após corrigir:
   ```cmd
   python diagnostico_evolution_v2_completo.py
   ```

---

**Última atualização**: 21/11/2024
**Plataforma**: Windows 10/11
**Python**: 3.8+
