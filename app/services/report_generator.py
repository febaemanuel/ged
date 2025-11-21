"""
Gerador de Relatórios PDF usando ReportLab

Funções:
- gerar_relatorio_tarefas_atrasadas
- gerar_relatorio_documentos_vencendo
- gerar_relatorio_geral
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io


def _criar_cabecalho(titulo, data_geracao):
    """Cria cabeçalho padrão do relatório"""
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'TituloRelatorio',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        alignment=TA_CENTER
    )

    data_style = ParagraphStyle(
        'DataGeracao',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )

    elements = []
    elements.append(Paragraph(titulo, titulo_style))
    elements.append(Paragraph(f"Data de Geração: {data_geracao}", data_style))
    elements.append(Spacer(1, 0.5 * cm))

    return elements


def gerar_relatorio_tarefas_atrasadas(tarefas, usuario_nome):
    """
    Gera relatório PDF de tarefas atrasadas

    Args:
        tarefas: Lista de dicionários com informações das tarefas
        usuario_nome: Nome do usuário que gerou o relatório

    Returns:
        BytesIO com o PDF gerado
    """
    buffer = io.BytesIO()

    # Cria documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho
    data_geracao = datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')
    elements.extend(_criar_cabecalho('Relatório de Tarefas Atrasadas', data_geracao))

    # Informações gerais
    info_text = f"""
    <b>Total de tarefas atrasadas:</b> {len(tarefas)}<br/>
    <b>Gerado por:</b> {usuario_nome}
    """
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 0.5 * cm))

    if not tarefas:
        elements.append(Paragraph("Não há tarefas atrasadas no momento.", styles['Normal']))
    else:
        # Tabela de tarefas
        data = [['ID', 'Tipo', 'Documento', 'Responsável', 'Prazo', 'Dias\nAtraso', 'Prioridade']]

        for t in tarefas:
            prazo = datetime.fromisoformat(t['prazo']).strftime('%d/%m/%Y') if t.get('prazo') else 'N/A'
            data.append([
                str(t['id']),
                t['tipo_tarefa'],
                t['documento_titulo'][:30] + '...' if len(t['documento_titulo']) > 30 else t['documento_titulo'],
                t['responsavel'][:20] + '...' if len(t['responsavel']) > 20 else t['responsavel'],
                prazo,
                str(t['dias_atraso']),
                t['prioridade']
            ])

        # Cria tabela
        table = Table(data, colWidths=[1.5*cm, 3*cm, 5*cm, 4*cm, 2.5*cm, 2*cm, 2*cm])

        # Estilo da tabela
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Corpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centralizado
            ('ALIGN', (4, 1), (5, -1), 'CENTER'),  # Prazo e dias centralizado
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Alterna cores
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))

        elements.append(table)

    # Rodapé
    elements.append(Spacer(1, 1 * cm))
    rodape = Paragraph(
        f"Sistema GED - Gerenciador Eletrônico de Documentos",
        ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(rodape)

    # Gera PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer


def gerar_relatorio_documentos_vencendo(documentos, dias_limite, usuario_nome):
    """
    Gera relatório PDF de documentos próximos ao vencimento

    Args:
        documentos: Lista de dicionários com informações dos documentos
        dias_limite: Dias até o vencimento considerados
        usuario_nome: Nome do usuário que gerou o relatório

    Returns:
        BytesIO com o PDF gerado
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho
    data_geracao = datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')
    titulo = f'Relatório de Documentos Vencendo em {dias_limite} Dias'
    elements.extend(_criar_cabecalho(titulo, data_geracao))

    # Informações gerais
    info_text = f"""
    <b>Total de documentos próximos ao vencimento:</b> {len(documentos)}<br/>
    <b>Período considerado:</b> Próximos {dias_limite} dias<br/>
    <b>Gerado por:</b> {usuario_nome}
    """
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 0.5 * cm))

    if not documentos:
        elements.append(Paragraph(f"Não há documentos vencendo nos próximos {dias_limite} dias.", styles['Normal']))
    else:
        # Tabela de documentos
        data = [['Código', 'Título', 'Tipo', 'Setor', 'Publicação', 'Vencimento', 'Dias\nRestantes']]

        for d in documentos:
            pub = datetime.fromisoformat(d['data_publicacao']).strftime('%d/%m/%Y') if d['data_publicacao'] else 'N/A'
            venc = datetime.fromisoformat(d['data_vencimento']).strftime('%d/%m/%Y') if d['data_vencimento'] else 'N/A'

            data.append([
                d['codigo_definitivo'] or 'N/A',
                d['titulo'][:25] + '...' if len(d['titulo']) > 25 else d['titulo'],
                d['tipo_documento'],
                d['setor'][:15] + '...' if d.get('setor') and len(d['setor']) > 15 else (d.get('setor') or 'N/A'),
                pub,
                venc,
                str(d['dias_ate_vencimento']) if d['dias_ate_vencimento'] else 'N/A'
            ])

        table = Table(data, colWidths=[3*cm, 4.5*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (4, 1), (6, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),

            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))

        elements.append(table)

        # Alerta
        elements.append(Spacer(1, 0.5 * cm))
        alerta = Paragraph(
            "<b>Atenção:</b> Estes documentos estão próximos do vencimento e podem necessitar de revisão ou atualização.",
            ParagraphStyle('Alerta', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#d9534f'))
        )
        elements.append(alerta)

    # Rodapé
    elements.append(Spacer(1, 1 * cm))
    rodape = Paragraph(
        "Sistema GED - Gerenciador Eletrônico de Documentos",
        ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(rodape)

    doc.build(elements)

    buffer.seek(0)
    return buffer


def gerar_relatorio_geral(dados, usuario_nome):
    """
    Gera relatório geral do sistema

    Args:
        dados: Dicionário com estatísticas gerais do sistema
        usuario_nome: Nome do usuário que gerou o relatório

    Returns:
        BytesIO com o PDF gerado
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Cabeçalho
    data_geracao = datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')
    elements.extend(_criar_cabecalho('Relatório Geral do Sistema GED', data_geracao))

    # Informações
    info_text = f"<b>Gerado por:</b> {usuario_nome}"
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 0.5 * cm))

    # Seção Usuários
    elements.append(Paragraph('<b>Usuários</b>', styles['Heading2']))
    usuarios_data = [
        ['Total de Usuários', str(dados['usuarios']['total'])],
        ['Usuários Ativos', str(dados['usuarios']['ativos'])],
        ['Usuários Inativos', str(dados['usuarios']['inativos'])]
    ]
    usuarios_table = Table(usuarios_data, colWidths=[8*cm, 4*cm])
    usuarios_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(usuarios_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Seção Documentos
    elements.append(Paragraph('<b>Documentos</b>', styles['Heading2']))
    docs_data = [
        ['Total de Documentos', str(dados['documentos']['total'])],
        ['Documentos Vencidos', str(dados['documentos']['vencidos'])],
        ['Vencendo em 30 dias', str(dados['documentos']['vencendo_30_dias'])]
    ]
    docs_table = Table(docs_data, colWidths=[8*cm, 4*cm])
    docs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(docs_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Documentos por status
    elements.append(Paragraph('<i>Documentos por Status:</i>', styles['Normal']))
    status_data = [['Status', 'Quantidade']]
    for status, qtd in dados['documentos']['por_status'].items():
        status_data.append([status, str(qtd)])

    status_table = Table(status_data, colWidths=[8*cm, 4*cm])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Seção Tarefas
    elements.append(Paragraph('<b>Tarefas</b>', styles['Heading2']))
    tarefas_data = [
        ['Total de Tarefas', str(dados['tarefas']['total'])],
        ['Tarefas Pendentes', str(dados['tarefas']['pendentes'])],
        ['Tarefas Atrasadas', str(dados['tarefas']['atrasadas'])]
    ]
    tarefas_table = Table(tarefas_data, colWidths=[8*cm, 4*cm])
    tarefas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(tarefas_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Documentos Recentes
    if dados.get('documentos_recentes'):
        elements.append(PageBreak())
        elements.append(Paragraph('<b>Documentos Recentes</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.3 * cm))

        recentes_data = [['ID', 'Título', 'Tipo', 'Status', 'Criador', 'Data']]
        for documento in dados['documentos_recentes']:
            data_criacao = datetime.fromisoformat(documento['data_criacao']).strftime('%d/%m/%Y') if documento.get('data_criacao') else 'N/A'
            recentes_data.append([
                str(documento['id']),
                documento['titulo'][:30] + '...' if len(documento['titulo']) > 30 else documento['titulo'],
                documento['tipo'] or 'N/A',
                documento['status'],
                documento['criador'][:15] + '...' if len(documento['criador']) > 15 else documento['criador'],
                data_criacao
            ])

        recentes_table = Table(recentes_data, colWidths=[1.5*cm, 5*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm])
        recentes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        elements.append(recentes_table)

    # Rodapé
    elements.append(Spacer(1, 1 * cm))
    rodape = Paragraph(
        "Sistema GED - Gerenciador Eletrônico de Documentos",
        ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(rodape)

    doc.build(elements)

    buffer.seek(0)
    return buffer
