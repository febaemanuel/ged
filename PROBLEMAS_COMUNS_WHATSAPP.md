# Problemas Comuns com WhatsApp - Evolution API v2

## 📋 Guia de Troubleshooting

Este documento lista os problemas mais comuns relacionados ao envio de mensagens via WhatsApp usando a Evolution API v2 e suas soluções.

---

## 🚨 Problema 1: Mensagens Não São Enviadas

### Sintomas
- Usuário não recebe mensagens
- Erro no log: "WhatsApp não configurado"
- Sistema não registra tentativa de envio

### Causas Possíveis

#### 1.1. WhatsApp Desativado no Sistema
**Verificar**: Acesse http://127.0.0.1:5000/admin/whatsapp

**Solução**:
1. Marque o checkbox "WhatsApp ATIVADO"
2. Clique em "Salvar Configurações"
3. Verifique se aparece a mensagem "Status: ATIVADO"

**Código para verificar**:
```bash
python3 diagnostico_evolution_v2_completo.py
```

#### 1.2. Credenciais Não Configuradas
**Verificar**: No painel admin, campos vazios ou incorretos

**Solução**:
1. Acesse http://127.0.0.1:5000/admin/whatsapp
2. Preencha:
   - **URL da Evolution API**: `http://IP:8080` (sem barra no final)
   - **Nome da Instância**: `principal12` (ou seu nome de instância)
   - **API Key**: Mesmo valor de `AUTHENTICATION_API_KEY` no `.env` da Evolution API
3. Clique em "Salvar Configurações"

**Validação**:
```bash
# No container da Evolution API
docker exec -it evolution_api cat .env | grep AUTHENTICATION_API_KEY

# Compare com o valor no banco do GED
```

#### 1.3. WhatsApp Não Conectado
**Verificar**: Status aparece como "Desconectado" (vermelho)

**Solução**:
1. Acesse http://127.0.0.1:5000/admin/whatsapp
2. Clique em "Obter QR Code"
3. Escaneie o QR Code com seu WhatsApp:
   - Abra WhatsApp no celular
   - Toque em "Dispositivos Vinculados"
   - Toque em "Vincular um Dispositivo"
   - Aponte a câmera para o QR Code
4. Aguarde a confirmação (status ficará verde)

**Troubleshooting**:
```bash
# Verifica se Evolution API está rodando
docker ps | grep evolution

# Vê logs da Evolution API
docker logs evolution_api --tail 50

# Testa conectividade
curl http://192.168.18.6:8080/
```

---

## 🚨 Problema 2: Erro HTTP 403 ao Criar Instância

### Sintomas
- Erro ao clicar em "Obter QR Code"
- Log mostra: "HTTP 403" ou "Access denied"

### Causas e Soluções

#### 2.1. API Key Incorreta
**Causa**: API Key no GED diferente da Evolution API

**Solução**:
```bash
# 1. Veja a API Key da Evolution API
docker exec -it evolution_api cat .env | grep AUTHENTICATION_API_KEY

# 2. Copie o valor EXATO (sem espaços)
# 3. Cole no campo "API Key" do painel admin do GED
# 4. Salve as configurações
```

#### 2.2. Instância Já Existe (403 Normal)
**Causa**: Evolution API retorna 403 quando instância já existe

**Identificação**: Mensagem contém "already in use" ou "já existe"

**Solução**: Isso é NORMAL e não é um erro. O sistema trata automaticamente.

**Código que trata isso** (`evolution_api_service_v2.py:196-203`):
```python
elif response.status_code == 403:
    # Verifica se o erro é por instância já existir
    response_text = response.text.lower()
    if "already in use" in response_text or "já existe" in response_text:
        logger.info(f"Instância já existe (403): {self.instance_name}")
        return True, "Instância já existe"
```

---

## 🚨 Problema 3: Erro de Conexão (Connection Refused)

### Sintomas
- Erro: "Não foi possível conectar em http://..."
- Timeout ao tentar enviar mensagem

### Causas e Soluções

#### 3.1. Evolution API Não Está Rodando
**Verificar**:
```bash
docker ps | grep evolution
```

**Solução**:
```bash
# Se não aparecer nada, inicie o container
cd /caminho/para/evolution-api
docker-compose up -d

# Aguarde 30 segundos e verifique
docker logs evolution_api
```

#### 3.2. URL Incorreta
**Verificar**: URL está com IP ou hostname correto?

**Soluções comuns**:
- ✅ `http://192.168.18.6:8080` (IP local na rede)
- ✅ `http://localhost:8080` (mesmo servidor)
- ✅ `http://evolution.meudominio.com` (domínio público)
- ❌ `http://192.168.18.6:8080/` (barra no final - REMOVER)
- ❌ `192.168.18.6:8080` (falta http://)

#### 3.3. Firewall Bloqueando
**Verificar**:
```bash
# Testa porta
telnet 192.168.18.6 8080

# Ou com curl
curl -v http://192.168.18.6:8080/
```

**Solução**:
```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

---

## 🚨 Problema 4: Mensagem Enviada mas Usuário Não Recebe

### Sintomas
- Log mostra "Mensagem enviada: message_id"
- Usuário não recebe a mensagem
- Status aparece como "enviado" no banco

### Causas e Soluções

#### 4.1. Número de Telefone Incorreto
**Verificar**: Formato do número no banco de dados

**Formatos aceitos**:
- ✅ `+5585999999999` (com código do país)
- ✅ `5585999999999` (sem +, será adicionado)
- ❌ `85999999999` (falta código do país)
- ❌ `(85) 99999-9999` (formatação incorreta)

**Código de formatação** (`evolution_api_service_v2.py:137-154`):
```python
def _format_number(self, numero: str) -> str:
    # Remove prefixos
    numero_limpo = numero.replace('whatsapp:', '').replace('+', '').strip()

    # Adiciona sufixo se não tiver
    if not numero_limpo.endswith('@s.whatsapp.net'):
        numero_limpo = f"{numero_limpo}@s.whatsapp.net"

    return numero_limpo
```

**Solução**:
```sql
-- Verifica números no banco
SELECT id, nome, telefone FROM usuarios WHERE telefone IS NOT NULL;

-- Corrige formato (exemplo: Brasil)
UPDATE usuarios
SET telefone = CONCAT('+55', SUBSTRING(telefone, 1, 11))
WHERE telefone NOT LIKE '+%' AND LENGTH(telefone) = 11;
```

#### 4.2. WhatsApp Não Está Instalado no Número
**Verificar**: O número realmente tem WhatsApp ativo?

**Solução**: Teste enviando manualmente pelo WhatsApp Web para o número

#### 4.3. Usuário Bloqueou o Número
**Verificar**: Usuário bloqueou seu número de WhatsApp?

**Solução**: Peça ao usuário para desbloquear ou use outro número

---

## 🚨 Problema 5: QR Code Não Aparece

### Sintomas
- Botão "Obter QR Code" não funciona
- Erro: "QR Code não disponível"
- Campo do QR Code fica vazio

### Causas e Soluções

#### 5.1. WhatsApp Já Conectado
**Verificar**: Status já está verde?

**Solução**: Não precisa de QR Code! O WhatsApp já está conectado.

#### 5.2. Resposta da API Não Contém QR Code
**Verificar logs**:
```bash
# No GED
tail -f logs/app.log | grep -i qrcode

# Na Evolution API
docker logs evolution_api --tail 50 | grep -i qrcode
```

**Solução**: Aguarde 30 segundos e tente novamente. O QR Code expira rapidamente.

#### 5.3. Instância em Estado Inválido
**Solução**:
```bash
# Deleta e recria a instância
curl -X DELETE \
  http://192.168.18.6:8080/instance/delete/principal12 \
  -H 'apikey: SUA_API_KEY'

# Aguarde 5 segundos e tente obter QR Code novamente
```

---

## 🚨 Problema 6: Timeout ao Enviar Mensagem

### Sintomas
- Erro: "Timeout ao conectar (30s)"
- Mensagem demora muito e falha

### Causas e Soluções

#### 6.1. Evolution API Lenta
**Verificar**:
```bash
# Vê uso de CPU e memória
docker stats evolution_api
```

**Solução**:
```bash
# Reinicia o container
docker restart evolution_api

# Aguarde 30 segundos
sleep 30

# Verifica se voltou
docker logs evolution_api --tail 20
```

#### 6.2. Banco de Dados PostgreSQL Lento
**Verificar**:
```bash
# Vê conexões ativas
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

**Solução**:
```bash
# Reinicia PostgreSQL
sudo service postgresql restart
```

#### 6.3. Rede Lenta
**Verificar**:
```bash
# Testa latência
ping -c 5 192.168.18.6
```

**Solução**: Verifique sua conexão de rede ou aumente o timeout no código

---

## 🚨 Problema 7: Webhook Não Recebe Mensagens

### Sintomas
- Usuário envia mensagem pelo WhatsApp
- Sistema não recebe/processa
- Chatbot não responde

### Causas e Soluções

#### 7.1. Webhook Não Configurado na Evolution API
**Verificar**:
```bash
curl -X GET \
  http://192.168.18.6:8080/webhook/find/principal12 \
  -H 'apikey: SUA_API_KEY'
```

**Solução**: O webhook é configurado automaticamente quando você conecta o WhatsApp. Se não estiver:

1. Acesse o painel admin do GED
2. Conecte o WhatsApp (obtenha QR Code)
3. O webhook será configurado automaticamente

#### 7.2. URL do Webhook Incorreta
**Verificar**: A Evolution API consegue acessar a URL do webhook?

**Solução**:
```bash
# Testa se o webhook está acessível
curl -X GET http://127.0.0.1:5000/whatsapp/webhook

# Deve retornar:
# {"status":"ok","message":"Webhook WhatsApp ativo"}
```

**Se o GED estiver em outro servidor**, configure a URL pública:
```python
# No .env ou config.py
WEBHOOK_BASE_URL = "https://meu-ged.com"
```

#### 7.3. Firewall Bloqueando Webhook
**Solução**:
```bash
# Libera porta 5000 (Flask)
sudo ufw allow 5000/tcp

# Ou use Nginx como proxy reverso
```

---

## 🚨 Problema 8: Erro "WhatsApp não configurado" Mesmo Após Configurar

### Sintomas
- Painel mostra "WhatsApp ATIVADO"
- Código ainda retorna "WhatsApp não configurado"

### Causa
Cache da configuração não foi atualizado

### Solução

#### 8.1. Reinicia o servidor Flask
```bash
# Se estiver usando systemd
sudo systemctl restart ged

# Se estiver rodando manualmente
# Ctrl+C e execute novamente
python3 app.py
```

#### 8.2. Verifica configuração no banco
```sql
-- Conecta ao banco
psql -U ged_user -d ged

-- Verifica configuração
SELECT ativo, evolution_api_url, evolution_instance_name
FROM configuracao_whatsapp
WHERE id = 1;

-- Deve retornar:
-- ativo | true
-- evolution_api_url | http://192.168.18.6:8080
-- evolution_instance_name | principal12
```

#### 8.3. Força recarga da configuração
```python
# No shell Python (python3)
from app import create_app, db
from app.models import ConfiguracaoWhatsApp

app = create_app()
with app.app_context():
    config = ConfiguracaoWhatsApp.query.get(1)
    print(f"Ativo: {config.ativo}")
    print(f"URL: {config.evolution_api_url}")
```

---

## 🛠️ Ferramentas de Diagnóstico

### 1. Script de Diagnóstico Completo
```bash
python3 diagnostico_evolution_v2_completo.py
```
- ✅ Testa TODAS as funcionalidades
- ✅ Relatório detalhado
- ✅ Recomendações específicas

### 2. Script de Teste Rápido
```bash
python3 teste_evolution_api.py
```
- ✅ Teste rápido de conectividade
- ✅ Verifica API Key
- ✅ Lista instâncias

### 3. Verificação do Sistema
```bash
python3 verificar_whatsapp.py
```
- ✅ Verifica banco de dados
- ✅ Mostra estatísticas
- ✅ Lista usuários com WhatsApp

### 4. Logs da Aplicação
```bash
# Logs do GED
tail -f logs/app.log

# Logs da Evolution API
docker logs -f evolution_api

# Logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

---

## 📊 Checklist de Verificação Rápida

Execute este checklist antes de reportar problemas:

- [ ] Evolution API está rodando (`docker ps | grep evolution`)
- [ ] WhatsApp está ativo no painel admin
- [ ] Credenciais estão preenchidas (URL, Instância, API Key)
- [ ] API Key do GED == `AUTHENTICATION_API_KEY` da Evolution API
- [ ] WhatsApp está conectado (status verde)
- [ ] Número de telefone do usuário está no formato correto (`+5585999999999`)
- [ ] Usuário tem `whatsapp_ativo = true` no banco
- [ ] Firewall não está bloqueando portas 8080 e 5000
- [ ] Logs não mostram erros (`tail -f logs/app.log`)

---

## 📚 Referências

- **Documentação Evolution API v2**: https://doc.evolution-api.com/v2/pt/
- **Guia Completo**: `GUIA_EVOLUTION_API.md`
- **Como Usar Diagnóstico**: `COMO_USAR_DIAGNOSTICO.md`
- **Referência da API**: `EVOLUTION_API_V2_REFERENCE.md`

---

## 🆘 Suporte

Se nenhuma solução funcionou:

1. **Execute o diagnóstico completo**:
   ```bash
   python3 diagnostico_evolution_v2_completo.py > diagnostico.log 2>&1
   ```

2. **Colete logs**:
   ```bash
   # Logs do GED
   tail -100 logs/app.log > ged.log

   # Logs da Evolution API
   docker logs evolution_api --tail 100 > evolution.log
   ```

3. **Verifique configuração**:
   ```bash
   # Exporta configuração do banco
   psql -U ged_user -d ged -c "SELECT * FROM configuracao_whatsapp;" > config.log
   ```

4. **Envie os 3 arquivos** (`diagnostico.log`, `ged.log`, `evolution.log`) para análise

---

**Última atualização**: 21/11/2024
**Versão**: 2.0
**Compatível com**: Evolution API v2.1.1+
