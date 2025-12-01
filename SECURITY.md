# 🔒 GUIA DE SEGURANÇA - SISTEMA GED EBSERH

## ⚠️ CONFIGURAÇÃO OBRIGATÓRIA ANTES DE USAR

### 1. Variáveis de Ambiente

**NUNCA** use os valores padrão em produção! Configure:

```bash
# 1. Copie o template
cp .env.example .env

# 2. Gere SECRET_KEY
python -c 'import secrets; print(secrets.token_hex(32))'

# 3. Gere REDIS_PASSWORD
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# 4. Gere BACKUP_ENCRYPTION_KEY
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# 5. Configure senha do PostgreSQL (mínimo 32 caracteres)
# Use letras, números e símbolos

# 6. Preencha o arquivo .env com TODOS os valores
```

### 2. Checklist de Segurança

Antes de colocar em produção, verifique:

- [ ] SECRET_KEY com 64 caracteres hexadecimais
- [ ] DB_PASSWORD com 32+ caracteres
- [ ] REDIS_PASSWORD configurada
- [ ] BACKUP_ENCRYPTION_KEY gerada
- [ ] HTTPS configurado (certificado SSL/TLS válido)
- [ ] Firewall configurado (apenas portas 80, 443)
- [ ] Backups automáticos testados
- [ ] Logs sendo monitorados
- [ ] Rate limiting testado

### 3. Hardening do PostgreSQL

```sql
-- No servidor PostgreSQL
ALTER ROLE ged_user WITH PASSWORD 'SENHA_SUPER_SEGURA';
REVOKE ALL ON DATABASE ged_db FROM PUBLIC;
GRANT CONNECT ON DATABASE ged_db TO ged_user;
```

### 4. Hardening do Docker

```bash
# Não exponha portas desnecessárias
# docker-compose.yml - remova:
# ports:
#   - "5432:5432"  # PostgreSQL - NUNCA expor
#   - "6379:6379"  # Redis - NUNCA expor
```

### 5. Monitoramento

Configure alertas para:
- Tentativas de login falhadas (>5 em 5 min)
- Uso de disco >80%
- CPU >90% por >5 min
- Memória >90%
- Erros 500 em produção

### 6. Backup

- Backups criptografados diariamente às 3h
- Retenção: 30 dias
- Testar restore mensalmente
- Armazenar fora do servidor (S3, GCS, etc)

### 7. Atualizações

```bash
# Atualizar dependências mensalmente
pip list --outdated
pip install --upgrade <pacote>

# Atualizar imagens Docker
docker-compose pull
docker-compose up -d
```

### 8. Auditoria

Revisar logs semanalmente:
```bash
# Acessos suspeitos
grep "401\|403" logs/gunicorn_access.log | tail -100

# Erros de aplicação
grep "ERROR" logs/ged.log | tail -100

# Tentativas de SQL injection
grep -i "select\|union\|drop" logs/gunicorn_access.log
```

## 🚨 Em Caso de Incidente

1. **Isolar o sistema** (desconectar da rede)
2. **Trocar TODAS as senhas** imediatamente
3. **Revisar logs** das últimas 48h
4. **Notificar LGPD/DPO** se houver vazamento
5. **Restaurar do backup** mais recente
6. **Investigar causa raiz**

## 📞 Contatos de Emergência

- Segurança da Informação: [email]
- DPO/LGPD: [email]
- Suporte Técnico: [email]

---

**Última atualização:** 2025-12-01
**Responsável:** Equipe de Segurança GED
