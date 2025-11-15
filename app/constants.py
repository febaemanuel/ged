"""
Constantes centralizadas do sistema GED
Evita strings hardcoded espalhadas pelo código
"""

# ============================================================================
# MENSAGENS DE FLASH/FEEDBACK
# ============================================================================

# Autenticação
MSG_LOGIN_SUCESSO = 'Login realizado com sucesso!'
MSG_LOGIN_ERRO = 'Email ou senha inválidos'
MSG_LOGOUT_SUCESSO = 'Logout realizado com sucesso'
MSG_USUARIO_INATIVO = 'Usuário inativo'
MSG_SENHA_ALTERADA = 'Senha alterada com sucesso!'
MSG_SENHA_ATUAL_INCORRETA = 'Senha atual incorreta'
MSG_SENHAS_NAO_COINCIDEM = 'As senhas não coincidem'
MSG_SENHA_FRACA = 'A nova senha não atende aos requisitos de segurança'

# Documentos
MSG_DOC_CRIADO = 'Documento {codigo} criado com sucesso!'
MSG_DOC_ATUALIZADO = 'Documento atualizado com sucesso!'
MSG_DOC_EXCLUIDO = 'Documento excluído com sucesso'
MSG_DOC_NAO_ENCONTRADO = 'Documento não encontrado'
MSG_ARQUIVO_OBRIGATORIO = 'Arquivo é obrigatório'
MSG_ARQUIVO_NAO_ENCONTRADO = 'Arquivo não encontrado'
MSG_EXTENSAO_NAO_PERMITIDA = 'Extensão .{extensao} não permitida'

# Tarefas
MSG_TAREFA_CRIADA = 'Tarefa criada com sucesso!'
MSG_TAREFA_CONCLUIDA = 'Tarefa concluída com sucesso!'
MSG_TAREFA_JA_CONCLUIDA = 'Tarefa já foi concluída'

# Usuários
MSG_USUARIO_CRIADO = 'Usuário {nome} criado com sucesso!'
MSG_USUARIO_ATUALIZADO = 'Usuário {nome} atualizado com sucesso!'
MSG_USUARIO_EXCLUIDO = 'Usuário {nome} excluído com sucesso!'
MSG_EMAIL_JA_CADASTRADO = 'Email já cadastrado'

# Permissões
MSG_ACESSO_NEGADO = 'Acesso negado'
MSG_SEM_PERMISSAO_EDITAR = 'Você não tem permissão para editar este documento'
MSG_SEM_PERMISSAO_VISUALIZAR = 'Sem permissão para visualizar este documento'
MSG_SEM_PERMISSAO_CONCLUIR = 'Você não tem permissão para concluir esta tarefa'
MSG_REQUER_AUTENTICACAO = 'Este documento requer autenticação'
MSG_APENAS_ADMIN = 'Apenas administradores podem realizar esta ação'
MSG_APENAS_GERENTES = 'Apenas gerentes e administradores podem criar tarefas'

# Workflow UGQ
MSG_TRIAGEM_APROVADA = '✅ Triagem aprovada! Documento enviado para Validador UGQ'
MSG_DOC_DEVOLVIDO_AUTOR = '❌ Documento devolvido ao autor para correção'
MSG_DOC_CODIFICADO = '✅ Documento codificado: {codigo}'
MSG_DOC_DEVOLVIDO_TRIADOR = '📤 Documento devolvido para o Triador UGQ'
MSG_DOC_DEVOLVIDO_VALIDADOR = '📤 Documento devolvido para o Validador UGQ'
MSG_BLOCO_CRIADO = '✅ Bloco de Assinatura #{bloco_id} criado!'
MSG_ASSINATURA_REGISTRADA = '✅ Assinatura registrada!'
MSG_DOC_PUBLICADO = '🎉 Documento {codigo} publicado com sucesso!'
MSG_TODOS_APROVARAM = '🎉 Todos aprovaram! Documento enviado para publicação'
MSG_DOC_REPROVADO = '❌ Documento reprovado. Devolvido para Validador UGQ'

# Validações
MSG_CAMPOS_OBRIGATORIOS = 'Preencha todos os campos obrigatórios'
MSG_SENHA_INCORRETA = 'Senha incorreta'
MSG_NAO_PODE_EXCLUIR_PROPRIA_CONTA = 'Você não pode excluir sua própria conta'

# Erros genéricos
MSG_ERRO_INESPERADO = 'Erro inesperado: {erro}'
MSG_ERRO_PROCESSAR = 'Erro ao processar: {erro}'


# ============================================================================
# LABELS E TEXTOS DA INTERFACE
# ============================================================================

LABEL_DOCUMENTO = 'Documento'
LABEL_TAREFA = 'Tarefa'
LABEL_USUARIO = 'Usuário'
LABEL_STATUS = 'Status'
LABEL_TIPO = 'Tipo'
LABEL_SETOR = 'Setor'
LABEL_DATA_CRIACAO = 'Data de Criação'
LABEL_DATA_VENCIMENTO = 'Data de Vencimento'


# ============================================================================
# DEFAULTS E VALORES PADRÃO
# ============================================================================

DEFAULT_VALIDADE_ANOS = 5
DEFAULT_PAGINACAO = 20
DEFAULT_PRAZO_DIAS = 7


# ============================================================================
# REGEX PATTERNS
# ============================================================================

PATTERN_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PATTERN_CODIGO_DOCUMENTO = r'^[A-Z]+\.[A-Z]+-\d{3}$'  # Ex: POP.TI-001


# ============================================================================
# LIMITES E RESTRIÇÕES
# ============================================================================

MAX_UPLOAD_SIZE_MB = 16
MAX_TITULO_LENGTH = 200
MAX_DESCRICAO_LENGTH = 1000
MAX_SEARCH_RESULTS = 100
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

# Rate Limiting
RATE_LIMIT_LOGIN_ATTEMPTS = 5  # tentativas
RATE_LIMIT_LOGIN_WINDOW = 300  # 5 minutos em segundos
RATE_LIMIT_API_REQUESTS = 100  # por minuto
