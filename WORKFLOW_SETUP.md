# 🔄 Workflow Oficial EBSERH - Sistema GED (UGQ Centralizado)

## 📋 Visão Geral

Este documento descreve a **implementação técnica do Workflow Oficial EBSERH** para o Sistema GED, que é **totalmente centralizado na Unidade de Gestão da Qualidade (UGQ)**.

### ⚠️ Mudança Fundamental

**❌ FLUXO ANTIGO (DESCARTADO):**
```
Autor → Chefia → Técnico → Qualidade → Aprovador → Admin
```

**✅ FLUXO OFICIAL EBSERH (CORRETO):**
```
Autor → UGQ (Triador) → UGQ (Validador) → Aprovadores → UGQ (Validador)
```

### 🎯 Conceito Central

O **Autor submete diretamente para a UGQ**, e a **UGQ gerencia todo o ciclo de vida do documento**:
- ✓ Triagem e validação de entrada
- ✓ Codificação e formatação
- ✓ Gestão do bloco de assinatura
- ✓ Publicação final

---

## 🏢 Arquitetura do Workflow UGQ

### 📊 Diagrama de Fluxo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       WORKFLOW OFICIAL EBSERH                            │
│              (Baseado em FLX.UGQ-CHUFC.002 e POPs da UGQ)               │
└─────────────────────────────────────────────────────────────────────────┘

ETAPA 0: AUTOR
┌──────────────────────────────────────────────┐
│  👤 USUÁRIO COMUM (Autor)                    │
│  ├─ Cria documento                           │
│  ├─ Preenche metadados                       │
│  ├─ Anexa arquivo (.doc, .docx, .odt)       │
│  └─ Clica "Submeter para Análise da UGQ"    │
└──────────────────────────────────────────────┘
                    ⬇️
        [Sistema cria tarefa "Documento Recebido"]
                    ⬇️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    🏢 UNIDADE DE GESTÃO DA QUALIDADE (UGQ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ETAPA 1: TRIAGEM
┌──────────────────────────────────────────────┐
│  🟡 QUALIDADE (Triador)                      │
│  📋 POP.UGQ-CHUFC.005                        │
│                                              │
│  Checkpoint 1: Documento já existe?          │
│  ├─ SIM → Devolve ao Autor ❌               │
│  └─ NÃO → Avança ✓                          │
│                                              │
│  Checkpoint 2: É Manual?                     │
│  ├─ SIM → Validado pelo Colegiado?          │
│  │   ├─ NÃO → Devolve ao Autor ❌          │
│  │   └─ SIM → Avança ✓                     │
│  └─ NÃO → Avança ✓                          │
│                                              │
│  Checkpoint 3: Formatação correta?           │
│  ├─ NÃO → Devolve ao Autor ❌               │
│  └─ SIM → "Aprovar Triagem" ✅              │
└──────────────────────────────────────────────┘
                    ⬇️
        [HAND-OFF: Triador → Validador]
        [Sistema cria "Validar e Codificar"]
                    ⬇️

ETAPA 2: CODIFICAÇÃO E VALIDAÇÃO
┌──────────────────────────────────────────────┐
│  🟢 QUALIDADE (Validador)                    │
│  📋 POP.UGQ-CHUFC.004                        │
│                                              │
│  ├─ Formatar (ajuste fino)                  │
│  ├─ Codificar: POP.SETOR-XYZ.001            │
│  ├─ Atualizar Lista Mestra                  │
│  ├─ Validar: Assinar Declaração SEI         │
│  └─ "Iniciar Bloco de Assinatura" ✅        │
└──────────────────────────────────────────────┘
                    ⬇️
    [Sistema abre "Gestão do Bloco de Assinatura"]
                    ⬇️

ETAPA 3: BLOCO DE ASSINATURA
┌──────────────────────────────────────────────┐
│  🟢 QUALIDADE (Validador)                    │
│  📋 POP.UGQ-CHUFC.006                        │
│                                              │
│  ├─ Anexar PDF final codificado             │
│  ├─ Selecionar Aprovadores (em ordem)       │
│  │   Ex: 1. Chefe Setor                     │
│  │       2. Superintendente                 │
│  └─ Escolher modo: Sequencial/Concomitante  │
└──────────────────────────────────────────────┘
                    ⬇️
        [Sistema cria tarefas para Aprovadores]
                    ⬇️

┌──────────────────────────────────────────────┐
│  🔵 APROVADORES (Chefias)                    │
│  ├─ Aprovador 1: Recebe tarefa "Assinar"    │
│  │   ├─ ❌ Reprovar → Volta p/ Validador   │
│  │   └─ ✅ Aprovar → Avança                │
│  ├─ Aprovador 2: Recebe tarefa "Assinar"    │
│  │   ├─ ❌ Reprovar → Volta p/ Validador   │
│  │   └─ ✅ Aprovar → Avança                │
│  └─ Todos aprovaram ✅                       │
└──────────────────────────────────────────────┘
                    ⬇️
    [Sistema cria "Publicar Documento Aprovado"]
                    ⬇️

ETAPA 4: PUBLICAÇÃO
┌──────────────────────────────────────────────┐
│  🟢 QUALIDADE (Validador)                    │
│                                              │
│  ├─ Move para status "VIGENTE"              │
│  ├─ Arquiva versão anterior "ANTIGO"        │
│  ├─ Publica no Portal                       │
│  └─ "Marcar Processo como Concluído" ✅     │
└──────────────────────────────────────────────┘
                    ⬇️
                 🎉 FIM
```

---

## 👥 Perfis e Responsabilidades

### 🔹 Perfil 1: QUALIDADE (Triador)

**Papel:** Porteiro da UGQ - Validação de entrada

**Responsabilidades:**
- Receber documentos dos autores
- Executar 3 checkpoints obrigatórios:
  1. Verificar duplicatas na Lista Mestra
  2. Validar aprovação do Colegiado (se for Manual)
  3. Validar formatação básica
- Devolver ao autor se não passar nos checkpoints
- Aprovar triagem e transferir para Validador

**Tarefas no Sistema:**
- `"Documento Recebido"` (criada quando Autor submete)

**Perfil no Banco:** `qualidade_triador`

---

### 🔹 Perfil 2: QUALIDADE (Validador)

**Papel:** Gestor Técnico - Codificação, validação, publicação

**Responsabilidades:**
- Formatar e codificar documentos
- Atualizar Lista Mestra
- Assinar validação (Declaração SEI)
- Gerenciar bloco de assinatura (sequencial/concomitante)
- Publicar documentos aprovados
- Receber devoluções de aprovadores reprovados

**Tarefas no Sistema:**
- `"Validar e Codificar Documento"` (criada quando Triador aprova)
- `"Gestão do Bloco de Assinatura"` (criada quando codifica)
- `"Publicar Documento Aprovado"` (criada quando todos aprovam)
- `"Realizar Ajustes"` (criada se algum aprovador reprova)

**Perfil no Banco:** `qualidade_validador`

---

### 🔹 Perfil 3: APROVADOR (Chefias)

**Papel:** Assinantes do Bloco de Assinatura

**Responsabilidades:**
- Assinar documentos no bloco de assinatura
- Aprovar ou reprovar com justificativa
- Se reprovar: anexar documento editável com correções

**Tarefas no Sistema:**
- `"Assinar Documento [Bloco #ID]"` (criada pelo Validador)

**Perfil no Banco:** `gerente` ou `superintendente`

---

### 🔹 Perfil 4: AUTOR (Usuário Comum)

**Papel:** Criador de documentos

**Responsabilidades:**
- Criar documentos
- Submeter para análise da UGQ
- Receber devoluções do Triador e corrigir

**Tarefas no Sistema:**
- `"Realizar Correção"` (criada se Triador devolve)

**Perfil no Banco:** `comum`

---

## 🔄 Detalhamento Técnico das Etapas

### ETAPA 0: Autor Submete Documento

#### Pseudocódigo

```python
# app/routes/routes_view.py

@view_bp.route('/documento/criar', methods=['POST'])
@login_required
def documento_criar():
    """Autor cria documento e submete para UGQ"""

    # 1. Cria documento
    documento = Documento(
        titulo=request.form['titulo'],
        tipo=request.form['tipo'],
        setor=request.form['setor'],
        criador_id=current_user.id,
        status='Novo',
        codigo_provisorio=gerar_codigo_provisorio()
    )

    # 2. Salva arquivo
    arquivo = request.files['arquivo']
    salvar_upload(arquivo, documento.id)

    db.session.add(documento)
    db.session.commit()

    # 3. Cria tarefa automática para TRIADOR UGQ
    triador_ugq = Usuario.query.filter_by(
        perfil='qualidade_triador',
        ativo=True
    ).first()

    if not triador_ugq:
        flash('❌ Erro: Nenhum Triador UGQ disponível', 'danger')
        return redirect(url_for('view.documentos'))

    tarefa = Tarefa(
        tipo_tarefa='Documento Recebido',
        documento_id=documento.id,
        responsavel_id=triador_ugq.id,
        criador_id=current_user.id,
        status='Pendente',
        prazo=datetime.now() + timedelta(days=5),
        descricao=f'Triagem de entrada: {documento.titulo}'
    )

    db.session.add(tarefa)
    db.session.commit()

    flash(f'✅ Documento submetido para análise da UGQ!', 'success')
    return redirect(url_for('view.documento_detalhe', id=documento.id))
```

---

### ETAPA 1: Triador UGQ Faz Triagem (3 Checkpoints)

#### Template HTML: Formulário de Triagem

```html
<!-- app/templates/tarefa_triagem.html -->

<form method="POST" action="{{ url_for('view.concluir_triagem', tarefa_id=tarefa.id) }}">

    <h4>🟡 Triagem UGQ - 3 Checkpoints Obrigatórios</h4>

    <!-- Checkpoint 1: Duplicata -->
    <div class="checkpoint">
        <label>✓ Checkpoint 1: Este documento já existe na Lista Mestra?</label>
        <select name="checkpoint_1" required>
            <option value="">Selecione...</option>
            <option value="nao">Não (documento novo)</option>
            <option value="sim">Sim (documento duplicado)</option>
        </select>
    </div>

    <!-- Checkpoint 2: Colegiado (condicional) -->
    <div class="checkpoint" id="checkpoint_2_container" style="display:none;">
        <label>✓ Checkpoint 2: Este Manual foi validado pelo Colegiado Executivo?</label>
        <select name="checkpoint_2">
            <option value="">Selecione...</option>
            <option value="sim">Sim (validado pelo Colegiado)</option>
            <option value="nao">Não (falta validação do Colegiado)</option>
            <option value="nao_se_aplica">Não se aplica (não é Manual)</option>
        </select>
    </div>

    <!-- Checkpoint 3: Formatação -->
    <div class="checkpoint">
        <label>✓ Checkpoint 3: O documento está no padrão de formatação?</label>
        <select name="checkpoint_3" required>
            <option value="">Selecione...</option>
            <option value="sim">Sim (formatação correta)</option>
            <option value="nao">Não (fora do padrão)</option>
        </select>
        <textarea name="observacoes_formatacao" placeholder="Descreva problemas de formatação (se houver)"></textarea>
    </div>

    <!-- Parecer -->
    <div class="form-group">
        <label>Parecer do Triador</label>
        <textarea name="parecer" required></textarea>
    </div>

    <!-- Ação -->
    <div class="form-group">
        <button type="submit" name="acao" value="aprovar" class="btn btn-success">
            ✅ Aprovar Triagem e Enviar para Validação
        </button>
        <button type="submit" name="acao" value="devolver" class="btn btn-warning">
            ↩️ Devolver ao Autor para Correção
        </button>
    </div>
</form>

<script>
// Mostra Checkpoint 2 apenas se for Manual
document.querySelector('select[name="tipo_documento"]').addEventListener('change', function() {
    if (this.value === 'Manual') {
        document.getElementById('checkpoint_2_container').style.display = 'block';
    } else {
        document.getElementById('checkpoint_2_container').style.display = 'none';
    }
});
</script>
```

#### Pseudocódigo: Processamento da Triagem

```python
# app/routes/routes_view.py

@view_bp.route('/tarefa/<int:tarefa_id>/concluir_triagem', methods=['POST'])
@login_required
def concluir_triagem(tarefa_id):
    """Triador UGQ conclui triagem com 3 checkpoints"""

    tarefa = Tarefa.query.get_or_404(tarefa_id)
    documento = tarefa.documento
    acao = request.form['acao']

    # Registra parecer
    tarefa.parecer = request.form['parecer']

    # Checkpoint 1: Duplicata
    checkpoint_1 = request.form['checkpoint_1']
    if checkpoint_1 == 'sim':
        # Devolver ao autor
        tarefa.aprovado = False
        tarefa.status = 'Concluída'
        criar_tarefa_correcao(documento, current_user,
            'Documento já existe na Lista Mestra.')
        flash('❌ Documento devolvido: duplicata detectada', 'warning')
        return redirect(url_for('view.minhas_tarefas'))

    # Checkpoint 2: Colegiado (apenas para Manuais)
    if documento.tipo == 'Manual':
        checkpoint_2 = request.form['checkpoint_2']
        if checkpoint_2 == 'nao':
            # Devolver ao autor
            tarefa.aprovado = False
            tarefa.status = 'Concluída'
            criar_tarefa_correcao(documento, current_user,
                'Manual precisa ser validado pelo Colegiado Executivo antes.')
            flash('❌ Documento devolvido: falta validação do Colegiado', 'warning')
            return redirect(url_for('view.minhas_tarefas'))

    # Checkpoint 3: Formatação
    checkpoint_3 = request.form['checkpoint_3']
    if checkpoint_3 == 'nao':
        # Devolver ao autor
        tarefa.aprovado = False
        tarefa.status = 'Concluída'
        observacoes = request.form['observacoes_formatacao']
        criar_tarefa_correcao(documento, current_user,
            f'Formatação fora do padrão: {observacoes}')
        flash('❌ Documento devolvido: problemas de formatação', 'warning')
        return redirect(url_for('view.minhas_tarefas'))

    # TODOS OS CHECKPOINTS APROVADOS!
    if acao == 'aprovar':
        tarefa.aprovado = True
        tarefa.status = 'Concluída'
        documento.status = 'Em Validação'

        # HAND-OFF: Cria tarefa para VALIDADOR UGQ
        validador_ugq = Usuario.query.filter_by(
            perfil='qualidade_validador',
            ativo=True
        ).first()

        if not validador_ugq:
            flash('❌ Erro: Nenhum Validador UGQ disponível', 'danger')
            return redirect(url_for('view.minhas_tarefas'))

        nova_tarefa = Tarefa(
            tipo_tarefa='Validar e Codificar Documento',
            documento_id=documento.id,
            responsavel_id=validador_ugq.id,
            criador_id=current_user.id,
            status='Pendente',
            prazo=datetime.now() + timedelta(days=7),
            descricao=f'Codificar, validar e preparar: {documento.titulo}'
        )

        db.session.add(nova_tarefa)
        db.session.commit()

        flash('✅ Triagem aprovada! Documento enviado para Validador UGQ', 'success')

    return redirect(url_for('view.minhas_tarefas'))


def criar_tarefa_correcao(documento, triador, motivo):
    """Cria tarefa de correção para o autor"""
    tarefa_correcao = Tarefa(
        tipo_tarefa='Realizar Correção',
        documento_id=documento.id,
        responsavel_id=documento.criador_id,
        criador_id=triador.id,
        status='Pendente',
        prazo=datetime.now() + timedelta(days=5),
        descricao=f'Correção necessária: {motivo}'
    )
    db.session.add(tarefa_correcao)
    documento.status = 'Em Correção'
```

---

### ETAPA 2: Validador UGQ Codifica e Valida

#### Modelo de Dados: Lista Mestra

```python
# app/models/models.py

class ListaMestra(db.Model):
    """Lista Mestra de Documentos da UGQ"""
    __tablename__ = 'lista_mestra'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)  # POP.SETOR-XYZ.001
    tipo = db.Column(db.String(50), nullable=False)  # POP, Manual, Protocolo
    titulo = db.Column(db.String(200), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    versao = db.Column(db.String(20), nullable=False)  # v1.0, v2.0
    data_publicacao = db.Column(db.DateTime, nullable=False)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'))
    status = db.Column(db.String(50), default='VIGENTE')  # VIGENTE, ANTIGO, OBSOLETO

    # Relacionamento
    documento = db.relationship('Documento', backref='registro_lista_mestra')

    def __repr__(self):
        return f'<ListaMestra {self.codigo} - {self.status}>'
```

#### Pseudocódigo: Codificação e Validação

```python
# app/routes/routes_view.py

@view_bp.route('/tarefa/<int:tarefa_id>/codificar', methods=['GET', 'POST'])
@login_required
def codificar_documento(tarefa_id):
    """Validador UGQ codifica documento e atualiza Lista Mestra"""

    if request.method == 'GET':
        # Mostra formulário de codificação
        tarefa = Tarefa.query.get_or_404(tarefa_id)
        documento = tarefa.documento

        # Sugere próximo código baseado na Lista Mestra
        ultimo_registro = ListaMestra.query.filter_by(
            tipo=documento.tipo,
            setor=documento.setor
        ).order_by(ListaMestra.id.desc()).first()

        if ultimo_registro:
            # Incrementa número
            numero_atual = int(ultimo_registro.codigo.split('.')[-1])
            numero_novo = numero_atual + 1
            codigo_sugerido = f'{documento.tipo}.{documento.setor}-{numero_novo:03d}'
        else:
            # Primeiro documento do tipo
            codigo_sugerido = f'{documento.tipo}.{documento.setor}-001'

        return render_template('tarefa_codificar.html',
            tarefa=tarefa,
            documento=documento,
            codigo_sugerido=codigo_sugerido
        )

    # POST: Processa codificação
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    documento = tarefa.documento

    # 1. Gera código definitivo
    codigo_definitivo = request.form['codigo']
    versao = request.form['versao']  # ex: v1.0

    documento.codigo_definitivo = codigo_definitivo
    documento.versao = versao
    documento.status = 'Validado'

    # 2. Atualiza Lista Mestra
    registro = ListaMestra(
        codigo=codigo_definitivo,
        tipo=documento.tipo,
        titulo=documento.titulo,
        setor=documento.setor,
        versao=versao,
        data_publicacao=datetime.now(),
        documento_id=documento.id,
        status='EM_APROVACAO'  # Ainda não está vigente
    )
    db.session.add(registro)

    # 3. Registra validação (Declaração SEI)
    validacao = ValidacaoUGQ(
        documento_id=documento.id,
        validador_id=current_user.id,
        data_validacao=datetime.now(),
        declaracao_sei='28538223',
        observacoes=request.form['observacoes_validacao']
    )
    db.session.add(validacao)

    # 4. Conclui tarefa
    tarefa.aprovado = True
    tarefa.status = 'Concluída'
    tarefa.parecer = f'Código gerado: {codigo_definitivo} {versao}'

    db.session.commit()

    flash(f'✅ Documento codificado: {codigo_definitivo}', 'success')

    # 5. Redireciona para criação do Bloco de Assinatura
    return redirect(url_for('view.criar_bloco_assinatura', documento_id=documento.id))
```

---

### ETAPA 3: Validador UGQ Gerencia Bloco de Assinatura

#### Modelos de Dados: Bloco de Assinatura

```python
# app/models/models.py

class BlocoAssinatura(db.Model):
    """Bloco de Assinatura para aprovação final"""
    __tablename__ = 'blocos_assinatura'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Validador UGQ
    modo = db.Column(db.String(20), nullable=False)  # 'sequencial' ou 'concomitante'
    status = db.Column(db.String(50), default='Em Andamento')  # Em Andamento, Aprovado, Reprovado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)

    # Relacionamentos
    documento = db.relationship('Documento', backref='blocos_assinatura')
    criador = db.relationship('Usuario', foreign_keys=[criador_id])
    itens = db.relationship('ItemBlocoAssinatura', backref='bloco', lazy='dynamic',
                            order_by='ItemBlocoAssinatura.ordem')

    def __repr__(self):
        return f'<BlocoAssinatura #{self.id} - {self.status}>'


class ItemBlocoAssinatura(db.Model):
    """Item individual do bloco: cada aprovador"""
    __tablename__ = 'itens_bloco_assinatura'

    id = db.Column(db.Integer, primary_key=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey('blocos_assinatura.id'), nullable=False)
    aprovador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)  # 1, 2, 3... (para modo sequencial)
    status = db.Column(db.String(50), default='Pendente')  # Pendente, Aprovado, Reprovado
    data_assinatura = db.Column(db.DateTime)
    parecer = db.Column(db.Text)

    # Relacionamento
    aprovador = db.relationship('Usuario', foreign_keys=[aprovador_id])

    def __repr__(self):
        return f'<Item #{self.ordem} - {self.aprovador.nome} - {self.status}>'
```

#### Template HTML: Criar Bloco de Assinatura

```html
<!-- app/templates/bloco_assinatura_criar.html -->

<form method="POST" action="{{ url_for('view.criar_bloco_assinatura', documento_id=documento.id) }}"
      enctype="multipart/form-data">

    <h4>🟢 Gestão do Bloco de Assinatura</h4>
    <p class="text-muted">Documento: {{ documento.codigo_definitivo }} - {{ documento.titulo }}</p>

    <!-- Anexar PDF Final -->
    <div class="form-group">
        <label>📎 Anexar PDF Final Codificado <span class="text-danger">*</span></label>
        <input type="file" name="pdf_final" accept=".pdf" required>
        <small>O PDF deve estar formatado, codificado e validado</small>
    </div>

    <!-- Modo de Assinatura -->
    <div class="form-group">
        <label>🔀 Modo de Assinatura</label>
        <select name="modo" required>
            <option value="sequencial">Sequencial (um por vez, em ordem)</option>
            <option value="concomitante">Concomitante (todos ao mesmo tempo)</option>
        </select>
    </div>

    <!-- Lista de Aprovadores -->
    <div class="form-group">
        <label>👥 Aprovadores (em ordem de assinatura)</label>
        <div id="aprovadores_container">
            <div class="aprovador-item">
                <span class="ordem">1.</span>
                <select name="aprovador_1" required>
                    <option value="">Selecione...</option>
                    {% for usuario in aprovadores_disponiveis %}
                    <option value="{{ usuario.id }}">{{ usuario.nome }} - {{ usuario.setor }}</option>
                    {% endfor %}
                </select>
                <button type="button" class="btn btn-sm btn-danger" onclick="removerAprovador(this)">×</button>
            </div>
        </div>
        <button type="button" class="btn btn-sm btn-secondary" onclick="adicionarAprovador()">
            + Adicionar Aprovador
        </button>
    </div>

    <!-- Observações -->
    <div class="form-group">
        <label>📝 Observações para os Aprovadores</label>
        <textarea name="observacoes" rows="3"></textarea>
    </div>

    <button type="submit" class="btn btn-primary">✅ Iniciar Bloco de Assinatura</button>
</form>

<script>
let contador_aprovadores = 1;

function adicionarAprovador() {
    contador_aprovadores++;
    const container = document.getElementById('aprovadores_container');
    const div = document.createElement('div');
    div.className = 'aprovador-item';
    div.innerHTML = `
        <span class="ordem">${contador_aprovadores}.</span>
        <select name="aprovador_${contador_aprovadores}" required>
            <option value="">Selecione...</option>
            {% for usuario in aprovadores_disponiveis %}
            <option value="{{ usuario.id }}">{{ usuario.nome }} - {{ usuario.setor }}</option>
            {% endfor %}
        </select>
        <button type="button" class="btn btn-sm btn-danger" onclick="removerAprovador(this)">×</button>
    `;
    container.appendChild(div);
}

function removerAprovador(btn) {
    btn.parentElement.remove();
    // Reordenar números
    document.querySelectorAll('.aprovador-item .ordem').forEach((el, idx) => {
        el.textContent = (idx + 1) + '.';
    });
}
</script>
```

#### Pseudocódigo: Criar Bloco de Assinatura

```python
# app/routes/routes_view.py

@view_bp.route('/documento/<int:documento_id>/bloco_assinatura/criar', methods=['GET', 'POST'])
@login_required
def criar_bloco_assinatura(documento_id):
    """Validador UGQ cria bloco de assinatura"""

    documento = Documento.query.get_or_404(documento_id)

    if request.method == 'GET':
        # Lista aprovadores disponíveis (Gerentes e Superintendentes)
        aprovadores = Usuario.query.filter(
            Usuario.perfil.in_(['gerente', 'superintendente']),
            Usuario.ativo == True
        ).all()

        return render_template('bloco_assinatura_criar.html',
            documento=documento,
            aprovadores_disponiveis=aprovadores
        )

    # POST: Cria o bloco
    modo = request.form['modo']

    # 1. Salva PDF final
    pdf_final = request.files['pdf_final']
    caminho_pdf = salvar_pdf_final(pdf_final, documento.id)
    documento.arquivo_final = caminho_pdf

    # 2. Cria Bloco de Assinatura
    bloco = BlocoAssinatura(
        documento_id=documento.id,
        criador_id=current_user.id,
        modo=modo,
        status='Em Andamento'
    )
    db.session.add(bloco)
    db.session.flush()  # Gera bloco.id

    # 3. Adiciona Aprovadores
    aprovadores_ids = []
    ordem = 1
    while f'aprovador_{ordem}' in request.form:
        aprovador_id = request.form[f'aprovador_{ordem}']
        if aprovador_id:
            aprovadores_ids.append((ordem, int(aprovador_id)))
        ordem += 1

    for ordem, aprovador_id in aprovadores_ids:
        item = ItemBlocoAssinatura(
            bloco_id=bloco.id,
            aprovador_id=aprovador_id,
            ordem=ordem,
            status='Pendente'
        )
        db.session.add(item)

    # 4. Cria tarefas para aprovadores
    if modo == 'sequencial':
        # Cria tarefa apenas para o primeiro aprovador
        primeiro_item = ItemBlocoAssinatura.query.filter_by(
            bloco_id=bloco.id,
            ordem=1
        ).first()

        tarefa = Tarefa(
            tipo_tarefa=f'Assinar Documento [Bloco #{bloco.id}]',
            documento_id=documento.id,
            responsavel_id=primeiro_item.aprovador_id,
            criador_id=current_user.id,
            status='Pendente',
            prazo=datetime.now() + timedelta(days=5),
            descricao=f'Assinar: {documento.codigo_definitivo}',
            metadata_json=json.dumps({
                'bloco_id': bloco.id,
                'item_id': primeiro_item.id,
                'modo': 'sequencial'
            })
        )
        db.session.add(tarefa)

    elif modo == 'concomitante':
        # Cria tarefas para TODOS os aprovadores
        for item in ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).all():
            tarefa = Tarefa(
                tipo_tarefa=f'Assinar Documento [Bloco #{bloco.id}]',
                documento_id=documento.id,
                responsavel_id=item.aprovador_id,
                criador_id=current_user.id,
                status='Pendente',
                prazo=datetime.now() + timedelta(days=5),
                descricao=f'Assinar: {documento.codigo_definitivo}',
                metadata_json=json.dumps({
                    'bloco_id': bloco.id,
                    'item_id': item.id,
                    'modo': 'concomitante'
                })
            )
            db.session.add(tarefa)

    documento.status = 'Em Aprovação'
    db.session.commit()

    flash(f'✅ Bloco de Assinatura #{bloco.id} criado! Tarefas enviadas aos aprovadores.', 'success')
    return redirect(url_for('view.documento_detalhe', id=documento.id))
```

#### Pseudocódigo: Aprovador Assina

```python
# app/routes/routes_view.py

@view_bp.route('/tarefa/<int:tarefa_id>/assinar', methods=['POST'])
@login_required
def assinar_documento(tarefa_id):
    """Aprovador assina documento no bloco de assinatura"""

    tarefa = Tarefa.query.get_or_404(tarefa_id)
    documento = tarefa.documento
    metadata = json.loads(tarefa.metadata_json)

    bloco_id = metadata['bloco_id']
    item_id = metadata['item_id']
    modo = metadata['modo']

    bloco = BlocoAssinatura.query.get(bloco_id)
    item = ItemBlocoAssinatura.query.get(item_id)

    acao = request.form['acao']  # 'aprovar' ou 'reprovar'
    parecer = request.form['parecer']

    # Registra assinatura/rejeição
    item.parecer = parecer
    item.data_assinatura = datetime.now()

    if acao == 'aprovar':
        item.status = 'Aprovado'
        tarefa.aprovado = True
        tarefa.status = 'Concluída'

        # Verifica se todos aprovaram
        if modo == 'sequencial':
            # Cria tarefa para próximo aprovador
            proximo_item = ItemBlocoAssinatura.query.filter_by(
                bloco_id=bloco.id,
                ordem=item.ordem + 1
            ).first()

            if proximo_item:
                # Ainda há aprovadores
                proxima_tarefa = Tarefa(
                    tipo_tarefa=f'Assinar Documento [Bloco #{bloco.id}]',
                    documento_id=documento.id,
                    responsavel_id=proximo_item.aprovador_id,
                    criador_id=current_user.id,
                    status='Pendente',
                    prazo=datetime.now() + timedelta(days=5),
                    metadata_json=json.dumps({
                        'bloco_id': bloco.id,
                        'item_id': proximo_item.id,
                        'modo': 'sequencial'
                    })
                )
                db.session.add(proxima_tarefa)
                flash('✅ Assinatura registrada! Enviado para próximo aprovador.', 'success')
            else:
                # Último aprovador - bloco completo!
                finalizar_bloco_assinatura(bloco, documento)

        elif modo == 'concomitante':
            # Verifica se todos assinaram
            total_itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).count()
            aprovados = ItemBlocoAssinatura.query.filter_by(
                bloco_id=bloco.id,
                status='Aprovado'
            ).count()

            if aprovados == total_itens:
                # Todos assinaram!
                finalizar_bloco_assinatura(bloco, documento)
            else:
                flash(f'✅ Assinatura registrada! Aguardando {total_itens - aprovados} aprovador(es).', 'success')

    elif acao == 'reprovar':
        item.status = 'Reprovado'
        tarefa.aprovado = False
        tarefa.status = 'Concluída'

        # Bloco reprovado - devolve para Validador UGQ
        bloco.status = 'Reprovado'
        documento.status = 'Em Ajustes'

        # Cancela todas as outras tarefas do bloco
        Tarefa.query.filter(
            Tarefa.metadata_json.contains(f'"bloco_id": {bloco.id}'),
            Tarefa.status == 'Pendente'
        ).update({'status': 'Cancelada'})

        # Cria tarefa para Validador UGQ fazer ajustes
        validador = Usuario.query.get(bloco.criador_id)
        tarefa_ajuste = Tarefa(
            tipo_tarefa='Realizar Ajustes [Reprovado]',
            documento_id=documento.id,
            responsavel_id=validador.id,
            criador_id=current_user.id,
            status='Pendente',
            prazo=datetime.now() + timedelta(days=5),
            descricao=f'Documento reprovado por {current_user.nome}: {parecer}'
        )
        db.session.add(tarefa_ajuste)

        flash(f'❌ Documento reprovado. Devolvido para Validador UGQ.', 'warning')

    db.session.commit()
    return redirect(url_for('view.minhas_tarefas'))


def finalizar_bloco_assinatura(bloco, documento):
    """Finaliza bloco de assinatura aprovado e cria tarefa de publicação"""
    bloco.status = 'Aprovado'
    bloco.data_conclusao = datetime.now()
    documento.status = 'Aprovado'

    # Cria tarefa de PUBLICAÇÃO para Validador UGQ
    validador = Usuario.query.get(bloco.criador_id)
    tarefa_publicar = Tarefa(
        tipo_tarefa='Publicar Documento Aprovado',
        documento_id=documento.id,
        responsavel_id=validador.id,
        criador_id=validador.id,
        status='Pendente',
        prazo=datetime.now() + timedelta(days=3),
        descricao=f'Publicar: {documento.codigo_definitivo}'
    )
    db.session.add(tarefa_publicar)

    flash('🎉 Todos os aprovadores assinaram! Documento enviado para publicação.', 'success')
```

---

### ETAPA 4: Validador UGQ Publica Documento

#### Pseudocódigo: Publicação Final

```python
# app/routes/routes_view.py

@view_bp.route('/tarefa/<int:tarefa_id>/publicar', methods=['POST'])
@login_required
def publicar_documento(tarefa_id):
    """Validador UGQ publica documento aprovado"""

    tarefa = Tarefa.query.get_or_404(tarefa_id)
    documento = tarefa.documento

    # 1. Move documento para VIGENTE
    documento.status = 'Publicado'
    documento.data_publicacao = datetime.now()

    # 2. Atualiza Lista Mestra
    registro = ListaMestra.query.filter_by(
        documento_id=documento.id
    ).first()

    if registro:
        registro.status = 'VIGENTE'

    # 3. Arquiva versão anterior (se houver)
    if documento.versao_anterior_id:
        doc_antigo = Documento.query.get(documento.versao_anterior_id)
        doc_antigo.status = 'Obsoleto'

        registro_antigo = ListaMestra.query.filter_by(
            documento_id=doc_antigo.id
        ).first()
        if registro_antigo:
            registro_antigo.status = 'ANTIGO'

    # 4. Copia PDF para pasta pública
    copiar_para_repositorio_publico(documento)

    # 5. Conclui tarefa
    tarefa.status = 'Concluída'
    tarefa.aprovado = True
    tarefa.parecer = f'Publicado em {datetime.now().strftime("%d/%m/%Y %H:%M")}'

    db.session.commit()

    # 6. Notifica todos os envolvidos
    notificar_publicacao(documento)

    flash(f'✅ Documento {documento.codigo_definitivo} publicado com sucesso!', 'success')
    return redirect(url_for('view.repositorio_publico'))
```

---

## 📋 Checklist de Implementação

### ✅ Banco de Dados

- [ ] Criar tabela `lista_mestra`
- [ ] Criar tabela `blocos_assinatura`
- [ ] Criar tabela `itens_bloco_assinatura`
- [ ] Criar tabela `validacoes_ugq`
- [ ] Adicionar campo `perfil` em `usuarios`:
  - `qualidade_triador`
  - `qualidade_validador`
- [ ] Adicionar campo `metadata_json` em `tarefas` (para dados do bloco)
- [ ] Adicionar campo `arquivo_final` em `documentos` (PDF codificado)

### ✅ Backend

- [ ] Criar rota `/documento/criar` (Autor submete)
- [ ] Criar rota `/tarefa/<id>/concluir_triagem` (Triador)
- [ ] Criar rota `/tarefa/<id>/codificar` (Validador codifica)
- [ ] Criar rota `/documento/<id>/bloco_assinatura/criar` (Validador cria bloco)
- [ ] Criar rota `/tarefa/<id>/assinar` (Aprovadores assinam)
- [ ] Criar rota `/tarefa/<id>/publicar` (Validador publica)
- [ ] Criar service `WorkflowUGQ` com métodos:
  - `criar_tarefa_triagem()`
  - `criar_tarefa_validacao()`
  - `criar_bloco_assinatura()`
  - `processar_assinatura()`
  - `publicar_documento()`

### ✅ Frontend

- [ ] Template `documento_criar.html` (com botão "Submeter para UGQ")
- [ ] Template `tarefa_triagem.html` (3 checkpoints)
- [ ] Template `tarefa_codificar.html` (codificação + Lista Mestra)
- [ ] Template `bloco_assinatura_criar.html` (selecionar aprovadores)
- [ ] Template `tarefa_assinar.html` (aprovar/reprovar)
- [ ] Template `tarefa_publicar.html` (publicação final)
- [ ] Dashboard: Separar tarefas por perfil (Triador/Validador)

### ✅ Testes

- [ ] Teste E2E: Fluxo completo (Autor → UGQ → Aprovadores → Publicação)
- [ ] Teste: Checkpoint 1 reprova (duplicata)
- [ ] Teste: Checkpoint 2 reprova (Manual sem Colegiado)
- [ ] Teste: Checkpoint 3 reprova (formatação)
- [ ] Teste: Modo sequencial (assinaturas em ordem)
- [ ] Teste: Modo concomitante (assinaturas paralelas)
- [ ] Teste: Aprovador reprova (volta para Validador)
- [ ] Teste: Publicação atualiza Lista Mestra

---

## 📚 Referências Oficiais EBSERH

### Documentos Base

1. **FLX.UGQ-CHUFC.002** - Fluxo de Elaboração e Revisão de Documentos
2. **POP.UGQ-CHUFC.004** - Codificação de Documentos
3. **POP.UGQ-CHUFC.005** - Triagem de Documentos
4. **POP.UGQ-CHUFC.006** - Gestão do Bloco de Assinatura
5. **Declaração SEI 28538223** - Modelo de Validação UGQ

### Nomenclatura de Códigos

```
Padrão: [TIPO].[SETOR]-[SEQUENCIAL]

Exemplos:
- POP.OPERACOES-001
- MANUAL.QUALIDADE-005
- PROTOCOLO.TI-023
- FORMULARIO.RH-012
```

### Estados de Documentos na Lista Mestra

- **VIGENTE** - Documento publicado e ativo
- **ANTIGO** - Versão anterior (substituída)
- **OBSOLETO** - Documento descontinuado
- **EM_APROVACAO** - Aguardando bloco de assinatura

---

## 🚀 Próximos Passos

Após implementar toda a documentação acima:

1. ✅ Aplicar migrations do banco de dados
2. ✅ Criar usuários de teste (Triador e Validador UGQ)
3. ✅ Testar fluxo completo E2E
4. ✅ Ajustar templates conforme necessário
5. ✅ Documentar APIs REST
6. ✅ Criar testes automatizados
7. ✅ Deploy em produção

---

**Sistema GED EBSERH - Workflow UGQ Oficial** 🏥
*Centralizado na Unidade de Gestão da Qualidade*
