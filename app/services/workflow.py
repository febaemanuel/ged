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
from app.models import db, Tarefa, Documento, Usuario, ListaMestra, BlocoAssinatura, ItemBlocoAssinatura, Notificacao
from config import Config
import logging
import json

logger = logging.getLogger(__name__)

# Import do serviço de email
try:
    from app.services.email_service import EmailService
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    logger.warning("EmailService não disponível")

# Import do serviço de WhatsApp (Evolution API)
try:
    from app.services.evolution_api_service import EvolutionAPIService as WhatsAppService
    WHATSAPP_ENABLED = True
except ImportError:
    WHATSAPP_ENABLED = False
    logger.warning("WhatsAppService não disponível")


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

        # Verifica método de confirmação configurado
        metodo = 'ambos'  # Padrão
        if WHATSAPP_ENABLED:
            from app.models import ConfiguracaoWhatsApp
            whatsapp_config = ConfiguracaoWhatsApp.get_config()
            metodo = whatsapp_config.metodo_confirmacao or 'ambos'
            log_debug(f"📬 Método de confirmação: {metodo}")

        # Envia e-mail para o Triador UGQ (se configurado)
        if EMAIL_ENABLED and metodo in ['email', 'ambos']:
            EmailService.enviar_notificacao_tarefa(
                usuario_id=triador.id,
                tipo_tarefa=Config.TAREFA_DOCUMENTO_RECEBIDO,
                documento_titulo=documento.titulo,
                documento_codigo=documento.codigo_provisorio
            )
            log_debug(f"📧 E-mail enviado para Triador UGQ: {triador.email}")

        # Envia WhatsApp para o Triador UGQ (se configurado)
        if WHATSAPP_ENABLED and metodo in ['whatsapp', 'ambos']:
            whatsapp_service = WhatsAppService()
            if whatsapp_service.esta_ativo():
                sucesso, resultado = whatsapp_service.enviar_notificacao_tarefa(triador, tarefa)
                if sucesso:
                    log_debug(f"📱 WhatsApp enviado para Triador UGQ: {triador.telefone}")
                else:
                    log_debug(f"⚠️ Falha ao enviar WhatsApp: {resultado}")

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

        # Envia e-mail para o Autor
        if EMAIL_ENABLED and documento.criador:
            EmailService.enviar_notificacao_documento_devolvido(
                usuario_id=documento.criador_id,
                documento_titulo=documento.titulo,
                documento_codigo=documento.codigo_provisorio or documento.codigo_unico,
                motivo=motivo
            )
            log_debug(f"📧 E-mail enviado para Autor: {documento.criador.email}")

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
    def gerar_proximo_codigo(cls, tipo, setor, abrangencia):
        """
        Gera próximo código disponível na Lista Mestra
        Formato: TIPO.SETOR-ABRANGENCIA.NNN

        Args:
            tipo: Tipo do documento (POP, Manual, Protocolo, Política, Regimento, Regulamento)
            setor: Setor do documento
            abrangencia: Abrangência do documento (CHUFC, HUWC, MEAC, etc)

        Returns:
            String com código sugerido (ex: POP.UGQ-CHUFC.001)
        """
        import re

        # Busca último código do mesmo tipo, setor e abrangência
        ultimo = ListaMestra.query.filter_by(
            tipo=tipo,
            setor=setor,
            abrangencia=abrangencia
        ).order_by(ListaMestra.id.desc()).first()

        if ultimo:
            # Extrai número do código (ex: POP.UGQ-CHUFC.001 → 001)
            match = re.search(r'\.(\d+)$', ultimo.codigo)
            if match:
                numero_atual = int(match.group(1))
                numero_novo = numero_atual + 1
            else:
                numero_novo = 1
        else:
            numero_novo = 1

        # Gera código no formato: TIPO.SETOR-ABRANGENCIA.NNN
        codigo = f'{tipo}.{setor}-{abrangencia}.{numero_novo:03d}'

        log_debug(f"📝 Código sugerido: {codigo}")

        return codigo

    @classmethod
    def calcular_data_vencimento(cls, tipo_documento, data_publicacao=None):
        """
        Calcula data de vencimento baseada no tipo de documento

        Regras:
        - Política, Regimento e Regulamento: 4 anos
        - Outros documentos: 2 anos

        Args:
            tipo_documento: Tipo do documento
            data_publicacao: Data de publicação (default: agora)

        Returns:
            Data de vencimento
        """
        if data_publicacao is None:
            data_publicacao = datetime.utcnow()

        # Documentos que têm validade de 4 anos
        if tipo_documento in Config.TIPOS_VALIDADE_4_ANOS:
            anos = 4
        else:
            anos = 2

        # Calcula data de vencimento
        data_vencimento = data_publicacao + timedelta(days=365 * anos)

        log_debug(f"📅 Validade calculada: {anos} anos - Vencimento: {data_vencimento.strftime('%d/%m/%Y')}")

        return data_vencimento

    @classmethod
    def validador_codifica_documento(cls, tarefa, codigo_definitivo, versao, observacoes_validacao, abrangencia):
        """
        Validador UGQ codifica documento e atualiza Lista Mestra

        Args:
            tarefa: Tarefa de validação e codificação
            codigo_definitivo: Código gerado (ex: POP.UGQ-CHUFC.001)
            versao: Versão do documento (ex: v1.0)
            observacoes_validacao: Observações da validação
            abrangencia: Abrangência do documento (CHUFC, HUWC, MEAC, etc)

        Returns:
            Documento atualizado
        """
        log_debug("=" * 80)
        log_debug(f"ETAPA 2: Validador codifica documento")
        log_debug(f"Código: {codigo_definitivo}")
        log_debug(f"Versão: {versao}")
        log_debug(f"Abrangência: {abrangencia}")
        log_debug("=" * 80)

        documento = tarefa.documento

        # Atualiza documento com código, versão e abrangência
        documento.codigo_definitivo = codigo_definitivo
        documento.versao = versao
        documento.abrangencia = abrangencia
        documento.status = Config.STATUS_VALIDADO

        # Cria registro na Lista Mestra
        registro = ListaMestra(
            codigo=codigo_definitivo,
            tipo=documento.tipo_documento,
            titulo=documento.titulo,
            setor=documento.setor,
            abrangencia=abrangencia,
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

        # Envia e-mail para o Autor informando que o documento foi validado
        if EMAIL_ENABLED and documento.criador:
            EmailService.enviar_notificacao_documento_validado(
                usuario_id=documento.criador_id,
                documento_titulo=documento.titulo,
                codigo_definitivo=codigo_definitivo,
                versao=versao
            )
            log_debug(f"📧 E-mail enviado para Autor: {documento.criador.email}")

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

        # Verifica método de confirmação configurado
        metodo = 'ambos'  # Padrão
        if WHATSAPP_ENABLED:
            from app.models import ConfiguracaoWhatsApp
            whatsapp_config = ConfiguracaoWhatsApp.get_config()
            metodo = whatsapp_config.metodo_confirmacao or 'ambos'
            log_debug(f"📬 Método de confirmação: {metodo}")

        # Envia e-mails para os aprovadores (se configurado)
        if EMAIL_ENABLED and metodo in ['email', 'ambos']:
            if modo == 'sequencial':
                # Envia apenas para o primeiro aprovador
                primeiro_item = ItemBlocoAssinatura.query.filter_by(
                    bloco_id=bloco.id,
                    ordem=1
                ).first()
                if primeiro_item:
                    EmailService.enviar_notificacao_tarefa(
                        usuario_id=primeiro_item.aprovador_id,
                        tipo_tarefa='Assinar Documento',
                        documento_titulo=documento.titulo,
                        documento_codigo=documento.codigo_definitivo
                    )
                    log_debug(f"📧 E-mail enviado para aprovador #1: ID {primeiro_item.aprovador_id}")
            elif modo == 'concomitante':
                # Envia para todos os aprovadores
                itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).all()
                for idx, item in enumerate(itens, 1):
                    EmailService.enviar_notificacao_tarefa(
                        usuario_id=item.aprovador_id,
                        tipo_tarefa='Assinar Documento',
                        documento_titulo=documento.titulo,
                        documento_codigo=documento.codigo_definitivo
                    )
                    log_debug(f"📧 E-mail enviado para aprovador #{idx}: ID {item.aprovador_id}")

        # Envia WhatsApp para os aprovadores (se configurado)
        if WHATSAPP_ENABLED and metodo in ['whatsapp', 'ambos']:
            whatsapp_service = WhatsAppService()
            if whatsapp_service.esta_ativo():
                if modo == 'sequencial':
                    # Envia apenas para o primeiro aprovador
                    primeiro_item = ItemBlocoAssinatura.query.filter_by(
                        bloco_id=bloco.id,
                        ordem=1
                    ).first()
                    if primeiro_item:
                        # Cria tarefa temporária para enviar notificação
                        tarefa_temp = Tarefa.query.filter_by(
                            documento_id=documento.id,
                            responsavel_id=primeiro_item.aprovador_id,
                            concluida=False
                        ).filter(
                            Tarefa.tipo_tarefa.like(f'%Bloco #{bloco.id}%')
                        ).first()

                        if tarefa_temp:
                            sucesso, resultado = whatsapp_service.enviar_notificacao_tarefa(primeiro_item.aprovador, tarefa_temp)
                            if sucesso:
                                log_debug(f"📱 WhatsApp enviado para aprovador #1: {primeiro_item.aprovador.telefone}")
                            else:
                                log_debug(f"⚠️ Falha ao enviar WhatsApp para aprovador #1: {resultado}")

                elif modo == 'concomitante':
                    # Envia para todos os aprovadores
                    itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).all()
                    for idx, item in enumerate(itens, 1):
                        # Busca tarefa correspondente
                        tarefa_item = Tarefa.query.filter_by(
                            documento_id=documento.id,
                            responsavel_id=item.aprovador_id,
                            concluida=False
                        ).filter(
                            Tarefa.tipo_tarefa.like(f'%Bloco #{bloco.id}%')
                        ).first()

                        if tarefa_item:
                            sucesso, resultado = whatsapp_service.enviar_notificacao_tarefa(item.aprovador, tarefa_item)
                            if sucesso:
                                log_debug(f"📱 WhatsApp enviado para aprovador #{idx}: {item.aprovador.telefone}")
                            else:
                                log_debug(f"⚠️ Falha ao enviar WhatsApp para aprovador #{idx}: {resultado}")

        log_debug("=" * 80)

        return bloco

    @classmethod
    def validador_devolve_para_triador(cls, documento, validador_id, motivo):
        """
        Validador UGQ devolve documento para Triador UGQ

        Args:
            documento: Documento a ser devolvido
            validador_id: ID do Validador UGQ
            motivo: Motivo da devolução

        Returns:
            Tarefa criada para o Triador
        """
        log_debug("=" * 80)
        log_debug(f"Validador devolve documento para Triador")
        log_debug(f"Motivo: {motivo}")
        log_debug("=" * 80)

        # Busca Triador UGQ disponível
        triador = Usuario.query.filter_by(
            perfil=Config.PERFIL_QUALIDADE_TRIADOR,
            ativo=True
        ).first()

        if not triador:
            log_debug("❌ ERRO: Nenhum Triador UGQ disponível")
            raise ValueError("Nenhum Triador UGQ disponível no sistema")

        # Cria tarefa de nova triagem
        tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=validador_id,
            responsavel_id=triador.id,
            tipo_tarefa=Config.TAREFA_DOCUMENTO_RECEBIDO,
            descricao=f'Retriagem solicitada pelo Validador: {motivo}',
            prazo=datetime.utcnow() + timedelta(days=5),
            concluida=False
        )

        db.session.add(tarefa)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_TRIAGEM

        db.session.commit()

        log_debug(f"✅ Documento devolvido para Triador UGQ")
        log_debug("=" * 80)

        return tarefa

    @classmethod
    def validador_devolve_para_autor(cls, documento, validador_id, motivo):
        """
        Validador UGQ devolve documento diretamente para Autor

        Args:
            documento: Documento a ser devolvido
            validador_id: ID do Validador UGQ
            motivo: Motivo da devolução

        Returns:
            Tarefa criada para o Autor
        """
        log_debug("=" * 80)
        log_debug(f"Validador devolve documento para Autor")
        log_debug(f"Motivo: {motivo}")
        log_debug("=" * 80)

        # Cria tarefa de correção para o autor
        tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=validador_id,
            responsavel_id=documento.criador_id,
            tipo_tarefa=Config.TAREFA_REALIZAR_CORRECAO,
            descricao=f'Correção solicitada pelo Validador: {motivo}',
            prazo=datetime.utcnow() + timedelta(days=5),
            concluida=False
        )

        db.session.add(tarefa)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_CORRECAO

        db.session.commit()

        log_debug(f"✅ Documento devolvido para Autor")
        log_debug("=" * 80)

        return tarefa

    @classmethod
    def aprovador_devolve_para_validador(cls, tarefa, motivo):
        """
        Aprovador devolve documento para Validador UGQ

        Args:
            tarefa: Tarefa de assinatura
            motivo: Motivo da devolução

        Returns:
            Tarefa criada para o Validador
        """
        log_debug("=" * 80)
        log_debug(f"Aprovador devolve documento para Validador")
        log_debug(f"Motivo: {motivo}")
        log_debug("=" * 80)

        metadata = tarefa.get_metadata()
        bloco_id = metadata.get('bloco_id')

        bloco = BlocoAssinatura.query.get(bloco_id)
        documento = tarefa.documento

        # Cancela bloco
        bloco.status = 'Devolvido'

        # Cancela todas as outras tarefas do bloco
        Tarefa.query.filter(
            Tarefa.metadata_json.contains(f'"bloco_id": {bloco.id}'),
            Tarefa.concluida == False
        ).update({'concluida': True, 'parecer': 'Cancelada - documento devolvido'}, synchronize_session=False)

        # Marca tarefa atual como concluída
        tarefa.concluida = True
        tarefa.aprovado = False
        tarefa.data_conclusao = datetime.utcnow()
        tarefa.parecer = f'Devolvido: {motivo}'

        # Cria tarefa de ajustes para Validador
        validador_id = bloco.criador_id
        tarefa_ajuste = Tarefa(
            documento_id=documento.id,
            criador_id=tarefa.responsavel_id,
            responsavel_id=validador_id,
            tipo_tarefa=Config.TAREFA_REALIZAR_AJUSTES,
            descricao=f'Devolvido por {tarefa.responsavel.nome}: {motivo}',
            prazo=datetime.utcnow() + timedelta(days=5),
            concluida=False
        )

        db.session.add(tarefa_ajuste)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_AJUSTES

        db.session.commit()

        log_debug(f"✅ Documento devolvido para Validador UGQ")
        log_debug("=" * 80)

        return tarefa_ajuste

    @classmethod
    def aprovador_assina(cls, tarefa, aprovado, parecer, senha=None, ip_address=None, user_agent=None):
        """
        Aprovador assina documento (aprova ou reprova) com verificação de senha

        Args:
            tarefa: Tarefa de assinatura
            aprovado: True=aprovar, False=reprovar
            parecer: Parecer do aprovador
            senha: Senha do aprovador para confirmação (obrigatória)
            ip_address: IP de onde foi assinado
            user_agent: Navegador/sistema usado

        Returns:
            Dict com informações sobre o próximo passo
        """
        import sys
        import hashlib
        print("=" * 80, file=sys.stderr, flush=True)
        print(f"[WORKFLOW] ETAPA 3: Aprovador assina documento", file=sys.stderr, flush=True)
        print(f"[WORKFLOW] Decisão: {'APROVADO' if aprovado else 'REPROVADO'}", file=sys.stderr, flush=True)
        print("=" * 80, file=sys.stderr, flush=True)

        log_debug("=" * 80)
        log_debug(f"ETAPA 3: Aprovador assina documento")
        log_debug(f"Decisão: {'APROVADO' if aprovado else 'REPROVADO'}")
        log_debug("=" * 80)

        metadata = tarefa.get_metadata()
        bloco_id = metadata.get('bloco_id')
        item_id = metadata.get('item_id')
        modo = metadata.get('modo')

        print(f"[WORKFLOW] Bloco ID: {bloco_id}, Item ID: {item_id}, Modo: {modo}", file=sys.stderr, flush=True)

        bloco = BlocoAssinatura.query.get(bloco_id)
        item = ItemBlocoAssinatura.query.get(item_id)
        documento = tarefa.documento

        print(f"[WORKFLOW] Aprovador: {item.aprovador.nome}, Ordem: {item.ordem}", file=sys.stderr, flush=True)

        # VERIFICAÇÃO DE SENHA OBRIGATÓRIA
        if not senha:
            log_debug("❌ ERRO: Senha não fornecida para assinatura")
            raise ValueError("Senha é obrigatória para assinar documento")

        # Verifica se a senha está correta
        from werkzeug.security import check_password_hash
        aprovador = item.aprovador
        if not check_password_hash(aprovador.senha_hash, senha):
            log_debug(f"❌ ERRO: Senha incorreta para {aprovador.nome}")
            raise ValueError("Senha incorreta")

        log_debug(f"✅ Senha verificada para {aprovador.nome}")

        # Gera hash da assinatura (SHA-256 de: documento_id + aprovador_id + timestamp + parecer)
        timestamp = datetime.utcnow().isoformat()
        dados_assinatura = f"{documento.id}|{aprovador.id}|{timestamp}|{parecer}"
        assinatura_hash = hashlib.sha256(dados_assinatura.encode('utf-8')).hexdigest()

        log_debug(f"🔐 Hash da assinatura gerado: {assinatura_hash[:16]}...")

        # Registra assinatura/rejeição com dados de autenticação
        if aprovado:
            item.aprovar(parecer, senha_hash=assinatura_hash, ip_address=ip_address, user_agent=user_agent)
            tarefa.aprovado = True
            log_debug(f"✅ Aprovador #{item.ordem} ({item.aprovador.nome}) APROVOU")
            log_debug(f"   Status do item após aprovar: {item.status}")
            log_debug(f"   IP: {ip_address}")
            log_debug(f"   User-Agent: {user_agent}")
        else:
            item.reprovar(parecer, senha_hash=assinatura_hash, ip_address=ip_address, user_agent=user_agent)
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
                import sys
                print(f"[WORKFLOW] 🔍 VERIFICANDO STATUS DO BLOCO CONCOMITANTE", file=sys.stderr, flush=True)

                total_itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).count()
                itens_aprovados = ItemBlocoAssinatura.query.filter_by(
                    bloco_id=bloco.id,
                    status='Aprovado'
                ).count()
                itens_pendentes = ItemBlocoAssinatura.query.filter_by(
                    bloco_id=bloco.id,
                    status='Pendente'
                ).count()

                print(f"[WORKFLOW] Total de aprovadores: {total_itens}", file=sys.stderr, flush=True)
                print(f"[WORKFLOW] Já aprovaram: {itens_aprovados}", file=sys.stderr, flush=True)
                print(f"[WORKFLOW] Pendentes: {itens_pendentes}", file=sys.stderr, flush=True)

                log_debug(f"📊 Modo concomitante - STATUS DO BLOCO:")
                log_debug(f"   Total de aprovadores: {total_itens}")
                log_debug(f"   Já aprovaram: {itens_aprovados}")
                log_debug(f"   Pendentes: {itens_pendentes}")

                # Debug: Lista todos os itens
                log_debug(f"   DEBUG - Status de cada item:")
                todos_itens = ItemBlocoAssinatura.query.filter_by(bloco_id=bloco.id).order_by(ItemBlocoAssinatura.ordem).all()
                for item_debug in todos_itens:
                    status_msg = f"Item #{item_debug.ordem} - {item_debug.aprovador.nome}: {item_debug.status}"
                    log_debug(f"      {status_msg}")
                    print(f"[WORKFLOW]    {status_msg}", file=sys.stderr, flush=True)

                # Verifica se todos aprovaram usando dados frescos do banco
                print(f"[WORKFLOW] 🧮 Verificando: {itens_aprovados} == {total_itens} and {itens_pendentes} == 0", file=sys.stderr, flush=True)

                if itens_aprovados == total_itens and itens_pendentes == 0:
                    print(f"[WORKFLOW] 🎉 TODOS APROVARAM! Chamando _finalizar_bloco_assinatura", file=sys.stderr, flush=True)
                    log_debug("🎉 Todos aprovadores assinaram! Bloco completo!")

                    try:
                        cls._finalizar_bloco_assinatura(bloco, documento)
                        print(f"[WORKFLOW] ✅ _finalizar_bloco_assinatura executado com sucesso", file=sys.stderr, flush=True)
                        resultado['proximo'] = 'publicacao'
                    except Exception as e:
                        print(f"[WORKFLOW] ❌ ERRO em _finalizar_bloco_assinatura: {str(e)}", file=sys.stderr, flush=True)
                        import traceback
                        traceback.print_exc(file=sys.stderr)
                        raise
                else:
                    print(f"[WORKFLOW] ⏳ Aguardando {itens_pendentes} aprovador(es)", file=sys.stderr, flush=True)
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
        import sys
        print("=" * 80, file=sys.stderr, flush=True)
        print("[WORKFLOW] 🎉 FINALIZANDO BLOCO DE ASSINATURA", file=sys.stderr, flush=True)
        print(f"[WORKFLOW] 📄 Documento: {documento.codigo_definitivo}", file=sys.stderr, flush=True)
        print(f"[WORKFLOW] 📦 Bloco ID: {bloco.id}", file=sys.stderr, flush=True)
        print("=" * 80, file=sys.stderr, flush=True)

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
        print(f"[WORKFLOW] 👤 Validador: {validador.nome} (ID: {validador_id})", file=sys.stderr, flush=True)
        print(f"[WORKFLOW] 📝 Criando tarefa de publicação...", file=sys.stderr, flush=True)

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

        print(f"[WORKFLOW] ➕ Tarefa criada (ainda não adicionada à sessão)", file=sys.stderr, flush=True)
        print(f"[WORKFLOW] 📋 Detalhes da tarefa:", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    - documento_id: {documento.id}", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    - criador_id: {validador_id}", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    - responsavel_id: {validador_id}", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    - tipo_tarefa: {Config.TAREFA_PUBLICAR_APROVADO}", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    - concluida: False", file=sys.stderr, flush=True)

        db.session.add(tarefa_publicar)
        print(f"[WORKFLOW] ✅ Tarefa adicionada à sessão", file=sys.stderr, flush=True)

        # CRÍTICO: Commit imediato para garantir que a tarefa seja criada
        print(f"[WORKFLOW] 💾 Fazendo commit...", file=sys.stderr, flush=True)
        db.session.commit()
        print(f"[WORKFLOW] ✅ COMMIT REALIZADO COM SUCESSO!", file=sys.stderr, flush=True)

        print(f"[WORKFLOW] 🎊 TAREFA DE PUBLICAÇÃO CRIADA E COMMITADA!", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    ID da tarefa: #{tarefa_publicar.id}", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    Responsável: {validador.nome} (ID: {validador_id})", file=sys.stderr, flush=True)
        print(f"[WORKFLOW]    Tipo: {Config.TAREFA_PUBLICAR_APROVADO}", file=sys.stderr, flush=True)
        print("=" * 80, file=sys.stderr, flush=True)

        log_debug(f"✅ TAREFA DE PUBLICAÇÃO CRIADA E COMMITADA!")
        log_debug(f"   ID da tarefa: #{tarefa_publicar.id}")
        log_debug(f"   Responsável: {validador.nome} (ID: {validador_id})")
        log_debug(f"   Tipo: {Config.TAREFA_PUBLICAR_APROVADO}")
        log_debug(f"   Prazo: {tarefa_publicar.prazo.strftime('%d/%m/%Y')}")

        # Verifica método de confirmação configurado
        metodo = 'ambos'  # Padrão
        if WHATSAPP_ENABLED:
            from app.models import ConfiguracaoWhatsApp
            whatsapp_config = ConfiguracaoWhatsApp.get_config()
            metodo = whatsapp_config.metodo_confirmacao or 'ambos'
            log_debug(f"📬 Método de confirmação: {metodo}")

        # Envia e-mail para o Validador UGQ (se configurado)
        if EMAIL_ENABLED and metodo in ['email', 'ambos']:
            EmailService.enviar_notificacao_tarefa(
                usuario_id=validador_id,
                tipo_tarefa=Config.TAREFA_PUBLICAR_APROVADO,
                documento_titulo=documento.titulo,
                documento_codigo=documento.codigo_definitivo
            )
            log_debug(f"📧 E-mail enviado para Validador UGQ: {validador.email}")

        # Envia WhatsApp para o Validador UGQ (se configurado)
        if WHATSAPP_ENABLED and metodo in ['whatsapp', 'ambos']:
            whatsapp_service = WhatsAppService()
            if whatsapp_service.esta_ativo():
                sucesso, resultado = whatsapp_service.enviar_notificacao_tarefa(validador, tarefa_publicar)
                if sucesso:
                    log_debug(f"📱 WhatsApp enviado para Validador UGQ: {validador.telefone}")
                    print(f"[WORKFLOW] 📱 WhatsApp enviado para Validador UGQ: {validador.telefone}", file=sys.stderr, flush=True)
                else:
                    log_debug(f"⚠️ Falha ao enviar WhatsApp: {resultado}")
                    print(f"[WORKFLOW] ⚠️ Falha ao enviar WhatsApp: {resultado}", file=sys.stderr, flush=True)

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

        # Calcula data de vencimento baseada no tipo de documento
        documento.data_vencimento = cls.calcular_data_vencimento(
            tipo_documento=documento.tipo_documento,
            data_publicacao=documento.data_publicacao
        )

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

        # NOVO: Notifica APROVADORES e AUTOR sobre publicação (usando Notificações, NÃO tarefas)
        bloco = BlocoAssinatura.query.filter_by(
            documento_id=documento.id
        ).order_by(BlocoAssinatura.id.desc()).first()

        if bloco:
            # 1. Notifica todos os aprovadores que assinaram
            for item in bloco.itens:
                if item.status == 'Aprovado':  # Status consistente
                    notificacao = Notificacao(
                        usuario_id=item.aprovador_id,
                        documento_id=documento.id,
                        tipo='publicacao',
                        titulo='Documento Publicado',
                        mensagem=f'✅ O documento que você aprovou foi publicado: {documento.codigo_definitivo} {documento.versao}'
                    )
                    db.session.add(notificacao)
                    log_debug(f"📬 Notificação enviada para aprovador: {item.aprovador.nome}")

                    # Envia e-mail para o aprovador
                    if EMAIL_ENABLED:
                        EmailService.enviar_notificacao_documento_publicado(
                            usuario_id=item.aprovador_id,
                            documento_titulo=documento.titulo,
                            documento_codigo=documento.codigo_definitivo,
                            versao=documento.versao
                        )
                        log_debug(f"📧 E-mail enviado para aprovador: {item.aprovador.email}")

        # 2. Notifica o AUTOR do documento
        autor = documento.criador
        if autor:
            notificacao_autor = Notificacao(
                usuario_id=autor.id,
                documento_id=documento.id,
                tipo='publicacao',
                titulo='Seu Documento foi Publicado',
                mensagem=f'🎉 Seu documento foi publicado com sucesso: {documento.codigo_definitivo} {documento.versao}'
            )
            db.session.add(notificacao_autor)
            log_debug(f"📬 Notificação enviada para autor: {autor.nome}")

            # Envia e-mail para o autor
            if EMAIL_ENABLED:
                EmailService.enviar_notificacao_documento_publicado(
                    usuario_id=autor.id,
                    documento_titulo=documento.titulo,
                    documento_codigo=documento.codigo_definitivo,
                    versao=documento.versao
                )
                log_debug(f"📧 E-mail enviado para autor: {autor.email}")

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
        filepath = os.path.join(Config.ASSINATURAS_FOLDER, filename)

        # Cria diretório se não existir
        os.makedirs(Config.ASSINATURAS_FOLDER, exist_ok=True)

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
            ['#', 'Nome', 'Data/Hora', 'Decisão', 'Hash (Assinatura Digital)']
        ]

        for item in sorted(bloco.itens, key=lambda x: x.ordem):
            aprovador = item.aprovador
            decisao = '✅ APROVADO' if item.status == 'Aprovado' else '❌ REPROVADO' if item.status == 'Reprovado' else '⏳ PENDENTE'
            data_assinatura = item.data_assinatura.strftime('%d/%m/%Y %H:%M') if item.data_assinatura else '---'

            # Hash resumido (primeiros e últimos 8 caracteres)
            hash_display = '---'
            if item.assinatura_hash:
                hash_display = f"{item.assinatura_hash[:8]}...{item.assinatura_hash[-8:]}"

            data_assinaturas.append([
                str(item.ordem),
                aprovador.nome,
                data_assinatura,
                decisao,
                hash_display
            ])

        table_assinaturas = Table(data_assinaturas, colWidths=[1*cm, 5*cm, 3.5*cm, 3*cm, 7.5*cm])
        table_assinaturas.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Corpo
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Ordem centralizada
            ('ALIGN', (1, 1), (3, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Hash centralizado
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTNAME', (4, 1), (4, -1), 'Courier'),  # Hash em fonte monospace
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTSIZE', (4, 1), (4, -1), 7),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Linhas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))

        elements.append(table_assinaturas)
        elements.append(Spacer(1, 0.8*cm))

        # Seção de Pareceres Detalhados
        elements.append(Paragraph("PARECERES DETALHADOS", title_style))
        elements.append(Spacer(1, 0.3*cm))

        parecer_style = ParagraphStyle(
            'Parecer',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            spaceAfter=8
        )

        for item in sorted(bloco.itens, key=lambda x: x.ordem):
            aprovador = item.aprovador
            # Box do parecer
            parecer_data = [
                [Paragraph(f"<b>{item.ordem}. {aprovador.nome}</b> - {item.status}", parecer_style)],
                [Paragraph(f"<i>{item.parecer or 'Sem parecer'}</i>", parecer_style)]
            ]

            if item.ip_address:
                parecer_data.append([Paragraph(f"<font size=7>IP: {item.ip_address}</font>", parecer_style)])

            if item.assinatura_hash:
                parecer_data.append([Paragraph(f"<font size=6 face='Courier'>Hash completo: {item.assinatura_hash}</font>", parecer_style)])

            parecer_table = Table(parecer_data, colWidths=[18*cm])
            parecer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f4f8')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a5490')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            elements.append(parecer_table)
            elements.append(Spacer(1, 0.3*cm))

        elements.append(Spacer(1, 0.5*cm))

        # Informações de Verificação
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT,
            leftIndent=20
        )

        elements.append(Paragraph("<b>INFORMAÇÕES DE VERIFICAÇÃO</b>", subtitle_style))
        elements.append(Paragraph(
            f"• Este documento foi assinado digitalmente por {bloco.total_aprovadores()} aprovador(es)",
            info_style
        ))
        elements.append(Paragraph(
            f"• Modo de assinatura: <b>{bloco.modo.upper()}</b>",
            info_style
        ))
        elements.append(Paragraph(
            f"• Cada assinatura possui um hash SHA-256 único que garante autenticidade e integridade",
            info_style
        ))
        elements.append(Paragraph(
            f"• Os hashes são gerados com base em: documento_id + aprovador_id + timestamp + parecer",
            info_style
        ))
        elements.append(Spacer(1, 0.5*cm))

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

    # ========================================================================
    # RETOMADA DE FLUXO APÓS CORREÇÕES
    # ========================================================================

    @classmethod
    def autor_reenvia_apos_correcao(cls, tarefa_correcao):
        """
        Autor concluiu correção (após devolução do Triador/Validador)
        Retorna documento para triagem na UGQ

        Args:
            tarefa_correcao: Tarefa "Realizar Correção" que foi concluída

        Returns:
            Nova tarefa criada para Triador UGQ
        """
        log_debug("=" * 80)
        log_debug(f"RETOMADA DE FLUXO: Autor concluiu correção")
        log_debug(f"Tarefa #{tarefa_correcao.id}")
        log_debug("=" * 80)

        documento = tarefa_correcao.documento

        # Marca tarefa de correção como concluída
        tarefa_correcao.aprovado = True
        tarefa_correcao.concluida = True
        tarefa_correcao.data_conclusao = datetime.utcnow()
        tarefa_correcao.parecer = tarefa_correcao.parecer or 'Correção realizada'

        # Busca Triador UGQ disponível
        triador = Usuario.query.filter_by(
            perfil=Config.PERFIL_QUALIDADE_TRIADOR,
            ativo=True
        ).first()

        if not triador:
            log_debug("❌ ERRO: Nenhum Triador UGQ disponível")
            raise ValueError("Nenhum Triador UGQ disponível no sistema")

        log_debug(f"✅ Triador UGQ encontrado: {triador.nome} ({triador.email})")

        # Cria nova tarefa de triagem
        nova_tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=documento.criador_id,
            responsavel_id=triador.id,
            tipo_tarefa=Config.TAREFA_DOCUMENTO_RECEBIDO,
            descricao=f'Retriagem após correção: {documento.titulo}',
            prazo=datetime.utcnow() + timedelta(days=5),
            concluida=False
        )

        db.session.add(nova_tarefa)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_TRIAGEM

        db.session.flush()  # Gera nova_tarefa.id

        log_debug(f"✅ Nova tarefa #{nova_tarefa.id} criada para Triador UGQ")
        log_debug(f"📊 Documento status: {documento.status}")

        # Envia e-mail para o Triador UGQ
        if EMAIL_ENABLED:
            EmailService.enviar_notificacao_tarefa(
                usuario_id=triador.id,
                tipo_tarefa=Config.TAREFA_DOCUMENTO_RECEBIDO,
                documento_titulo=documento.titulo,
                documento_codigo=documento.codigo_provisorio or documento.codigo_unico
            )
            log_debug(f"📧 E-mail enviado para Triador UGQ: {triador.email}")

        log_debug("=" * 80)

        return nova_tarefa

    @classmethod
    def validador_reenvia_apos_ajustes(cls, tarefa_ajuste):
        """
        Validador concluiu ajustes (após reprovação de aprovador no bloco de assinatura)
        Retorna para o próprio Validador fazer nova codificação/validação

        Args:
            tarefa_ajuste: Tarefa "Realizar Ajustes" que foi concluída

        Returns:
            Nova tarefa criada para Validador UGQ
        """
        log_debug("=" * 80)
        log_debug(f"RETOMADA DE FLUXO: Validador concluiu ajustes")
        log_debug(f"Tarefa #{tarefa_ajuste.id}")
        log_debug("=" * 80)

        documento = tarefa_ajuste.documento

        # Marca tarefa de ajustes como concluída
        tarefa_ajuste.aprovado = True
        tarefa_ajuste.concluida = True
        tarefa_ajuste.data_conclusao = datetime.utcnow()
        tarefa_ajuste.parecer = tarefa_ajuste.parecer or 'Ajustes realizados'

        # Busca Validador UGQ disponível (preferencialmente o mesmo que fez os ajustes)
        validador = Usuario.query.get(tarefa_ajuste.responsavel_id)

        if not validador or not validador.is_validador_ugq():
            # Busca qualquer Validador UGQ ativo
            validador = Usuario.query.filter_by(
                perfil=Config.PERFIL_QUALIDADE_VALIDADOR,
                ativo=True
            ).first()

        if not validador:
            log_debug("❌ ERRO: Nenhum Validador UGQ disponível")
            raise ValueError("Nenhum Validador UGQ disponível no sistema")

        log_debug(f"✅ Validador UGQ encontrado: {validador.nome} ({validador.email})")

        # Cria nova tarefa de validação e codificação
        nova_tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=tarefa_ajuste.responsavel_id,
            responsavel_id=validador.id,
            tipo_tarefa=Config.TAREFA_VALIDAR_CODIFICAR,
            descricao=f'Revalidar após ajustes: {documento.titulo}',
            prazo=datetime.utcnow() + timedelta(days=7),
            concluida=False
        )

        db.session.add(nova_tarefa)

        # Atualiza status do documento
        documento.status = Config.STATUS_EM_VALIDACAO

        db.session.flush()  # Gera nova_tarefa.id

        log_debug(f"✅ Nova tarefa #{nova_tarefa.id} criada para Validador UGQ")
        log_debug(f"📊 Documento status: {documento.status}")

        # Envia e-mail para o Validador UGQ
        if EMAIL_ENABLED:
            EmailService.enviar_notificacao_tarefa(
                usuario_id=validador.id,
                tipo_tarefa=Config.TAREFA_VALIDAR_CODIFICAR,
                documento_titulo=documento.titulo,
                documento_codigo=documento.codigo_provisorio or documento.codigo_unico
            )
            log_debug(f"📧 E-mail enviado para Validador UGQ: {validador.email}")

        log_debug("=" * 80)

        return nova_tarefa
