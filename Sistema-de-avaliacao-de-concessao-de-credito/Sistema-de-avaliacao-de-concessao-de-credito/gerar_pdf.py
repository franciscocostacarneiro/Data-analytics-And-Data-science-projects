"""
Gerador do documento de apresentação do projeto em PDF.
ABNT-inspired com diagramação de negócios.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Paleta de cores ─────────────────────────────────────────────────────────
ROXO_PRIMARIO   = colors.HexColor("#6E42AD")
ROXO_ESCURO     = colors.HexColor("#4A2878")
ROXO_CLARO      = colors.HexColor("#916DED")
CINZA_ESCURO    = colors.HexColor("#303233")
CINZA_MEDIO     = colors.HexColor("#595959")
CINZA_CLARO     = colors.HexColor("#F5F5F5")
BRANCO          = colors.white
PRETO           = colors.HexColor("#1A1A1A")
VERDE_ACENTO    = colors.HexColor("#27AE60")
AZUL_ACENTO     = colors.HexColor("#2980B9")
CODE_BG         = colors.HexColor("#F0EAF8")   # fundo lavanda para blocos de código

# ── Dimensões ABNT ──────────────────────────────────────────────────────────
MARGEM_ESQ      = 3.0 * cm
MARGEM_DIR      = 2.0 * cm
MARGEM_SUP      = 3.0 * cm
MARGEM_INF      = 2.0 * cm
LARGURA_UTIL    = A4[0] - MARGEM_ESQ - MARGEM_DIR

OUTPUT = "Apresentacao_Projeto_Credit_Scoring.pdf"


# ── Estilos ─────────────────────────────────────────────────────────────────
def build_styles():
    s = getSampleStyleSheet()

    body = ParagraphStyle("body_abnt",
        fontName="Helvetica", fontSize=12, leading=22,
        alignment=TA_JUSTIFY, textColor=PRETO,
        spaceBefore=6, spaceAfter=6,
    )
    body_small = ParagraphStyle("body_small",
        fontName="Helvetica", fontSize=11, leading=18,
        alignment=TA_JUSTIFY, textColor=CINZA_MEDIO,
        spaceBefore=4, spaceAfter=4,
    )
    h1 = ParagraphStyle("h1",
        fontName="Helvetica-Bold", fontSize=22, leading=28,
        textColor=BRANCO, alignment=TA_LEFT,
        spaceBefore=0, spaceAfter=0,
    )
    h2 = ParagraphStyle("h2",
        fontName="Helvetica-Bold", fontSize=15, leading=20,
        textColor=ROXO_ESCURO, alignment=TA_LEFT,
        spaceBefore=18, spaceAfter=6,
    )
    h3 = ParagraphStyle("h3",
        fontName="Helvetica-Bold", fontSize=12, leading=16,
        textColor=ROXO_PRIMARIO, alignment=TA_LEFT,
        spaceBefore=12, spaceAfter=4,
    )
    caption = ParagraphStyle("caption",
        fontName="Helvetica-Oblique", fontSize=9, leading=12,
        textColor=CINZA_MEDIO, alignment=TA_CENTER,
    )
    toc_item = ParagraphStyle("toc",
        fontName="Helvetica", fontSize=12, leading=22,
        textColor=CINZA_ESCURO, alignment=TA_LEFT,
    )
    badge = ParagraphStyle("badge",
        fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=BRANCO, alignment=TA_CENTER,
    )
    cover_sub = ParagraphStyle("cover_sub",
        fontName="Helvetica", fontSize=13, leading=18,
        textColor=colors.HexColor("#D4B8FF"), alignment=TA_LEFT,
    )
    cover_meta = ParagraphStyle("cover_meta",
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=colors.HexColor("#C0C0C0"), alignment=TA_LEFT,
    )
    return dict(
        body=body, body_small=body_small,
        h1=h1, h2=h2, h3=h3,
        caption=caption, toc_item=toc_item,
        badge=badge, cover_sub=cover_sub, cover_meta=cover_meta,
    )


# ── Cabeçalho / rodapé ──────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4

    if doc.page == 1:
        # capa — sem header/footer padrão
        canvas.restoreState()
        return

    # Faixa roxa topo
    canvas.setFillColor(ROXO_PRIMARIO)
    canvas.rect(0, h - 1.0 * cm, w, 1.0 * cm, fill=1, stroke=0)

    # Título no header
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(BRANCO)
    canvas.drawString(MARGEM_ESQ, h - 0.65 * cm, "Sistema de Avaliação de Concessão de Crédito")
    canvas.drawRightString(w - MARGEM_DIR, h - 0.65 * cm, "Credit Scoring · Data Science")

    # Linha separadora rodapé
    canvas.setStrokeColor(ROXO_CLARO)
    canvas.setLineWidth(0.5)
    canvas.line(MARGEM_ESQ, MARGEM_INF - 0.2 * cm, w - MARGEM_DIR, MARGEM_INF - 0.2 * cm)

    # Número de página
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(CINZA_MEDIO)
    canvas.drawCentredString(w / 2, MARGEM_INF - 0.6 * cm, f"— {doc.page} —")

    canvas.restoreState()


# ── Helpers de layout ───────────────────────────────────────────────────────
def section_divider():
    return HRFlowable(width="100%", thickness=1.5,
                      color=ROXO_CLARO, spaceAfter=6, spaceBefore=4)


def colored_box(content_rows, bg=CINZA_CLARO, col_widths=None):
    """Cria uma tabela de 1 coluna com fundo colorido."""
    col_widths = col_widths or [LARGURA_UTIL]
    t = Table(content_rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return t


def metric_card(label, value, sub, bg=ROXO_PRIMARIO):
    st = build_styles()
    lbl = Paragraph(f"<font color='#D4B8FF' size='9'>{label}</font>", st["badge"])
    val = Paragraph(f"<font color='white' size='20'><b>{value}</b></font>", st["badge"])
    sub_p = Paragraph(f"<font color='#E0E0E0' size='8'>{sub}</font>", st["badge"])
    inner = Table([[lbl], [val], [sub_p]], colWidths=[LARGURA_UTIL / 4 - 10])
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return inner


def kv_table(rows, header=None):
    """Tabela chave-valor estilizada."""
    st = build_styles()
    data = []
    if header:
        data.append([Paragraph(f"<b>{header[0]}</b>", st["body_small"]),
                     Paragraph(f"<b>{header[1]}</b>", st["body_small"])])
    for k, v in rows:
        data.append([
            Paragraph(f"<b>{k}</b>", st["body_small"]),
            Paragraph(v, st["body_small"]),
        ])
    cw = [LARGURA_UTIL * 0.35, LARGURA_UTIL * 0.65]
    t = Table(data, colWidths=cw, repeatRows=1 if header else 0)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), ROXO_PRIMARIO if header else CINZA_CLARO),
        ("TEXTCOLOR",  (0, 0), (-1, 0), BRANCO if header else PRETO),
        ("BACKGROUND", (0, 1), (-1, -1), BRANCO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]
    t.setStyle(TableStyle(style))
    return t


def _escape_code(texto):
    """Escapa caracteres XML e preserva indentação com espaços não-quebráveis."""
    texto = texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    linhas = texto.split('\n')
    escapadas = []
    for linha in linhas:
        stripped = linha.lstrip(' ')
        n = len(linha) - len(stripped)
        escapadas.append('&#160;' * n + stripped)
    return '<br/>'.join(escapadas)


def code_block(arquivo, descricao, codigo):
    """Renderiza um bloco de código: header roxo escuro + corpo em lavanda."""
    header_st = ParagraphStyle("_code_hdr",
        fontName="Courier-Bold", fontSize=9, leading=12,
        textColor=BRANCO, alignment=TA_LEFT,
    )
    desc_st = ParagraphStyle("_code_desc",
        fontName="Helvetica-Oblique", fontSize=8, leading=12,
        textColor=colors.HexColor("#D4B8FF"), alignment=TA_RIGHT,
    )
    code_st = ParagraphStyle("_code_body",
        fontName="Courier", fontSize=7.5, leading=11,
        textColor=CINZA_ESCURO, alignment=TA_LEFT,
    )
    header = Table([[
        Paragraph(arquivo, header_st),
        Paragraph(descricao, desc_st),
    ]], colWidths=[LARGURA_UTIL * 0.45, LARGURA_UTIL * 0.55])
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ROXO_ESCURO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    body = Table([[
        Paragraph(_escape_code(codigo), code_st),
    ]], colWidths=[LARGURA_UTIL])
    body.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CODE_BG),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX",           (0, 0), (-1, -1), 0.5, ROXO_CLARO),
    ]))
    return KeepTogether([header, body, Spacer(1, 0.3 * cm)])


# ── CAPA ─────────────────────────────────────────────────────────────────────
def build_cover(story, st):
    w, h = A4
    # Bloco de fundo escuro — simulado com tabela de largura total
    cover_data = [[
        Paragraph("SISTEMA DE AVALIAÇÃO DE<br/>"
                  "<font color='#A467F5'>CONCESSÃO DE CRÉDITO</font>", st["h1"])
    ]]
    cover_t = Table(cover_data, colWidths=[LARGURA_UTIL])
    cover_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CINZA_ESCURO),
        ("LEFTPADDING",  (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
        ("TOPPADDING",   (0, 0), (-1, -1), 40),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 40),
    ]))

    story.append(Spacer(1, 1.5 * cm))
    story.append(cover_t)
    story.append(Spacer(1, 0.6 * cm))

    # Faixa roxa decorativa
    accent = Table([[""]], colWidths=[LARGURA_UTIL], rowHeights=[0.35 * cm])
    accent.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ROXO_PRIMARIO)]))
    story.append(accent)
    story.append(Spacer(1, 0.8 * cm))

    # Subtítulo
    story.append(Paragraph("Documentação Técnica de Projeto", st["cover_sub"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Credit Scoring com Machine Learning · Aplicação Web Interativa · "
        "Política de Concessão Baseada em Dados",
        st["cover_meta"]
    ))

    story.append(Spacer(1, 1.5 * cm))

    # Cards de destaque da capa
    cards_row = [
        metric_card("Precisão do Modelo", "69%", "AUC · ROC Score", ROXO_PRIMARIO),
        metric_card("Maus Capturados", "83%", "Recall @ thresh. 0.10", ROXO_ESCURO),
        metric_card("Registros Treino", "22.742", "Clientes analisados", colors.HexColor("#5B3494")),
        metric_card("Componentes", "3", "Camadas de decisão", colors.HexColor("#3D1F6E")),
    ]
    cards_t = Table([cards_row],
                    colWidths=[LARGURA_UTIL / 4 - 4] * 4,
                    hAlign="LEFT")
    cards_t.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(cards_t)
    story.append(Spacer(1, 2.0 * cm))

    # Metadados
    meta = Table([
        [Paragraph("<b>Autor:</b>", st["body_small"]),
         Paragraph("Francisco Costa Carneiro", st["body_small"])],
        [Paragraph("<b>Área:</b>", st["body_small"]),
         Paragraph("Ciência de Dados · Finanças · Machine Learning", st["body_small"])],
        [Paragraph("<b>Tecnologias:</b>", st["body_small"]),
         Paragraph("Python · Streamlit · Scikit-learn · XGBoost · Pandas · Joblib", st["body_small"])],
        [Paragraph("<b>Data:</b>", st["body_small"]),
         Paragraph("Maio de 2026", st["body_small"])],
    ], colWidths=[LARGURA_UTIL * 0.22, LARGURA_UTIL * 0.78])
    meta.setStyle(TableStyle([
        ("LINEABOVE",   (0, 0), (-1, 0), 1, ROXO_PRIMARIO),
        ("LINEBELOW",   (0, -1), (-1, -1), 1, ROXO_PRIMARIO),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
    ]))
    story.append(meta)
    story.append(PageBreak())


# ── SUMÁRIO ──────────────────────────────────────────────────────────────────
def build_toc(story, st):
    story.append(Paragraph("SUMÁRIO", st["h2"]))
    story.append(section_divider())
    story.append(Spacer(1, 0.4 * cm))

    items = [
        ("1", "Introdução e Contexto de Negócio", "3"),
        ("2", "Objetivos do Projeto",              "3"),
        ("3", "Arquitetura Tecnológica",            "4"),
        ("4", "Fonte de Dados e Preparação",        "4"),
        ("5", "Engenharia de Features",             "5"),
        ("6", "Modelagem e Machine Learning",       "5"),
        ("7", "Política de Concessão de Crédito",   "6"),
        ("8", "Interface e Funcionalidades",        "7"),
        ("9", "Resultados e Métricas",              "8"),
        ("10","Conclusões e Próximos Passos",       "8"),
        ("11","Anexo Técnico — Código-Fonte",        "9"),
    ]
    for num, title, page in items:
        dots = "." * (60 - len(title) - len(num))
        row = Table([
            [Paragraph(f"{num}.", st["toc_item"]),
             Paragraph(title, st["toc_item"]),
             Paragraph(page, st["toc_item"])]
        ], colWidths=[1.0 * cm, LARGURA_UTIL - 2.2 * cm, 1.2 * cm])
        row.setStyle(TableStyle([
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.3, colors.HexColor("#E0D0FF")),
        ]))
        story.append(row)

    story.append(PageBreak())


# ── SEÇÕES DE CONTEÚDO ───────────────────────────────────────────────────────
def build_content(story, st):

    # ── 1. Introdução ─────────────────────────────────────────────────────
    story.append(Paragraph("1. Introdução e Contexto de Negócio", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "O crédito é o principal instrumento de alavancagem financeira de pessoas físicas e "
        "jurídicas. Para instituições financeiras, a decisão de conceder crédito envolve um "
        "equilíbrio crítico entre a expansão da carteira e o controle do risco de inadimplência. "
        "Uma concessão inadequada pode comprometer a saúde financeira do negócio; uma rejeição "
        "indevida, por sua vez, perde receita e prejudica a experiência do cliente.", st["body"]))
    story.append(Paragraph(
        "Este projeto propõe um <b>Sistema de Avaliação de Concessão de Crédito</b> que combina "
        "duas abordagens complementares: <b>Regras de Política de Negócio</b> (decisões hard "
        "baseadas em critérios mínimos absolutos) e um <b>Modelo de Machine Learning</b> "
        "(GradientBoostingClassifier) que calcula a probabilidade de inadimplência de cada "
        "solicitante. O sistema é entregue em uma <b>aplicação web interativa</b> desenvolvida "
        "com Streamlit, tornando o processo acessível a analistas de crédito sem necessidade "
        "de conhecimento técnico em programação.", st["body"]))

    # ── 2. Objetivos ─────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("2. Objetivos do Projeto", st["h2"]))
    story.append(section_divider())

    objs = [
        ["Objetivo Primário",
         "Automatizar a avaliação de risco de crédito, reduzindo decisões subjetivas e acelerando "
         "o processo de concessão de cartões de crédito."],
        ["Objetivo Secundário",
         "Implementar uma política de crédito baseada em dados reais, com regras transparentes e "
         "auditáveis que protejam o negócio contra perfis de alto risco."],
        ["Objetivo Técnico",
         "Construir um pipeline de Machine Learning reproduzível, com feature engineering, "
         "tratamento de desbalanceamento de classes e calibração de threshold de decisão."],
        ["Objetivo de UX",
         "Entregar uma interface web intuitiva que permita a qualquer analista realizar avaliações "
         "em tempo real, com feedback claro sobre aprovação, rejeição e motivos da decisão."],
    ]
    for ob in objs:
        row_t = Table([[
            Paragraph(ob[0], ParagraphStyle("ob_label",
                fontName="Helvetica-Bold", fontSize=10,
                textColor=ROXO_ESCURO, alignment=TA_LEFT)),
            Paragraph(ob[1], st["body_small"]),
        ]], colWidths=[LARGURA_UTIL * 0.30, LARGURA_UTIL * 0.70])
        row_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EDE0FF")),
            ("BACKGROUND", (1, 0), (1, 0), BRANCO),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(row_t)
        story.append(Spacer(1, 3))

    story.append(PageBreak())

    # ── 3. Arquitetura ────────────────────────────────────────────────────
    story.append(Paragraph("3. Arquitetura Tecnológica", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "O projeto é estruturado em três camadas principais, seguindo boas práticas de "
        "arquitetura de sistemas de Machine Learning em produção:", st["body"]))
    story.append(Spacer(1, 0.3 * cm))

    arch_data = [
        [Paragraph("<b>Camada</b>", st["badge"]),
         Paragraph("<b>Componente</b>", st["badge"]),
         Paragraph("<b>Responsabilidade</b>", st["badge"]),
         Paragraph("<b>Tecnologia</b>", st["badge"])],
        [Paragraph("Apresentação", st["body_small"]),
         Paragraph("Interface Web", st["body_small"]),
         Paragraph("Formulário interativo, feedback visual ao usuário", st["body_small"]),
         Paragraph("Streamlit 1.57", st["body_small"])],
        [Paragraph("Negócio", st["body_small"]),
         Paragraph("Policy Rules Engine", st["body_small"]),
         Paragraph("Regras de crédito hard: renda mínima, per capita, perfil estudante, risco jovem", st["body_small"]),
         Paragraph("Python puro", st["body_small"])],
        [Paragraph("ML / Analytics", st["body_small"]),
         Paragraph("Pipeline Scikit-learn", st["body_small"]),
         Paragraph("Transformações, encoding, normalização, predição probabilística", st["body_small"]),
         Paragraph("Scikit-learn 1.8 · Joblib", st["body_small"])],
        [Paragraph("Dados", st["body_small"]),
         Paragraph("Dataset histórico", st["body_small"]),
         Paragraph("22.742 registros de clientes, pré-processados e validados", st["body_small"]),
         Paragraph("Pandas · CSV", st["body_small"])],
        [Paragraph("Balanceamento", st["body_small"]),
         Paragraph("SMOTE", st["body_small"]),
         Paragraph("Oversampling da classe minoritária (maus pagadores, 2,3% do total)", st["body_small"]),
         Paragraph("Imbalanced-learn 0.14", st["body_small"])],
    ]
    arch_t = Table(arch_data,
                   colWidths=[LARGURA_UTIL * 0.16, LARGURA_UTIL * 0.18,
                               LARGURA_UTIL * 0.42, LARGURA_UTIL * 0.24])
    arch_t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), ROXO_PRIMARIO),
        ("TEXTCOLOR",   (0, 0), (-1, 0), BRANCO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 10),
        ("ALIGN",       (0, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(arch_t)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Estrutura de arquivos do projeto:", st["h3"]))
    files = [
        ("app.py",           "Aplicação principal Streamlit — interface, regras e orquestração"),
        ("utils.py",         "Transformers customizados do pipeline scikit-learn"),
        ("retrain_model.py", "Script reproduzível de retreinamento do modelo"),
        ("modelo/xgb.joblib","Modelo serializado (GradientBoostingClassifier treinado)"),
        ("df_clean.csv",     "Dataset limpo e consolidado (22.742 registros)"),
        ("dados/",           "Dados brutos históricos (clientes cadastrados e aprovados)"),
        (".streamlit/",      "Configuração de tema visual da aplicação"),
    ]
    story.append(kv_table(files, header=("Arquivo / Pasta", "Função")))

    story.append(PageBreak())

    # ── 4. Dados ──────────────────────────────────────────────────────────
    story.append(Paragraph("4. Fonte de Dados e Preparação", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "Os dados utilizados foram obtidos a partir de duas fontes históricas complementares: "
        "<b>clientes_cadastrados.csv</b> (perfil socioeconômico dos solicitantes) e "
        "<b>clientes_aprovados.csv</b> (histórico de comportamento de pagamento após aprovação). "
        "A variável-alvo <b>Mau</b> foi construída identificando clientes com atraso superior "
        "a 60 dias em qualquer mês da janela de observação de 12 meses.", st["body"]))

    story.append(Paragraph("Etapas do pré-processamento:", st["h3"]))
    prep_steps = [
        ("Remoção de duplicatas", "Clientes com ID_Cliente duplicado foram eliminados para evitar data leakage."),
        ("Tratamento de nulos", "Coluna Ocupacao: valores ausentes substituídos por 'Outro'."),
        ("Remoção de colunas", "Genero e Tem_celular removidos (baixíssima correlação, risco de viés)."),
        ("Conversão de datas", "Idade e Anos_empregado transformados de dias negativos para anos positivos."),
        ("Outliers de renda", "Clientes com renda além de 2 desvios-padrão da média removidos."),
        ("Janela de observação", "Apenas clientes com 12+ meses de histórico incluídos (estabilidade do label)."),
        ("Merge e target", "Join entre cadastro e aprovados; função verifica() classifica como Mau (1) ou Bom (0)."),
    ]
    story.append(kv_table(prep_steps, header=("Etapa", "Descrição")))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "O dataset final possui <b>22.742 registros</b>, com distribuição de classes altamente "
        "desbalanceada: <b>97,7% Bom pagador</b> e apenas <b>2,3% Mau pagador</b>. "
        "Este desbalanceamento exigiu tratamento específico na etapa de modelagem.", st["body"]))

    story.append(PageBreak())

    # ── 5. Feature Engineering ────────────────────────────────────────────
    story.append(Paragraph("5. Engenharia de Features", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "Além das variáveis originais, foram criadas quatro <b>features derivadas</b> que capturam "
        "dimensões de risco mais sofisticadas, elevando o AUC do modelo de 0,61 para 0,69 (+13%):", st["body"]))

    feats = [
        ("Renda_per_capita",      "Rendimento_anual ÷ Tamanho_familia",
         "Captura a carga financeira real por membro dependente. Famílias grandes com renda "
         "baixa têm maior propensão à inadimplência."),
        ("Score_patrimonio",      "Tem_carro + Tem_casa_propria (0 a 2)",
         "Proxy de solidez patrimonial. Clientes sem qualquer patrimônio representam risco maior."),
        ("Score_contatos",        "Telefone_trabalho + Telefone_fixo + Email (0 a 3)",
         "Indicador de verificabilidade e estabilidade. Mais canais de contato = menor risco de fuga."),
        ("Renda_por_ano_emprego", "Rendimento_anual ÷ max(Anos_empregado, 0.5)",
         "Estabilidade da trajetória profissional. Renda crescente com anos de experiência "
         "indica consistência financeira."),
    ]
    for name, formula, desc in feats:
        feat_block = KeepTogether([
            Paragraph(name, st["h3"]),
            Table([[
                Paragraph(f"<b>Fórmula:</b> <font color='#6E42AD'>{formula}</font>",
                          st["body_small"]),
            ]], colWidths=[LARGURA_UTIL]),
            Paragraph(desc, st["body_small"]),
            Spacer(1, 6),
        ])
        story.append(feat_block)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Pipeline de transformação de dados:", st["h3"]))
    story.append(Paragraph(
        "Todas as transformações são encapsuladas em um <b>Pipeline scikit-learn</b> com "
        "transformers customizados, garantindo que o mesmo pré-processamento seja aplicado "
        "de forma idêntica em treino e produção:", st["body_small"]))
    pipeline_steps = [
        ("1. DropFeatures",        "Remove ID_Cliente (identificador sem valor preditivo)"),
        ("2. OneHotEncodingNames",  "One-Hot Encoding: Estado_civil, Moradia, Categoria_de_renda, Ocupacao"),
        ("3. OrdinalFeature",       "Encoding ordinal: Grau_escolaridade (do fundamental à pós-graduação)"),
        ("4. MinMaxWithFeatNames",  "Normalização Min-Max: features numéricas e features derivadas"),
        ("5. Oversample (treino)",  "SMOTE — oversampling da classe Mau para balancear o treino"),
    ]
    story.append(kv_table(pipeline_steps, header=("Etapa do Pipeline", "Transformação")))

    story.append(PageBreak())

    # ── 6. Modelagem ──────────────────────────────────────────────────────
    story.append(Paragraph("6. Modelagem e Machine Learning", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "O algoritmo escolhido foi o <b>GradientBoostingClassifier</b> (Scikit-learn), "
        "um método de ensemble baseado em boosting sequencial de árvores de decisão. "
        "A escolha se justifica por sua robustez a dados desbalanceados, capacidade de "
        "capturar interações não-lineares entre features e boa performance em datasets "
        "tabulares de crédito.", st["body"]))

    story.append(Paragraph("Hiperparâmetros configurados:", st["h3"]))
    hps = [
        ("n_estimators",   "300", "Número de árvores — maior = melhor generalização"),
        ("learning_rate",  "0.05", "Taxa de aprendizado — baixa para evitar overfitting"),
        ("max_depth",      "4", "Profundidade máxima das árvores — controle de complexidade"),
        ("min_samples_leaf","20", "Mínimo de amostras por folha — regularização"),
        ("subsample",      "0.8", "Fração do dataset em cada iteração — stochastic boosting"),
        ("random_state",   "1561651", "Semente para reprodutibilidade dos resultados"),
    ]
    hp_data = [[Paragraph("<b>Parâmetro</b>", st["badge"]),
                Paragraph("<b>Valor</b>", st["badge"]),
                Paragraph("<b>Justificativa</b>", st["badge"])]]
    for p, v, j in hps:
        hp_data.append([Paragraph(p, ParagraphStyle("code", fontName="Courier",
                                  fontSize=10, textColor=ROXO_PRIMARIO)),
                        Paragraph(f"<b>{v}</b>", st["body_small"]),
                        Paragraph(j, st["body_small"])])
    hp_t = Table(hp_data, colWidths=[LARGURA_UTIL * 0.28, LARGURA_UTIL * 0.12, LARGURA_UTIL * 0.60])
    hp_t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), ROXO_ESCURO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRANCO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (0, 0), (-1, 0), "CENTER"),
        ("ALIGN",        (1, 1), (1, -1), "CENTER"),
    ]))
    story.append(hp_t)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Tratamento do desbalanceamento com SMOTE:", st["h3"]))
    story.append(Paragraph(
        "Com apenas 2,3% de maus pagadores no dataset, o modelo treinado sem balanceamento "
        "tenderia a prever sempre 'Bom pagador'. A técnica <b>SMOTE (Synthetic Minority "
        "Oversampling Technique)</b> foi aplicada apenas ao conjunto de treino, gerando "
        "amostras sintéticas da classe minoritária até equiparar as distribuições. "
        "O conjunto de teste manteve a distribuição original para avaliação realista.", st["body"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Calibração do Threshold de Decisão:", st["h3"]))
    story.append(Paragraph(
        "Em vez de utilizar o limiar padrão de 0,5 do método <code>predict()</code>, "
        "o sistema utiliza <code>predict_proba()</code> e um <b>threshold configurável</b>. "
        "Para um negócio de crédito, é preferível ter mais falsos negativos (bons pagadores "
        "rejeitados) do que falsos positivos (maus pagadores aprovados). O padrão adotado "
        "é <b>threshold = 0,10</b>, capturando 83% dos maus pagadores.", st["body"]))

    thresh_data = [
        [Paragraph("<b>Threshold</b>", st["badge"]),
         Paragraph("<b>Recall Mau</b>", st["badge"]),
         Paragraph("<b>Maus aprovados (FN)</b>", st["badge"]),
         Paragraph("<b>Indicação</b>", st["badge"])],
        ["0,50 (padrão ML)", "26%", "71 de 96", "❌ Insuficiente para crédito"],
        ["0,30",             "57%", "41 de 96", "⚠️ Conservador médio"],
        ["0,20",             "82%", "17 de 96", "✅ Recomendado — conservador"],
        ["0,10 (padrão app)","83%", "16 de 96", "✅✅ Recomendado — proteção máxima"],
    ]
    td = Table(thresh_data,
               colWidths=[LARGURA_UTIL * 0.18, LARGURA_UTIL * 0.18,
                           LARGURA_UTIL * 0.30, LARGURA_UTIL * 0.34])
    td.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), ROXO_PRIMARIO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRANCO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("BACKGROUND",   (0, 4), (-1, 4), colors.HexColor("#E8F8EE")),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(td)

    story.append(PageBreak())

    # ── 7. Política de Crédito ────────────────────────────────────────────
    story.append(Paragraph("7. Política de Concessão de Crédito", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "Antes de consultar o modelo de ML, o sistema aplica uma <b>camada de regras de negócio "
        "determinísticas</b> (Policy Rules), replicando práticas adotadas por instituições "
        "financeiras regulamentadas. Caso qualquer regra seja violada, o crédito é negado "
        "automaticamente com o motivo explicitado ao analista.", st["body"]))

    story.append(Spacer(1, 0.3 * cm))

    rules = [
        ("Regra 1 · Renda Mínima Absoluta",
         "Renda anual < R$ 7.200 (R$ 600/mês)",
         "Garante que o solicitante tenha capacidade mínima de pagamento mensal."),
        ("Regra 2 · Renda Per Capita Familiar",
         "Renda per capita < R$ 3.600/ano/membro",
         "Avalia o comprometimento real da renda com obrigações familiares."),
        ("Regra 3 · Estudante sem Renda Suficiente",
         "Categoria 'Estudante' com renda < R$ 18.000/ano",
         "Estudantes sem renda comprovada de R$ 1.500/mês requerem fiador."),
        ("Regra 4 · Perfil Jovem de Alto Risco",
         "Idade < 21 anos + sem patrimônio + < 1 ano de emprego + renda < R$ 27.000",
         "Combinação de fatores que historicamente resulta em inadimplência elevada."),
    ]

    for title, cond, rationale in rules:
        rule_t = Table([
            [Paragraph(title, ParagraphStyle("rule_title",
                fontName="Helvetica-Bold", fontSize=10,
                textColor=BRANCO))],
            [Paragraph(f"<b>Condição:</b> {cond}", st["body_small"])],
            [Paragraph(f"<b>Fundamento:</b> {rationale}", st["body_small"])],
        ], colWidths=[LARGURA_UTIL])
        rule_t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (0, 0), ROXO_PRIMARIO),
            ("BACKGROUND",   (0, 1), (0, 1), colors.HexColor("#F3ECFF")),
            ("BACKGROUND",   (0, 2), (0, 2), CINZA_CLARO),
            ("LEFTPADDING",  (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("LINEBELOW",    (0, -1), (-1, -1), 1, ROXO_CLARO),
        ]))
        story.append(rule_t)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Esta abordagem em <b>duas camadas</b> é fundamental: as regras de negócio capturam "
        "casos que o modelo estatístico não consegue avaliar corretamente — especialmente "
        "perfis fora da distribuição de treino (ex: renda declarada muito abaixo do mínimo "
        "histórico de R$ 27.000/ano). O modelo ML, por sua vez, discrimina entre perfis que "
        "passam nos critérios mínimos mas apresentam padrões mais sutis de risco.", st["body"]))

    story.append(PageBreak())

    # ── 8. Interface ──────────────────────────────────────────────────────
    story.append(Paragraph("8. Interface e Funcionalidades", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "A aplicação web desenvolvida com <b>Streamlit</b> oferece uma interface intuitiva "
        "para solicitação e avaliação de crédito em tempo real. O fluxo completo é executado "
        "no momento em que o analista clica em <b>Enviar</b>.", st["body"]))

    story.append(Paragraph("Campos do formulário:", st["h3"]))
    campos = [
        ("Dados Pessoais",    "Idade, Grau de escolaridade, Estado civil, Tamanho da família"),
        ("Patrimônio",        "Possui automóvel, Possui imóvel próprio, Tipo de residência"),
        ("Financeiro",        "Categoria de renda, Rendimento anual, Ocupação"),
        ("Profissional",      "Tempo de experiência em anos"),
        ("Contato",           "Telefone corporativo, Telefone fixo, E-mail"),
    ]
    story.append(kv_table(campos, header=("Categoria", "Variáveis")))

    story.append(Paragraph("Funcionalidades entregues:", st["h3"]))
    funcs = [
        "Formulário interativo com sliders, selectboxes e radio buttons",
        "Painel lateral com configuração do threshold de risco (0,05 a 0,50)",
        "Avaliação em tempo real com duas camadas: Policy Rules → Modelo ML",
        "Exibição do score de risco (probabilidade de inadimplência em %)",
        "Barra de progresso visual do nível de risco",
        "Feedback explícito dos motivos de rejeição quando aplicável",
        "Tema visual personalizado com paleta corporativa (roxo/dark)",
    ]
    for f in funcs:
        story.append(Paragraph(f"• {f}", st["body_small"]))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Fluxo de decisão:", st["h3"]))

    flow_data = [
        [Paragraph("ENTRADA", st["badge"]),
         Paragraph("→", st["badge"]),
         Paragraph("POLICY RULES", st["badge"]),
         Paragraph("→", st["badge"]),
         Paragraph("MODELO ML", st["badge"]),
         Paragraph("→", st["badge"]),
         Paragraph("DECISÃO", st["badge"])],
        [Paragraph("Dados do formulário", st["body_small"]),
         Paragraph("", st["body_small"]),
         Paragraph("4 regras de negócio hard", st["body_small"]),
         Paragraph("", st["body_small"]),
         Paragraph("predict_proba + threshold", st["body_small"]),
         Paragraph("", st["body_small"]),
         Paragraph("Aprovado / Negado + motivo", st["body_small"])],
    ]
    flow_t = Table(flow_data,
                   colWidths=[LARGURA_UTIL * 0.18, 0.5 * cm,
                               LARGURA_UTIL * 0.20, 0.5 * cm,
                               LARGURA_UTIL * 0.20, 0.5 * cm,
                               LARGURA_UTIL * 0.20])
    flow_t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0), ROXO_ESCURO),
        ("BACKGROUND",   (2, 0), (2, 0), ROXO_PRIMARIO),
        ("BACKGROUND",   (4, 0), (4, 0), colors.HexColor("#5B3494")),
        ("BACKGROUND",   (6, 0), (6, 0), VERDE_ACENTO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRANCO),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
    ]))
    story.append(flow_t)

    story.append(PageBreak())

    # ── 9. Resultados ─────────────────────────────────────────────────────
    story.append(Paragraph("9. Resultados e Métricas", st["h2"]))
    story.append(section_divider())

    # Cards de métricas
    metrics_row = [
        metric_card("AUC · ROC", "0,69", "GradientBoosting + Feature Eng.", ROXO_PRIMARIO),
        metric_card("Recall Mau", "83%",  "Com threshold 0,10", ROXO_ESCURO),
        metric_card("Melhoria AUC", "+13%", "vs. baseline sem feature eng.", colors.HexColor("#5B3494")),
        metric_card("Maus Capturados", "80 / 96", "Conjunto de teste — 4.549 reg.", colors.HexColor("#3D1F6E")),
    ]
    m_t = Table([metrics_row],
                colWidths=[LARGURA_UTIL / 4 - 4] * 4, hAlign="LEFT")
    m_t.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    story.append(m_t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(
        "A evolução mais significativa foi a adição da <b>feature engineering</b> que elevou "
        "o AUC de <b>0,61 → 0,69</b>. A combinação com as regras de negócio cobre os casos "
        "que o modelo probabilístico não consegue discriminar (perfis fora da distribuição "
        "de treino), tornando o sistema muito mais robusto do que qualquer abordagem isolada.", st["body"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Comparação de abordagens:", st["h3"]))
    comp = [
        [Paragraph("<b>Abordagem</b>", st["badge"]),
         Paragraph("<b>AUC</b>", st["badge"]),
         Paragraph("<b>Recall Mau @ 0,10</b>", st["badge"]),
         Paragraph("<b>Limitação</b>", st["badge"])],
        ["Modelo original (sklearn 1.0.2)", "~0,61", "—", "Incompatível com Python 3.13"],
        ["Baseline retreinado", "0,61", "83%", "Sem features derivadas"],
        ["Com feature engineering", "0,69", "83%", "AUC ainda moderado"],
        ["+ Policy Rules (sistema final)", "0,69", "100% dos bloqueados por regras", "Melhor proteção"],
    ]
    comp_t = Table(comp,
                   colWidths=[LARGURA_UTIL * 0.35, LARGURA_UTIL * 0.12,
                               LARGURA_UTIL * 0.23, LARGURA_UTIL * 0.30])
    comp_t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), ROXO_PRIMARIO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRANCO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("BACKGROUND",   (0, 4), (-1, 4), colors.HexColor("#E8F8EE")),
        ("FONTNAME",     (0, 4), (-1, 4), "Helvetica-Bold"),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(comp_t)

    story.append(PageBreak())

    # ── 10. Conclusão ─────────────────────────────────────────────────────
    story.append(Paragraph("10. Conclusões e Próximos Passos", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "O projeto entrega um sistema funcional, robusto e alinhado com práticas reais do "
        "mercado de crédito. A arquitetura em duas camadas — Policy Rules + ML — demonstra "
        "maturidade técnica ao reconhecer que modelos estatísticos, por mais sofisticados "
        "que sejam, precisam ser complementados por regras de negócio explícitas e auditáveis.", st["body"]))

    story.append(Paragraph("Principais conquistas técnicas:", st["h3"]))
    conquistas = [
        "Migração completa do ambiente de Python 3.x antigo para Python 3.13, resolvendo incompatibilidades de serialização do modelo",
        "Feature engineering que elevou o AUC em +13% sem alterar o algoritmo base",
        "Implementação de threshold calibrado (0,10) que captura 83% dos maus pagadores",
        "Camada de Policy Rules que cobre 100% dos casos fora da distribuição de treino",
        "Interface Streamlit com sidebar configurável para ajuste de risco em tempo real",
        "Pipeline scikit-learn reproduzível com transformers customizados em utils.py",
        "Script retrain_model.py para retreinamento completo com uma linha de comando",
    ]
    for c in conquistas:
        story.append(Paragraph(f"✔  {c}", st["body_small"]))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Próximos passos sugeridos:", st["h3"]))
    proximos = [
        ("Ampliar o dataset",          "Incorporar dados de bureau de crédito (Serasa/SPC) para features mais preditivas"),
        ("Explicabilidade (XAI)",       "Integrar SHAP values para explicar cada decisão individualmente ao analista"),
        ("Monitoramento de drift",      "Implementar monitoramento de data drift com Evidently AI ou Great Expectations"),
        ("A/B Testing de políticas",    "Testar diferentes thresholds em grupos de controle para otimizar o tradeoff risco/receita"),
        ("Deploy em cloud",             "Containerizar a aplicação com Docker e publicar em Streamlit Cloud ou AWS EC2"),
        ("Score de crédito contínuo",   "Substituir decisão binária por score de 0–1000, similar ao modelo Serasa Score"),
        ("Retraining automatizado",     "Pipeline MLOps com retreinamento mensal automático via GitHub Actions ou Airflow"),
    ]
    story.append(kv_table(proximos, header=("Iniciativa", "Descrição")))

    story.append(Spacer(1, 0.8 * cm))

    # Caixa de fechamento
    closing = Table([[
        Paragraph(
            "<b>Este projeto demonstra a aplicação prática de Ciência de Dados ao problema de "
            "concessão de crédito — um dos domínios de maior impacto econômico para instituições "
            "financeiras. A combinação de rigor técnico com visão de negócio é o diferencial "
            "que transforma um modelo de ML em uma ferramenta real de decisão.</b>",
            ParagraphStyle("closing", fontName="Helvetica-Bold", fontSize=11,
                           leading=18, alignment=TA_CENTER, textColor=BRANCO))
    ]], colWidths=[LARGURA_UTIL])
    closing.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), ROXO_ESCURO),
        ("LEFTPADDING",  (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
        ("TOPPADDING",   (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 20),
    ]))
    story.append(closing)


# ── ANEXO TÉCNICO ────────────────────────────────────────────────────────────
def build_code_annex(story, st):
    story.append(PageBreak())
    story.append(Paragraph("11. Anexo Técnico — Código-Fonte", st["h2"]))
    story.append(section_divider())
    story.append(Paragraph(
        "Esta seção apresenta trechos representativos dos principais módulos da solução, "
        "demonstrando a existência e a qualidade técnica de cada componente implementado. "
        "Os códigos completos estão disponíveis no repositório do projeto.", st["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # ── app.py ────────────────────────────────────────────────────────────────
    story.append(Paragraph("app.py — Aplicação Principal (Streamlit)", st["h3"]))

    story.append(code_block(
        "app.py",
        "Importações e dependências",
        "import streamlit as st\n"
        "import pandas as pd\n"
        "from sklearn.model_selection import train_test_split\n"
        "from utils import DropFeatures, OneHotEncodingNames, OrdinalFeature, MinMaxWithFeatNames\n"
        "from sklearn.pipeline import Pipeline\n"
        "import joblib",
    ))

    story.append(code_block(
        "app.py",
        "Camada 1 — Policy Rules (regras de negócio hard)",
        "def aplicar_regras_negocio(\n"
        "        rendimento, membros_familia, categoria_renda,\n"
        "        grau_escolaridade, idade, anos_emprego, carro, casa, tipo_moradia):\n"
        "    motivos = []\n"
        "    RENDA_MINIMA_ANUAL   = 7_200    # R$ 600/mes -- minimo absoluto\n"
        "    RENDA_PER_CAPITA_MIN = 3_600    # R$ 300/mes por membro da familia\n"
        "    RENDA_ESTUDANTE_MIN  = 18_000   # R$ 1.500/mes -- estudante sem fiador\n"
        "    RENDA_DATASET_MIN    = 27_000   # minimo observado nos dados de treino\n"
        "    renda_per_capita = rendimento / max(membros_familia, 1)\n"
        "\n"
        "    if rendimento < RENDA_MINIMA_ANUAL:\n"
        "        motivos.append('Renda abaixo do minimo exigido de R$ 7.200/ano.')\n"
        "    if renda_per_capita < RENDA_PER_CAPITA_MIN:\n"
        "        motivos.append('Renda per capita familiar insuficiente.')\n"
        "    if categoria_renda == 'Estudante' and rendimento < RENDA_ESTUDANTE_MIN:\n"
        "        motivos.append('Estudantes precisam comprovar renda minima de R$ 1.500/mes.')\n"
        "\n"
        "    aprovado = len(motivos) == 0\n"
        "    return aprovado, motivos, aviso_fora_distribuicao",
    ))

    story.append(code_block(
        "app.py",
        "Camada 2 — Predição ML e exibição do resultado",
        "if st.button('Enviar'):\n"
        "    model = joblib.load('modelo/xgb.joblib')\n"
        "    prob = model.predict_proba(cliente_pred)\n"
        "    prob_mau = prob[-1][1]\n"
        "    prob_bom = prob[-1][0]\n"
        "\n"
        "    col1, col2 = st.columns(2)\n"
        "    col1.metric('Risco de inadimplencia', f'{prob_mau * 100:.1f}%')\n"
        "    col2.metric('Perfil positivo', f'{prob_bom * 100:.1f}%')\n"
        "    st.progress(float(prob_mau))\n"
        "\n"
        "    if prob_mau < threshold:\n"
        "        st.success('Cartao de credito aprovado!')\n"
        "        st.balloons()\n"
        "    else:\n"
        "        st.error('Credito nao liberado.')",
    ))

    story.append(PageBreak())

    # ── utils.py ──────────────────────────────────────────────────────────────
    story.append(Paragraph("utils.py — Transformers Customizados do Pipeline", st["h3"]))

    story.append(code_block(
        "utils.py",
        "DropFeatures e MinMaxWithFeatNames",
        "class DropFeatures(BaseEstimator, TransformerMixin):\n"
        "    def __init__(self, feature_to_drop=['ID_Cliente']):\n"
        "        self.feature_to_drop = feature_to_drop\n"
        "    def fit(self, df):\n"
        "        return self\n"
        "    def transform(self, df):\n"
        "        if set(self.feature_to_drop).issubset(df.columns):\n"
        "            df.drop(self.feature_to_drop, axis=1, inplace=True)\n"
        "        return df\n"
        "\n"
        "class MinMaxWithFeatNames(BaseEstimator, TransformerMixin):\n"
        "    def __init__(self, min_max_scaler_ft=[\n"
        "            'Idade', 'Rendimento_anual', 'Tamanho_familia', 'Anos_empregado',\n"
        "            'Renda_per_capita', 'Score_patrimonio', 'Score_contatos',\n"
        "            'Renda_por_ano_emprego']):\n"
        "        self.min_max_scaler_ft = min_max_scaler_ft\n"
        "    def fit(self, df):\n"
        "        return self\n"
        "    def transform(self, df):\n"
        "        cols = [c for c in self.min_max_scaler_ft if c in df.columns]\n"
        "        if cols:\n"
        "            df[cols] = MinMaxScaler().fit_transform(df[cols])\n"
        "        return df",
    ))

    # ── retrain_model.py ──────────────────────────────────────────────────────
    story.append(Paragraph("retrain_model.py — Script de Retreinamento", st["h3"]))

    story.append(code_block(
        "retrain_model.py",
        "Engenharia de features derivadas",
        "def criar_features_derivadas(df):\n"
        "    df = df.copy()\n"
        "    df['Renda_per_capita']      = df['Rendimento_anual'] / df['Tamanho_familia'].clip(lower=1)\n"
        "    df['Score_patrimonio']      = df['Tem_carro'] + df['Tem_casa_propria']\n"
        "    df['Score_contatos']        = (df['Tem_telefone_trabalho']\n"
        "                                   + df['Tem_telefone_fixo'] + df['Tem_email'])\n"
        "    df['Renda_por_ano_emprego'] = df['Rendimento_anual'] / df['Anos_empregado'].clip(lower=0.5)\n"
        "    return df",
    ))

    story.append(code_block(
        "retrain_model.py",
        "Treino, avaliação e persistência do modelo",
        "modelo = GradientBoostingClassifier(\n"
        "    n_estimators=300, learning_rate=0.05,\n"
        "    max_depth=4,      min_samples_leaf=20,\n"
        "    subsample=0.8,    random_state=SEED,\n"
        ")\n"
        "modelo.fit(X_train, y_train)\n"
        "\n"
        "probs = modelo.predict_proba(X_test)[:, 1]\n"
        "auc   = roc_auc_score(y_test, probs)\n"
        "print(f'AUC no teste: {auc:.4f}')\n"
        "\n"
        "joblib.dump(modelo, 'modelo/xgb.joblib')\n"
        "print('Modelo salvo em modelo/xgb.joblib')",
    ))


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=MARGEM_ESQ,
        rightMargin=MARGEM_DIR,
        topMargin=MARGEM_SUP,
        bottomMargin=MARGEM_INF,
        title="Sistema de Avaliação de Concessão de Crédito",
        author="Projeto de Ciência de Dados",
        subject="Credit Scoring com Machine Learning",
    )

    st = build_styles()
    story = []

    build_cover(story, st)
    build_toc(story, st)
    build_content(story, st)
    build_code_annex(story, st)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF gerado com sucesso: {OUTPUT}")


if __name__ == "__main__":
    main()
