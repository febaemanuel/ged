# Como Usar o Diagnóstico da Evolution API v2

## 📋 Visão Geral

O script `diagnostico_evolution_v2_completo.py` é uma ferramenta completa de diagnóstico para verificar o estado da integração com a Evolution API v2.

## 🚀 Como Executar

### Método 1: Execução Simples

```bash
python3 diagnostico_evolution_v2_completo.py
```

### Método 2: Com Permissão de Execução

```bash
chmod +x diagnostico_evolution_v2_completo.py
./diagnostico_evolution_v2_completo.py
```

## 🧪 O Que o Script Testa

### 1. Configuração do Banco de Dados
- ✅ Carrega configurações da tabela `configuracao_whatsapp`
- ✅ Valida se URL, instância e API Key estão configuradas
- ✅ Verifica se o WhatsApp está ativo no sistema

### 2. Conectividade com Evolution API
- ✅ Testa conexão básica com a API
- ✅ Verifica versão da Evolution API instalada
- ✅ Testa acesso com e sem autenticação

### 3. Autenticação (API Key)
- ✅ Valida se a API Key está correta
- ✅ Lista todas as instâncias disponíveis
- ✅ Verifica permissões de acesso

### 4. Status da Instância
- ✅ Verifica se a instância existe
- ✅ Mostra estado da conexão WhatsApp (open/close/connecting)
- ✅ Identifica se o WhatsApp está conectado

### 5. QR Code
- ✅ Testa obtenção de QR Code
- ✅ Cria instância automaticamente se não existir
- ✅ Identifica se WhatsApp já está conectado

### 6. Envio de Mensagem (Opcional)
- ✅ Permite testar envio de mensagem real
- ✅ Solicita número de teste do usuário
- ✅ Envia mensagem de teste formatada
- ✅ Retorna ID da mensagem enviada

### 7. Webhook
- ✅ Verifica se webhook está configurado
- ✅ Mostra URL e eventos configurados
- ✅ Indica se webhook está ativo

### 8. Banco de Dados
- ✅ Verifica conexão com PostgreSQL
- ✅ Valida existência de tabelas necessárias
- ✅ Mostra estatísticas de uso (mensagens, conversas, usuários)

### 9. Relatório Final
- 📊 Agrupa resultados por categoria
- 📈 Calcula taxa de sucesso/falha
- 💡 Fornece recomendações específicas baseadas nos problemas encontrados

## 🎨 Saída Colorida

O script usa cores no terminal para facilitar a leitura:

- 🟢 **Verde (✓)**: Teste passou com sucesso
- 🔴 **Vermelho (✗)**: Teste falhou
- 🟡 **Amarelo (⚠)**: Aviso ou atenção necessária
- 🔵 **Azul**: Informações e detalhes

## 📝 Exemplo de Saída

```
╔════════════════════════════════════════════════════════════════════════════════╗
║          DIAGNÓSTICO COMPLETO - EVOLUTION API V2                               ║
║          Baseado na documentação oficial v2.1.1+                               ║
╚════════════════════════════════════════════════════════════════════════════════╝

================================================================================
1. CARREGANDO CONFIGURAÇÃO DO BANCO DE DADOS
================================================================================

  Importando módulos...
✓ Configuração carregada do banco de dados
  ID: 1
  WhatsApp Ativo: True
  URL Evolution API: http://192.168.18.6:8080
  Nome da Instância: principal12
  API Key: ********

================================================================================
2. TESTANDO CONECTIVIDADE COM EVOLUTION API
================================================================================

  Testando: http://192.168.18.6:8080
✓ Evolution API está acessível
  Versão: v2.1.1
  Client: Evolution API
  Manager: Baileys

...

================================================================================
9. RELATÓRIO FINAL DO DIAGNÓSTICO
================================================================================

  Total de testes: 12
  Sucessos: 10 (83.3%)
  Falhas: 2 (16.7%)

Configuração
------------
Sucessos: 1, Falhas: 0
  ✓ Carregar do banco

Conectividade
------------
Sucessos: 1, Falhas: 0
  ✓ Acesso à API → Versão: v2.1.1

...

RECOMENDAÇÕES
------------
⚠ Alguns testes falharam
  Ações recomendadas:
    • Acesse http://127.0.0.1:5000/admin/whatsapp
    • Clique em 'Obter QR Code'
    • Escaneie o QR Code com seu WhatsApp
```

## 🔍 Interpretando os Resultados

### ✅ Sistema Totalmente Funcional
Se todos os testes passarem, você verá:
```
✓ Sistema totalmente funcional! ✨
  Próximos passos:
    1. Acesse http://127.0.0.1:5000/admin/whatsapp
    2. Configure webhooks se necessário
    3. Teste envio de mensagens
```

### ⚠️ Problemas Encontrados

#### Erro de Conexão
```
✗ Não foi possível conectar em http://192.168.18.6:8080
  Verifique se a Evolution API está rodando:
    docker ps
```

**Solução**: Verifique se o container Docker da Evolution API está rodando.

#### API Key Inválida
```
✗ API Key inválida!
  Verifique o valor de AUTHENTICATION_API_KEY no .env da Evolution API
```

**Solução**: Compare a API Key no banco de dados do GED com o valor de `AUTHENTICATION_API_KEY` no arquivo `.env` da Evolution API.

#### Instância Não Conectada
```
⚠ WhatsApp está DESCONECTADO
  Você precisa escanear o QR Code para conectar
```

**Solução**:
1. Acesse http://127.0.0.1:5000/admin/whatsapp
2. Clique em "Obter QR Code"
3. Escaneie o QR Code com seu WhatsApp

#### Webhook Não Configurado
```
⚠ Webhook não configurado ou desativado
  Configure em: http://127.0.0.1:5000/admin/whatsapp
```

**Solução**: O webhook é configurado automaticamente pela Evolution API quando você conecta o WhatsApp. Verifique se o WhatsApp está conectado.

## 🛠️ Troubleshooting

### Problema: "No module named 'flask'"
**Solução**: Instale as dependências do projeto
```bash
pip install -r requirements.txt
```

### Problema: "Não foi possível conectar ao banco de dados"
**Solução**: Verifique se o PostgreSQL está rodando
```bash
sudo service postgresql start
```

### Problema: "Tabela 'configuracao_whatsapp' NÃO EXISTE"
**Solução**: Execute as migrações do banco
```bash
python3 aplicar_migracao.py
```

### Problema: "Evolution API retornou 403"
**Causas possíveis**:
1. **API Key incorreta**: Verifique se a API Key no banco está igual ao `.env` da Evolution API
2. **Instância já existe**: Normal, o script tenta criar mas já existe (não é um erro grave)

### Problema: "QR Code não encontrado na resposta"
**Causas possíveis**:
1. **WhatsApp já conectado**: Não precisa de QR Code
2. **Instância em estado inválido**: Tente deletar e recriar a instância

## 📊 Comparação com Outros Scripts

### `teste_evolution_api.py`
- ✅ Teste rápido e simples
- ✅ Foca em conectividade básica
- ❌ Não verifica banco de dados
- ❌ Não faz estatísticas

### `verificar_whatsapp.py`
- ✅ Foca em banco de dados
- ✅ Mostra estatísticas detalhadas
- ❌ Não testa envio de mensagens
- ❌ Não verifica QR Code

### `diagnostico_whatsapp.py`
- ✅ Mais completo que os anteriores
- ✅ Testa criação de instância
- ❌ Menos detalhado que o v2_completo

### `diagnostico_evolution_v2_completo.py` ⭐
- ✅ **MAIS COMPLETO**
- ✅ Testa TODAS as funcionalidades
- ✅ Relatório detalhado com recomendações
- ✅ Saída colorida e fácil de ler
- ✅ Baseado na documentação oficial v2

## 💡 Dicas

### 1. Execute Regularmente
Execute o diagnóstico após:
- Instalar/atualizar a Evolution API
- Alterar configurações no painel admin
- Problemas de envio de mensagens
- Após reiniciar o servidor

### 2. Salve os Logs
Salve a saída do diagnóstico para análise posterior:
```bash
python3 diagnostico_evolution_v2_completo.py > diagnostico_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### 3. Use em Produção
O script é seguro para usar em produção, pois:
- Não altera configurações sem permissão
- Não envia mensagens sem confirmação
- Apenas lê dados para análise

### 4. Integre no CI/CD
Você pode integrar o diagnóstico no seu pipeline de CI/CD para validar a configuração automaticamente.

## 🤝 Suporte

Se o diagnóstico não resolver seu problema:

1. **Revise os logs da Evolution API**:
   ```bash
   docker logs evolution_api
   ```

2. **Verifique logs do GED**:
   ```bash
   tail -f logs/app.log
   ```

3. **Consulte a documentação oficial**:
   - https://doc.evolution-api.com/v2/pt/get-started/introduction

4. **Abra uma issue no GitHub**:
   - https://github.com/EvolutionAPI/evolution-api/issues

## 📚 Documentação Relacionada

- `GUIA_EVOLUTION_API.md` - Guia completo de setup
- `EVOLUTION_API_V2_REFERENCE.md` - Referência da API
- `COMO_USAR_WHATSAPP_V2.md` - Guia de uso para usuários finais
- `SETUP_EVOLUTION_DB.md` - Setup do banco Evolution

## 🎯 Próximos Passos

Após executar o diagnóstico e corrigir os problemas:

1. **Configure usuários**: Adicione números de telefone aos usuários
2. **Ative notificações**: Habilite notificações via WhatsApp no painel admin
3. **Teste chatbot**: Envie "menu" para o WhatsApp e teste as funcionalidades
4. **Configure lembretes**: Ative lembretes automáticos de tarefas
5. **Personalize templates**: Edite os templates de mensagens no painel admin

---

**Última atualização**: 21/11/2024
**Versão**: 2.0
**Compatível com**: Evolution API v2.1.1+
