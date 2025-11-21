# 🚀 Guia Completo - Configuração WhatsApp Evolution API v2

## ✅ Sistema Completamente Refatorado!

A integração WhatsApp foi **completamente refeita do zero** baseada na documentação oficial da Evolution API v2.2.2.

---

## 🎯 O que Mudou?

### ✨ Melhorias Principais

1. **Serviço Evolution API v2**
   - ✅ Endpoints corretos da API v2.2.2
   - ✅ Logging detalhado de todas as operações
   - ✅ Retry automático com backoff exponencial
   - ✅ Tratamento robusto de erros (401, 403, 404, 500)
   - ✅ Mensagens de erro descritivas e úteis
   - ✅ Criação automática de instância

2. **Nova Interface de Configuração**
   - ✅ Design moderno e responsivo
   - ✅ Status em tempo real (atualiza a cada 10s)
   - ✅ QR Code com auto-refresh automático (25s)
   - ✅ Timer visual com progress bar
   - ✅ Validação de formulário no frontend
   - ✅ Toggle de visibilidade de senha
   - ✅ Tooltips explicativos

3. **Documentação Completa**
   - ✅ `EVOLUTION_API_V2_REFERENCE.md` - Referência da API
   - ✅ Exemplos de todos os endpoints
   - ✅ Scripts de teste e diagnóstico

---

## 🔧 Como Configurar (Passo a Passo)

### Passo 1: Encontre a API Key Correta ⚠️

A API Key está no arquivo `.env` da Evolution API:

```bash
# No diretório da Evolution API
cat .env | grep AUTHENTICATION_API_KEY
```

Você verá algo como:
```env
AUTHENTICATION_API_KEY=12345678
```

**Essa é a API Key que você deve usar!**

---

### Passo 2: Acesse a Página de Configuração

```
http://127.0.0.1:5000/admin/whatsapp
```

---

### Passo 3: Preencha as Credenciais

**URL da Evolution API:**
```
http://host.docker.internal:8080
```
⚠️ **SEM barra no final!**

**Nome da Instância:**
```
principal12
```
⚠️ **Apenas letras, números e underscore (_)**

**API Key:**
```
12345678
```
⚠️ **Exatamente igual ao `AUTHENTICATION_API_KEY` do .env**

---

### Passo 4: Marque "WhatsApp ATIVADO"

Certifique-se de que o toggle no topo esteja **ATIVADO** (verde).

---

### Passo 5: Clique em "Salvar Configurações"

O sistema validará:
- ✓ URL começa com http:// ou https://
- ✓ Nome da instância é válido
- ✓ API Key tem pelo menos 8 caracteres

---

### Passo 6: Obtenha o QR Code

1. **Clique no botão verde "Obter QR Code"**

2. **O QR Code aparecerá automaticamente**
   - Timer de 30 segundos
   - Progress bar animada
   - Auto-refresh antes de expirar

3. **Escaneie com seu WhatsApp:**
   - Abra o WhatsApp no celular
   - Configurações → Aparelhos conectados
   - Conectar um aparelho
   - Escaneie o QR Code

4. **Aguarde a conexão**
   - O status mudará para "WhatsApp Conectado" (verde)
   - Atualizações a cada 10 segundos

---

## 🧪 Como Testar

### Teste 1: Enviar Mensagem de Teste

1. No painel lateral, insira um número de teste:
   ```
   +5585999999999
   ```

2. Clique em "Enviar Teste"

3. Você receberá uma mensagem de confirmação no WhatsApp

---

### Teste 2: Verificar Logs

1. Clique em "Ver Logs de Mensagens"
2. Verifique se a mensagem de teste foi registrada

---

## 🐛 Solução de Problemas

### Erro: "API Key inválida"

**Causa:** A API Key não corresponde à configurada na Evolution API

**Solução:**
```bash
# Verifique a API Key no .env da Evolution API
cat .env | grep AUTHENTICATION_API_KEY

# Use EXATAMENTE esse valor na página de configuração
```

---

### Erro: "Não foi possível conectar"

**Causa:** Evolution API não está rodando ou URL incorreta

**Solução:**
```bash
# Verifique se a Evolution API está rodando
docker ps | grep evolution

# Verifique a URL
curl http://host.docker.internal:8080/

# Deve retornar: {"status":200,"message":"Welcome to the Evolution API..."}
```

---

### Erro: "QR Code não disponível"

**Causa:** WhatsApp já está conectado

**Solução:**
1. Verifique o card de "Status da Conexão"
2. Se estiver verde (conectado), está tudo certo!
3. Se estiver amarelo (desconectado), tente novamente

---

### Erro: "Instância não encontrada"

**Causa:** Instância ainda não foi criada

**Solução:**
1. O sistema cria automaticamente
2. Aguarde 3 segundos
3. Clique em "Obter QR Code" novamente

---

## 📊 Monitoramento

### Status em Tempo Real

O card "Status da Conexão" mostra:

🟢 **Verde** = WhatsApp Conectado
- Pronto para enviar mensagens
- Chatbot funcionando

🟡 **Amarelo** = WhatsApp Desconectado
- Precisa escanear QR Code
- Mensagens não serão enviadas

---

### Logs Detalhados

Para debug avançado, verifique os logs do Flask:

```bash
# Se estiver usando o servidor de desenvolvimento
# Os logs aparecem no terminal onde o Flask está rodando

# Procure por:
[INFO] Tentando obter QR Code para instância: principal12
[INFO] URL Base: http://host.docker.internal:8080
[INFO] QR Code obtido com sucesso!
```

---

## 🔗 Arquivos Criados

### Documentação
- ✅ `EVOLUTION_API_V2_REFERENCE.md` - Referência completa da API
- ✅ `COMO_USAR_WHATSAPP_V2.md` - Este guia
- ✅ `COMO_ENCONTRAR_API_KEY.md` - Guia para encontrar API Key

### Scripts de Teste
- ✅ `teste_evolution_api.py` - Teste rápido de conectividade
- ✅ `diagnostico_whatsapp.py` - Diagnóstico completo

### Código
- ✅ `app/services/evolution_api_service_v2.py` - Nova implementação
- ✅ `app/templates/admin/whatsapp_config_v2.html` - Nova interface

---

## 📚 Recursos Adicionais

### Documentação Evolution API
- [Documentação Oficial](https://doc.evolution-api.com)
- [Referência Rápida](EVOLUTION_API_V2_REFERENCE.md)

### Scripts de Teste

**Teste Rápido:**
```bash
# Edite a API Key no arquivo primeiro!
nano teste_evolution_api.py

# Execute
python3 teste_evolution_api.py
```

**Diagnóstico Completo:**
```bash
# Requer ambiente virtual ativo
source venv/bin/activate
python diagnostico_whatsapp.py
```

---

## ✅ Checklist Final

Antes de considerar a configuração completa:

- [ ] Evolution API está rodando (`docker ps`)
- [ ] API Key foi encontrada e está correta
- [ ] URL foi configurada sem barra no final
- [ ] Nome da instância usa apenas letras, números e _
- [ ] WhatsApp está ATIVADO (toggle verde)
- [ ] Configurações foram salvas
- [ ] QR Code foi obtido com sucesso
- [ ] QR Code foi escaneado com WhatsApp
- [ ] Status mostra "WhatsApp Conectado" (verde)
- [ ] Teste de envio funcionou
- [ ] Log de mensagens mostra a mensagem de teste

---

## 🎉 Pronto!

Seu sistema WhatsApp está configurado e funcionando!

**O que acontece agora:**

1. ✅ Notificações de tarefas são enviadas via WhatsApp
2. ✅ Usuários podem assinar documentos pelo WhatsApp
3. ✅ Chatbot responde automaticamente
4. ✅ Lembretes de prazo são enviados
5. ✅ Todas as mensagens são registradas em logs

---

## 🆘 Precisa de Ajuda?

Se ainda tiver problemas:

1. **Verifique os logs do Docker:**
   ```bash
   docker logs evolution_api
   ```

2. **Execute o script de diagnóstico:**
   ```bash
   python3 teste_evolution_api.py
   ```

3. **Verifique a documentação:**
   - `EVOLUTION_API_V2_REFERENCE.md`
   - `COMO_ENCONTRAR_API_KEY.md`

4. **Abra uma issue no GitHub** com:
   - Logs do Docker
   - Resultado do script de teste
   - Screenshot da página de configuração

---

**Versão:** 2.0 - Refatoração Completa
**Data:** 21/11/2024
**Compatível com:** Evolution API v2.1.1+ (testado com v2.2.2)
