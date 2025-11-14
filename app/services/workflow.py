"""
Serviço de Workflow Automático UGQ - Sistema GED EBSERH
Gerencia o fluxo oficial EBSERH centralizado na Unidade de Gestão da Qualidade

FLUXO OFICIAL EBSERH (Centralizado na UGQ):
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 0: Autor submete → Cria "Documento Recebido" p/ UGQ │
│  ETAPA 1: Triador UGQ (3 checkpoints) → Aprova ou Devolve  │
│  ETAPA 2: Validador UGQ (Codifica + Lista Mestra)          │
│  ETAPA 3: Validador UGQ (Bloco de Assinatura)              │
│  ETAPA 4: Validador UGQ (Publicação)                       │
└─────────────────────────────────────────────────────────────┘

Baseado em: FLX.UGQ-CHUFC.002 e POPs da Qualidade
"""

from datetime import datetime, timedelta
from app.models import db, Tarefa, Documento, Usuario, ListaMestra, BlocoAssinatura, ItemBlocoAssinatura
from config import Config
import logging
import json

logger = logging.getLogger(__name__)


def log_debug(message):
    """Helper para logar tanto no logger quanto no console"""
    print(f"[WORKFLOW UGQ] {message}")
    logger.info(message)


class WorkflowUGQ:
    """
    Gerenciador de Workflow UGQ Centralizado
    Implementa o fluxo oficial EBSERH
    """

    # ========================================================================
    # ETAPA 0: AUTOR SUBMETE DOCUMENTO
    # ========================================================================

    @classmethod
    def autor_submete_documento(cls, documento):
        """
        Autor cria documento e submete para análise da UGQ
        Cria tarefa "Documento Recebido" para Triador UGQ

        Args:
            documento: Objeto Documento

        Returns:
            Tarefa criada para Triador UGQ
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 0: Autor submete documento {documento.id}")
        log_debug(f"Título: {documento.titulo}")
        log_debug(f"Tipo: {documento.tipo_documento}")
        log_debug("=" * 80)

        # Busca Triador UGQ disponível
        triador = Usuario.query.filter_by(
            perfil=Config.PERFIL_QUALIDADE_TRIADOR,
            ativo=True
        ).first()

        if not triador:
            log_debug("❌ ERRO: Nenhum Triador UGQ disponível")
            raise ValueError("Nenhum Triador UGQ disponível no sistema")

        log_debug(f"✅ Triador UGQ encontrado: {triador.nome} ({triador.email})")

        # Cria tarefa de triagem
        tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=documento.criador_id,
            responsavel_id=triador.id,
            tipo_tarefa=Config.TAREFA_DOCUMENTO_RECEBIDO,
            descricao=f'Triagem de entrada: {documento.titulo}',
            prazo=datetime.utcnow() + timedelta(days=5),
            concluida=False
        )

        db.session.add(tarefa)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_TRIAGEM

        db.session.commit()

        log_debug(f"✅ Tarefa #{tarefa.id} criada para Triador UGQ")
        log_debug(f"📊 Documento status: {documento.status}")
        log_debug("=" * 80)

        return tarefa

    # ========================================================================
    # ETAPA 1: TRIADOR UGQ FAZ TRIAGEM (3 CHECKPOINTS)
    # ========================================================================

    @classmethod
    def triador_devolve_ao_autor(cls, tarefa, motivo):
        """
        Triador UGQ devolve documento ao autor para correção
        (Checkpoint reprovado)

        Args:
            tarefa: Tarefa de triagem
            motivo: Motivo da devolução

        Returns:
            Tarefa de correção criada para o autor
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 1: Triador devolve documento")
        log_debug(f"Motivo: {motivo}")
        log_debug("=" * 80)

        documento = tarefa.documento

        # Marca tarefa de triagem como concluída (reprovada)
        tarefa.aprovado = False
        tarefa.concluida = True
        tarefa.data_conclusao = datetime.utcnow()

        # Cria tarefa de correção para o autor
        tarefa_correcao = Tarefa(
            documento_id=documento.id,
            criador_id=tarefa.responsavel_id,  # Triador
            responsavel_id=documento.criador_id,  # Autor
            tipo_tarefa=Config.TAREFA_REALIZAR_CORRECAO,
            descricao=f'Correção necessária: {motivo}',
            prazo=datetime.utcnow() + timedelta(days=5),
            concluida=False
        )

        db.session.add(tarefa_correcao)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_CORRECAO

        db.session.commit()

        log_debug(f"✅ Tarefa de correção #{tarefa_correcao.id} criada para Autor")
        log_debug(f"📊 Documento status: {documento.status}")
        log_debug("=" * 80)

        return tarefa_correcao

    @classmethod
    def triador_aprova_triagem(cls, tarefa):
        """
        Triador UGQ aprova triagem (todos checkpoints OK)
        HAND-OFF: Cria tarefa "Validar e Codificar" para Validador UGQ

        Args:
            tarefa: Tarefa de triagem

        Returns:
            Tarefa criada para Validador UGQ
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 1: Triador aprova triagem")
        log_debug(f"HAND-OFF: Triador → Validador")
        log_debug("=" * 80)

        documento = tarefa.documento

        # Marca tarefa de triagem como concluída (aprovada)
        tarefa.aprovado = True
        tarefa.concluida = True
        tarefa.data_conclusao = datetime.utcnow()

        # Busca Validador UGQ disponível
        validador = Usuario.query.filter_by(
            perfil=Config.PERFIL_QUALIDADE_VALIDADOR,
            ativo=True
        ).first()

        if not validador:
            log_debug("❌ ERRO: Nenhum Validador UGQ disponível")
            raise ValueError("Nenhum Validador UGQ disponível no sistema")

        log_debug(f"✅ Validador UGQ encontrado: {validador.nome} ({validador.email})")

        # Cria tarefa de validação e codificação
        tarefa_validacao = Tarefa(
            documento_id=documento.id,
            criador_id=tarefa.responsavel_id,  # Triador
            responsavel_id=validador.id,  # Validador
            tipo_tarefa=Config.TAREFA_VALIDAR_CODIFICAR,
            descricao=f'Codificar, validar e preparar: {documento.titulo}',
            prazo=datetime.utcnow() + timedelta(days=7),
            concluida=False
        )

        db.session.add(tarefa_validacao)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_VALIDACAO

        db.session.commit()

        log_debug(f"✅ Tarefa #{tarefa_validacao.id} criada para Validador UGQ")
        log_debug(f"📊 Documento status: {documento.status}")
        log_debug("=" * 80)

        return tarefa_validacao

    # ========================================================================
    # ETAPA 2: VALIDADOR UGQ CODIFICA E VALIDA
    # ========================================================================

    @classmethod
    def gerar_proximo_codigo(cls, tipo, setor):
        """
        Gera próximo código disponível na Lista Mestra
        Formato: TIPO.SETOR-NNN

        Args:
            tipo: Tipo do documento (POP, Manual, Protocolo)
            setor: Setor do documento

        Returns:
            String com código sugerido (ex: POP.OPERACOES-001)
        """
        import re

        # Busca último código do mesmo tipo e setor
        ultimo = ListaMestra.query.filter_by(
            tipo=tipo,
            setor=setor
        ).order_by(ListaMestra.id.desc()).first()

        if ultimo:
            # Extrai número do código (ex: POP.OPERACOES-001 → 001)
            match = re.search(r'-(\d+)$', ultimo.codigo)
            if match:
                numero_atual = int(match.group(1))
                numero_novo = numero_atual + 1
            else:
                numero_novo = 1
        else:
            numero_novo = 1

        # Gera código no formato: TIPO.SETOR-NNN
        codigo = f'{tipo}.{setor}-{numero_novo:03d}'

        log_debug(f"📝 Código sugerido: {codigo}")

        return codigo

    @classmethod
    def validador_codifica_documento(cls, tarefa, codigo_definitivo, versao, observacoes_validacao):
        """
        Validador UGQ codifica documento e atualiza Lista Mestra

        Args:
            tarefa: Tarefa de validação e codificação
            codigo_definitivo: Código gerado (ex: POP.OPERACOES-001)
            versao: Versão do documento (ex: v1.0)
            observacoes_validacao: Observações da validação

        Returns:
            Documento atualizado
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 2: Validador codifica documento")
        log_debug(f"Código: {codigo_definitivo}")
        log_debug(f"Versão: {versao}")
        log_debug("=" * 80)

        documento = tarefa.documento

        # Atualiza documento com código e versão
        documento.codigo_definitivo = codigo_definitivo
        documento.versao = versao
        documento.status = Config.STATUS_VALIDADO

        # Cria registro na Lista Mestra
        registro = ListaMestra(
            codigo=codigo_definitivo,
            tipo=documento.tipo_documento,
            titulo=documento.titulo,
            setor=documento.setor,
            versao=versao,
            data_publicacao=datetime.utcnow(),
            documento_id=documento.id,
            status='EM_APROVACAO'  # Aguardando bloco de assinatura
        )

        db.session.add(registro)

        # Registra validação UGQ
        from app.models.models import ValidacaoUGQ
        validacao = ValidacaoUGQ(
            documento_id=documento.id,
            validador_id=tarefa.responsavel_id,
            data_validacao=datetime.utcnow(),
            declaracao_sei='28538223',  # Modelo padrão
            observacoes=observacoes_validacao
        )

        db.session.add(validacao)

        # Marca tarefa como concluída
        tarefa.aprovado = True
        tarefa.concluida = True
        tarefa.data_conclusao = datetime.utcnow()
        tarefa.parecer = f'Código gerado: {codigo_definitivo} {versao}'

        db.session.commit()

        log_debug(f"✅ Documento codificado: {codigo_definitivo}")
        log_debug(f"✅ Registro criado na Lista Mestra (ID: {registro.id})")
        log_debug(f"✅ Validação UGQ registrada (ID: {validacao.id})")
        log_debug(f"📊 Documento status: {documento.status}")
        log_debug("=" * 80)

        return documento

    # ========================================================================
    # ETAPA 3: VALIDADOR UGQ GERENCIA BLOCO DE ASSINATURA
    # ========================================================================

    @classmethod
    def validador_cria_bloco_assinatura(cls, documento, validador_id, aprovadores_ids, modo, observacoes=''):
        """
        Validador UGQ cria bloco de assinatura e envia para aprovadores

        Args:
            documento: Documento a ser aprovado
            validador_id: ID do Validador UGQ
            aprovadores_ids: Lista de IDs dos aprovadores (em ordem)
            modo: 'sequencial' ou 'concomitante'
            observacoes: Observações para os aprovadores

        Returns:
            BlocoAssinatura criado
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 3: Validador cria Bloco de Assinatura")
        log_debug(f"Modo: {modo}")
        log_debug(f"Aprovadores: {len(aprovadores_ids)}")
        log_debug("=" * 80)

        # Cria bloco de assinatura
        bloco = BlocoAssinatura(
            documento_id=documento.id,
            criador_id=validador_id,
            modo=modo,
            status='Em Andamento',
            observacoes=observacoes
        )

        db.session.add(bloco)
        db.session.flush()  # Gera bloco.id

        log_debug(f"✅ Bloco #{bloco.id} criado")

        # Adiciona aprovadores
        for ordem, aprovador_id in enumerate(aprovadores_ids, start=1):
            item = ItemBlocoAssinatura(
                bloco_id=bloco.id,
                aprovador_id=aprovador_id,
                ordem=ordem,
                status='Pendente'
            )
            db.session.add(item)
            log_debug(f"   📌 Aprovador #{ordem}: ID {aprovador_id}")

        # Cria tarefas para aprovadores
        if modo == 'sequencial':
            # Modo sequencial: apenas primeiro aprovador
            primeiro_item = ItemBlocoAssinatura.query.filter_by(
                bloco_id=bloco.id,
                ordem=1
            ).first()

            tarefa = Tarefa(
                documento_id=documento.id,
                criador_id=validador_id,
                responsavel_id=primeiro_item.aprovador_id,
                tipo_tarefa=f'Assinar Documento [Bloco #{bloco.id}]',
                descricao=f'Assinar: {documento.codigo_definitivo}',
                prazo=datetime.utcnow() + timedelta(days=5),
                concluida=False
            )
            tarefa.set_metadata({
                'bloco_id': bloco.id,
                'item_id': primeiro_item.id,
                'modo': 'sequencial'
            })
            db.session.add(tarefa)

            log_debug(f"✅ Tarefa criada para aprovador #1 (modo sequencial)")

        elif modo == 'concomitante':
            # Modo concomitante: todos aprovadores simultaneamente
            itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).all()
            for item in itens:
                tarefa = Tarefa(
                    documento_id=documento.id,
                    criador_id=validador_id,
                    responsavel_id=item.aprovador_id,
                    tipo_tarefa=f'Assinar Documento [Bloco #{bloco.id}]',
                    descricao=f'Assinar: {documento.codigo_definitivo}',
                    prazo=datetime.utcnow() + timedelta(days=5),
                    concluida=False
                )
                tarefa.set_metadata({
                    'bloco_id': bloco.id,
                    'item_id': item.id,
                    'modo': 'concomitante'
                })
                db.session.add(tarefa)

            log_debug(f"✅ Tarefas criadas para {len(itens)} aprovadores (modo concomitante)")

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_APROVACAO

        db.session.commit()

        log_debug(f"📊 Documento status: {documento.status}")
        log_debug("=" * 80)

        return bloco

    @classmethod
    def aprovador_assina(cls, tarefa, aprovado, parecer):
        """
        Aprovador assina documento (aprova ou reprova)

        Args:
            tarefa: Tarefa de assinatura
            aprovado: True=aprovar, False=reprovar
            parecer: Parecer do aprovador

        Returns:
            Dict com informações sobre o próximo passo
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 3: Aprovador assina documento")
        log_debug(f"Decisão: {'APROVADO' if aprovado else 'REPROVADO'}")
        log_debug("=" * 80)

        metadata = tarefa.get_metadata()
        bloco_id = metadata.get('bloco_id')
        item_id = metadata.get('item_id')
        modo = metadata.get('modo')

        bloco = BlocoAssinatura.query.get(bloco_id)
        item = ItemBlocoAssinatura.query.get(item_id)
        documento = tarefa.documento

        # Registra assinatura/rejeição
        if aprovado:
            item.aprovar(parecer)
            tarefa.aprovado = True
            log_debug(f"✅ Aprovador #{item.ordem} ({item.aprovador.nome}) APROVOU")
            log_debug(f"   Status do item após aprovar: {item.status}")
        else:
            item.reprovar(parecer)
            tarefa.aprovado = False
            log_debug(f"❌ Aprovador #{item.ordem} ({item.aprovador.nome}) REPROVOU")

        tarefa.concluida = True
        tarefa.data_conclusao = datetime.utcnow()
        tarefa.parecer = parecer

        resultado = {}

        if not aprovado:
            # REPROVADO - Cancela bloco e devolve para Validador
            log_debug("🔙 Reprovado! Devolvendo para Validador UGQ")

            bloco.status = 'Reprovado'
            documento.status = Config.STATUS_EM_AJUSTES

            # Cancela todas as outras tarefas do bloco
            Tarefa.query.filter(
                Tarefa.metadata_json.contains(f'"bloco_id": {bloco.id}'),
                Tarefa.concluida == False
            ).update({'concluida': True, 'parecer': 'Cancelada - bloco reprovado'}, synchronize_session=False)

            # Cria tarefa de ajustes para Validador
            validador_id = bloco.criador_id
            tarefa_ajuste = Tarefa(
                documento_id=documento.id,
                criador_id=tarefa.responsavel_id,
                responsavel_id=validador_id,
                tipo_tarefa=Config.TAREFA_REALIZAR_AJUSTES,
                descricao=f'Reprovado por {tarefa.responsavel.nome}: {parecer}',
                prazo=datetime.utcnow() + timedelta(days=5),
                concluida=False
            )
            db.session.add(tarefa_ajuste)

            resultado['proximo'] = 'ajustes'
            resultado['tarefa_id'] = tarefa_ajuste.id

        else:
            # APROVADO - Verifica se todos aprovaram
            # IMPORTANTE: Commit imediato para garantir que as mudanças sejam persistidas
            db.session.commit()
            log_debug("✅ Assinatura commitada no banco de dados")

            if modo == 'sequencial':
                # Cria tarefa para próximo aprovador (se houver)
                proximo_item = ItemBlocoAssinatura.query.filter_by(
                    bloco_id=bloco.id,
                    ordem=item.ordem + 1
                ).first()

                if proximo_item:
                    log_debug(f"➡️  Próximo aprovador: #{proximo_item.ordem}")

                    proxima_tarefa = Tarefa(
                        documento_id=documento.id,
                        criador_id=tarefa.responsavel_id,
                        responsavel_id=proximo_item.aprovador_id,
                        tipo_tarefa=f'Assinar Documento [Bloco #{bloco.id}]',
                        descricao=f'Assinar: {documento.codigo_definitivo}',
                        prazo=datetime.utcnow() + timedelta(days=5),
                        concluida=False
                    )
                    proxima_tarefa.set_metadata({
                        'bloco_id': bloco.id,
                        'item_id': proximo_item.id,
                        'modo': 'sequencial'
                    })
                    db.session.add(proxima_tarefa)
                    db.session.commit()

                    resultado['proximo'] = 'proximo_aprovador'
                    resultado['tarefa_id'] = proxima_tarefa.id
                else:
                    # Último aprovador!
                    log_debug("🎉 Último aprovador! Bloco completo!")
                    cls._finalizar_bloco_assinatura(bloco, documento)
                    resultado['proximo'] = 'publicacao'

            elif modo == 'concomitante':
                # CRÍTICO: Busca itens diretamente do banco para evitar cache
                total_itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).count()
                itens_aprovados = ItemBlocoAssinatura.query.filter_by(
                    bloco_id=bloco.id,
                    status='Aprovado'
                ).count()
                itens_pendentes = ItemBlocoAssinatura.query.filter_by(
                    bloco_id=bloco.id,
                    status='Pendente'
                ).count()

                log_debug(f"📊 Modo concomitante - STATUS DO BLOCO:")
                log_debug(f"   Total de aprovadores: {total_itens}")
                log_debug(f"   Já aprovaram: {itens_aprovados}")
                log_debug(f"   Pendentes: {itens_pendentes}")

                # Debug: Lista todos os itens
                log_debug(f"   DEBUG - Status de cada item:")
                todos_itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).order_by(ItemBlocoAssinatura.ordem).all()
                for item_debug in todos_itens:
                    log_debug(f"      Item #{item_debug.ordem} - {item_debug.aprovador.nome}: {item_debug.status}")

                # Verifica se todos aprovaram usando dados frescos do banco
                if itens_aprovados == total_itens and itens_pendentes == 0:
                    log_debug("🎉 Todos aprovadores assinaram! Bloco completo!")
                    cls._finalizar_bloco_assinatura(bloco, documento)
                    resultado['proximo'] = 'publicacao'
                else:
                    log_debug(f"⏳ Aguardando {itens_pendentes} aprovador(es)")
                    resultado['proximo'] = 'aguardando'
                    resultado['pendentes'] = itens_pendentes

        log_debug("=" * 80)

        return resultado

    @classmethod
    def _finalizar_bloco_assinatura(cls, bloco, documento):
        """
        Finaliza bloco de assinatura e cria tarefa de publicação

        Args:
            bloco: BlocoAssinatura aprovado
            documento: Documento aprovado
        """
        log_debug("=" * 80)
        log_debug("🎉 FINALIZANDO BLOCO DE ASSINATURA")
        log_debug(f"📄 Documento: {documento.codigo_definitivo}")
        log_debug(f"📦 Bloco ID: {bloco.id}")
        log_debug(f"📊 Total de aprovadores: {bloco.total_aprovadores()}")
        log_debug(f"✅ Aprovadores que aprovaram: {bloco.aprovadores_aprovaram()}")
        log_debug("=" * 80)

        bloco.status = 'Aprovado'  # Status consistente com ItemBlocoAssinatura
        bloco.data_conclusao = datetime.utcnow()
        documento.status = Config.STATUS_APROVADO

        # Cria tarefa de publicação para Validador UGQ
        validador_id = bloco.criador_id

        # IMPORTANTE: Busca o Validador para garantir que existe
        validador = Usuario.query.get(validador_id)
        if not validador:
            log_debug("⚠️ Validador não encontrado! Buscando qualquer Validador UGQ ativo...")
            validador = Usuario.query.filter_by(
                perfil=Config.PERFIL_QUALIDADE_VALIDADOR,
                ativo=True
            ).first()
            if validador:
                validador_id = validador.id
            else:
                log_debug("❌ ERRO CRÍTICO: Nenhum Validador UGQ disponível!")
                raise ValueError("Nenhum Validador UGQ disponível para publicação!")

        log_debug(f"👤 Validador encontrado: {validador.nome} (ID: {validador_id})")

        tarefa_publicar = Tarefa(
            documento_id=documento.id,
            criador_id=validador_id,
            responsavel_id=validador_id,
            tipo_tarefa=Config.TAREFA_PUBLICAR_APROVADO,
            descricao=f'Publicar documento aprovado: {documento.codigo_definitivo}',
            prazo=datetime.utcnow() + timedelta(days=3),
            concluida=False,
            prioridade='alta'
        )
        db.session.add(tarefa_publicar)

        # CRÍTICO: Commit imediato para garantir que a tarefa seja criada
        db.session.commit()

        log_debug(f"✅ TAREFA DE PUBLICAÇÃO CRIADA E COMMITADA!")
        log_debug(f"   ID da tarefa: #{tarefa_publicar.id}")
        log_debug(f"   Responsável: {validador.nome} (ID: {validador_id})")
        log_debug(f"   Tipo: {Config.TAREFA_PUBLICAR_APROVADO}")
        log_debug(f"   Prazo: {tarefa_publicar.prazo.strftime('%d/%m/%Y')}")
        log_debug("=" * 80)

    # ========================================================================
    # ETAPA 4: VALIDADOR UGQ PUBLICA DOCUMENTO
    # ========================================================================

    @classmethod
    def validador_publica_documento(cls, tarefa):
        """
        Validador UGQ publica documento aprovado

        Args:
            tarefa: Tarefa de publicação

        Returns:
            Documento publicado
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 4: Validador publica documento")
        log_debug("=" * 80)

        documento = tarefa.documento

        # NOVO: Gera PDF de assinaturas ANTES de publicar
        bloco = BlocoAssinatura.query.filter_by(
            documento_id=documento.id
        ).order_by(BlocoAssinatura.id.desc()).first()

        if bloco:
            pdf_assinaturas = cls._gerar_pdf_assinaturas(documento, bloco)
            documento.arquivo_final = pdf_assinaturas
            log_debug(f"📄 PDF de assinaturas gerado: {pdf_assinaturas}")

        # Atualiza status do documento
        documento.status = Config.STATUS_PUBLICADO
        documento.data_publicacao = datetime.utcnow()

        # Atualiza Lista Mestra para VIGENTE
        registro = ListaMestra.query.filter_by(
            documento_id=documento.id
        ).first()

        if registro:
            registro.status = 'VIGENTE'
            log_debug(f"✅ Lista Mestra atualizada: {registro.codigo} → VIGENTE")

        # Arquiva versão anterior (se houver)
        if documento.versao_anterior_id:
            doc_antigo = Documento.query.get(documento.versao_anterior_id)
            if doc_antigo:
                doc_antigo.status = Config.STATUS_OBSOLETO

                registro_antigo = ListaMestra.query.filter_by(
                    documento_id=doc_antigo.id
                ).first()
                if registro_antigo:
                    registro_antigo.status = 'ANTIGO'

                log_debug(f"📦 Versão anterior arquivada: {doc_antigo.codigo}")

        # Marca tarefa como concluída
        tarefa.aprovado = True
        tarefa.concluida = True
        tarefa.data_conclusao = datetime.utcnow()
        tarefa.parecer = f'Publicado em {datetime.utcnow().strftime("%d/%m/%Y %H:%M")}'

        # NOVO: Notifica APROVADORES e AUTOR sobre publicação
        bloco = BlocoAssinatura.query.filter_by(
            documento_id=documento.id
        ).order_by(BlocoAssinatura.id.desc()).first()

        if bloco:
            # 1. Notifica todos os aprovadores que assinaram
            for item in bloco.itens:
                if item.status == 'Aprovado':  # Status consistente
                    tarefa_notificacao_aprovador = Tarefa(
                        documento_id=documento.id,
                        criador_id=tarefa.responsavel_id,  # Validador
                        responsavel_id=item.aprovador_id,  # Aprovador que assinou
                        tipo_tarefa='Notificação de Publicação',
                        descricao=f'✅ Documento que você aprovou foi publicado: {documento.codigo_definitivo} {documento.versao}',
                        prazo=datetime.utcnow() + timedelta(days=3),
                        concluida=False,
                        prioridade='baixa'
                    )
                    db.session.add(tarefa_notificacao_aprovador)
                    log_debug(f"📬 Notificação enviada para aprovador: {item.aprovador.nome}")

        # 2. Notifica o AUTOR do documento
        autor = documento.criador
        if autor:
            tarefa_notificacao_autor = Tarefa(
                documento_id=documento.id,
                criador_id=tarefa.responsavel_id,  # Validador
                responsavel_id=autor.id,  # Autor do documento
                tipo_tarefa='Notificação de Publicação',
                descricao=f'✅ Seu documento foi publicado: {documento.codigo_definitivo} {documento.versao}',
                prazo=datetime.utcnow() + timedelta(days=3),
                concluida=False,
                prioridade='baixa'
            )
            db.session.add(tarefa_notificacao_autor)
            log_debug(f"📬 Notificação enviada para autor: {autor.nome}")

        db.session.commit()

        log_debug(f"✅ Documento {documento.codigo_definitivo} publicado!")
        log_debug(f"📊 Status: {documento.status}")
        log_debug("🎉 FIM DO WORKFLOW UGQ")
        log_debug("=" * 80)

        return documento

    # ========================================================================
    # GERAÇÃO DE PDF DE ASSINATURAS
    # ========================================================================

    @classmethod
    def _gerar_pdf_assinaturas(cls, documento, bloco):
        """
        Gera PDF formatado com todas as assinaturas do documento

        Args:
            documento: Documento aprovado
            bloco: BlocoAssinatura com os itens assinados

        Returns:
            String com nome do arquivo PDF gerado
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import os

        # Define nome do arquivo
        filename = f"assinaturas_{documento.codigo_definitivo.replace('.', '_')}.pdf"
        filepath = os.path.join('uploads', 'assinaturas', filename)

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Cria documento PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Estilo customizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # Estilo para subtítulo
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        # Título
        elements.append(Paragraph("FOLHA DE ASSINATURAS", title_style))
        elements.append(Paragraph(f"Documento: {documento.codigo_definitivo}", subtitle_style))
        elements.append(Spacer(1, 0.5*cm))

        # Informações do documento
        data_info = [
            ['Título:', documento.titulo],
            ['Tipo:', documento.tipo_documento],
            ['Setor:', documento.setor],
            ['Versão:', documento.versao],
            ['Data de Aprovação:', bloco.data_conclusao.strftime('%d/%m/%Y %H:%M') if bloco.data_conclusao else '---']
        ]

        table_info = Table(data_info, colWidths=[4*cm, 12*cm])
        table_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table_info)
        elements.append(Spacer(1, 1*cm))

        # Título da seção de assinaturas
        elements.append(Paragraph(f"ASSINATURAS ({bloco.modo.upper()})", title_style))
        elements.append(Spacer(1, 0.5*cm))

        # Tabela de assinaturas
        data_assinaturas = [
            ['Ordem', 'Nome', 'Cargo', 'Data/Hora', 'Decisão', 'Parecer']
        ]

        for item in bloco.itens.order_by(ItemBlocoAssinatura.ordem):
            aprovador = item.aprovador
            decisao = '✅ APROVADO' if item.status == 'Aprovado' else '❌ REPROVADO' if item.status == 'Reprovado' else '⏳ PENDENTE'
            data_assinatura = item.data_assinatura.strftime('%d/%m/%Y %H:%M') if item.data_assinatura else '---'
            parecer_resumido = (item.parecer[:50] + '...') if item.parecer and len(item.parecer) > 50 else (item.parecer or '---')

            data_assinaturas.append([
                str(item.ordem),
                aprovador.nome,
                'Gerente',  # Perfil
                data_assinatura,
                decisao,
                parecer_resumido
            ])

        table_assinaturas = Table(data_assinaturas, colWidths=[1.5*cm, 4*cm, 3*cm, 3.5*cm, 3*cm, 5*cm])
        table_assinaturas.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Corpo
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Ordem centralizada
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Linhas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))

        elements.append(table_assinaturas)
        elements.append(Spacer(1, 1*cm))

        # Rodapé
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )

        elements.append(Paragraph(
            f"Documento gerado automaticamente pelo Sistema GED UGQ em {datetime.utcnow().strftime('%d/%m/%Y às %H:%M')}",
            footer_style
        ))

        # Constrói PDF
        doc.build(elements)

        log_debug(f"📄 PDF de assinaturas salvo em: {filepath}")

        return filename
