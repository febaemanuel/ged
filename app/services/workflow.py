"""
Serviço de Workflow Automático - Sistema GED
Gerencia o fluxo de aprovação de documentos seguindo o padrão EBSERH

FLUXO OBRIGATÓRIO:
1. Autor (Cria) → Status: "Novo"
2. Chefia Imediata (Analisa) → Tarefa: "Analisar"
3. Especialista/Área Técnica (Valida Conteúdo) → Tarefa: "Validar Conteúdo"
4. Qualidade (Valida Padronização) → Tarefa: "Validar Padronização"
5. Aprovador/Superintendência (Aprova) → Tarefa: "Aprovar"
6. Gestão Documental (Publica) → Tarefa: "Publicar"
"""

from datetime import datetime, timedelta
from app.models import db, Tarefa, Documento, Usuario
import logging

logger = logging.getLogger(__name__)


class WorkflowGED:
    """Gerenciador de Workflow de Aprovação de Documentos"""

    # Definição do fluxo
    FLUXO_APROVACAO = [
        {
            'etapa': 1,
            'tipo_tarefa': 'Analisar',
            'descricao': 'Análise de pertinência pela Chefia Imediata',
            'perfil_responsavel': 'gerente',  # Chefia
            'prazo_dias': 5,
            'proximo_status': 'Em Análise'
        },
        {
            'etapa': 2,
            'tipo_tarefa': 'Validar Conteúdo',
            'descricao': 'Validação de conteúdo técnico pela Área Especialista',
            'perfil_responsavel': 'responsavel_interno',  # Especialista
            'prazo_dias': 7,
            'proximo_status': 'Em Validação'
        },
        {
            'etapa': 3,
            'tipo_tarefa': 'Validar Padronização',
            'descricao': 'Validação de padronização pela Qualidade',
            'perfil_responsavel': 'responsavel_interno',  # Qualidade
            'prazo_dias': 5,
            'proximo_status': 'Em Validação'
        },
        {
            'etapa': 4,
            'tipo_tarefa': 'Aprovar',
            'descricao': 'Aprovação final pela Superintendência',
            'perfil_responsavel': 'gerente',  # Aprovador
            'prazo_dias': 3,
            'proximo_status': 'Aguardando Aprovação'
        },
        {
            'etapa': 5,
            'tipo_tarefa': 'Publicar',
            'descricao': 'Publicação e geração de PDF final',
            'perfil_responsavel': 'administrador',  # Gestão Documental
            'prazo_dias': 2,
            'proximo_status': 'Aprovado'
        }
    ]

    @classmethod
    def iniciar_fluxo(cls, documento, chefia_id):
        """
        Inicia o fluxo de aprovação quando o documento é criado

        Args:
            documento: Objeto Documento
            chefia_id: ID da Chefia Imediata selecionada pelo autor

        Returns:
            Tarefa criada
        """
        logger.info(f"Iniciando fluxo de aprovação para documento {documento.id}")

        # Primeira etapa: Chefia Imediata
        primeira_etapa = cls.FLUXO_APROVACAO[0]

        # Busca a chefia
        chefia = Usuario.query.get(chefia_id)
        if not chefia:
            raise ValueError(f"Chefia com ID {chefia_id} não encontrada")

        # Cria tarefa para Chefia Imediata
        tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=documento.criador_id,
            responsavel_id=chefia_id,
            tipo_tarefa=primeira_etapa['tipo_tarefa'],
            descricao=primeira_etapa['descricao'],
            prioridade='normal',
            prazo=datetime.utcnow() + timedelta(days=primeira_etapa['prazo_dias'])
        )

        # Atualiza status do documento
        documento.status = primeira_etapa['proximo_status']

        db.session.add(tarefa)
        db.session.commit()

        logger.info(f"Tarefa '{primeira_etapa['tipo_tarefa']}' criada para {chefia.nome}")

        return tarefa

    @classmethod
    def proximo_passo(cls, tarefa_concluida):
        """
        Cria a próxima tarefa do fluxo quando uma tarefa é concluída e aprovada

        Args:
            tarefa_concluida: Tarefa que foi concluída

        Returns:
            Nova tarefa criada ou None se for a última etapa
        """
        if not tarefa_concluida.aprovado:
            logger.warning(f"Tarefa {tarefa_concluida.id} foi reprovada. Não criando próxima etapa.")
            # Se reprovado, volta para o autor corrigir
            cls._criar_tarefa_correcao(tarefa_concluida)
            return None

        # Encontra etapa atual
        etapa_atual = None
        indice_atual = None

        for i, etapa in enumerate(cls.FLUXO_APROVACAO):
            if etapa['tipo_tarefa'] == tarefa_concluida.tipo_tarefa:
                etapa_atual = etapa
                indice_atual = i
                break

        if etapa_atual is None:
            logger.error(f"Tipo de tarefa '{tarefa_concluida.tipo_tarefa}' não encontrado no fluxo")
            return None

        # Verifica se é a última etapa
        if indice_atual >= len(cls.FLUXO_APROVACAO) - 1:
            logger.info(f"Última etapa concluída. Documento {tarefa_concluida.documento_id} publicado!")
            return None

        # Próxima etapa
        proxima_etapa = cls.FLUXO_APROVACAO[indice_atual + 1]
        documento = tarefa_concluida.documento

        # Busca responsável para próxima etapa
        responsavel = cls._buscar_responsavel(proxima_etapa, documento)

        if not responsavel:
            logger.error(f"Nenhum responsável encontrado para etapa '{proxima_etapa['tipo_tarefa']}'")
            return None

        # Cria próxima tarefa
        nova_tarefa = Tarefa(
            documento_id=documento.id,
            criador_id=tarefa_concluida.responsavel_id,  # Quem concluiu a tarefa anterior
            responsavel_id=responsavel.id,
            tipo_tarefa=proxima_etapa['tipo_tarefa'],
            descricao=proxima_etapa['descricao'],
            prioridade='normal',
            prazo=datetime.utcnow() + timedelta(days=proxima_etapa['prazo_dias'])
        )

        # Atualiza status do documento
        documento.status = proxima_etapa['proximo_status']

        db.session.add(nova_tarefa)
        db.session.commit()

        logger.info(f"Próxima tarefa '{proxima_etapa['tipo_tarefa']}' criada para {responsavel.nome}")

        return nova_tarefa

    @classmethod
    def _buscar_responsavel(cls, etapa, documento):
        """
        Busca responsável adequado para a etapa

        Args:
            etapa: Dicionário da etapa
            documento: Objeto Documento

        Returns:
            Usuario responsável
        """
        perfil = etapa['perfil_responsavel']
        tipo_tarefa = etapa['tipo_tarefa']

        # Lógica específica por tipo de tarefa
        if tipo_tarefa == 'Validar Conteúdo':
            # Busca responsável interno do mesmo setor
            responsavel = Usuario.query.filter_by(
                perfil='responsavel_interno',
                setor=documento.setor,
                ativo=True
            ).first()

            # Se não encontrar do setor, pega qualquer responsável interno
            if not responsavel:
                responsavel = Usuario.query.filter_by(
                    perfil='responsavel_interno',
                    ativo=True
                ).first()

        elif tipo_tarefa == 'Validar Padronização':
            # Busca responsável da área de Qualidade
            responsavel = Usuario.query.filter_by(
                perfil='responsavel_interno',
                setor='Qualidade',
                ativo=True
            ).first()

            # Se não encontrar, pega qualquer responsável interno
            if not responsavel:
                responsavel = Usuario.query.filter_by(
                    perfil='responsavel_interno',
                    ativo=True
                ).first()

        elif tipo_tarefa == 'Aprovar':
            # Busca gerente do setor ou superior
            responsavel = Usuario.query.filter_by(
                perfil='gerente',
                setor=documento.setor,
                ativo=True
            ).first()

            # Se não encontrar, pega qualquer gerente
            if not responsavel:
                responsavel = Usuario.query.filter_by(
                    perfil='gerente',
                    ativo=True
                ).first()

        elif tipo_tarefa == 'Publicar':
            # Busca administrador
            responsavel = Usuario.query.filter_by(
                perfil='administrador',
                ativo=True
            ).first()

        else:
            # Padrão: busca qualquer usuário do perfil especificado
            responsavel = Usuario.query.filter_by(
                perfil=perfil,
                ativo=True
            ).first()

        return responsavel

    @classmethod
    def _criar_tarefa_correcao(cls, tarefa_reprovada):
        """
        Cria tarefa de correção para o autor quando algo é reprovado

        Args:
            tarefa_reprovada: Tarefa que foi reprovada
        """
        documento = tarefa_reprovada.documento

        tarefa_correcao = Tarefa(
            documento_id=documento.id,
            criador_id=tarefa_reprovada.responsavel_id,
            responsavel_id=documento.criador_id,  # Volta para o autor
            tipo_tarefa='Realizar Correção',
            descricao=f'Correção solicitada na etapa "{tarefa_reprovada.tipo_tarefa}": {tarefa_reprovada.parecer}',
            prioridade='alta',
            prazo=datetime.utcnow() + timedelta(days=3)
        )

        # Status volta para inicial
        documento.status = 'Novo'

        db.session.add(tarefa_correcao)
        db.session.commit()

        logger.info(f"Tarefa de correção criada para autor {documento.criador.nome}")

        return tarefa_correcao

    @classmethod
    def obter_proxima_etapa(cls, tipo_tarefa_atual):
        """
        Retorna informações da próxima etapa do fluxo

        Args:
            tipo_tarefa_atual: Tipo da tarefa atual

        Returns:
            Dicionário da próxima etapa ou None
        """
        for i, etapa in enumerate(cls.FLUXO_APROVACAO):
            if etapa['tipo_tarefa'] == tipo_tarefa_atual:
                if i < len(cls.FLUXO_APROVACAO) - 1:
                    return cls.FLUXO_APROVACAO[i + 1]
                break

        return None

    @classmethod
    def obter_etapa_atual(cls, tipo_tarefa):
        """
        Retorna informações da etapa baseado no tipo de tarefa

        Args:
            tipo_tarefa: Tipo da tarefa

        Returns:
            Dicionário da etapa
        """
        for etapa in cls.FLUXO_APROVACAO:
            if etapa['tipo_tarefa'] == tipo_tarefa:
                return etapa

        return None
