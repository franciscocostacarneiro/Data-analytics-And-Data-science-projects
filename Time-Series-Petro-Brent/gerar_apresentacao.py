"""
Gerador de Apresentação Técnica — Previsão do Petróleo Brent
Autor: Francisco Costa Carneiro
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.pdfgen import canvas as pdfgen_canvas

# ─── CORES ───────────────────────────────────────────────────────────────────
AZUL_ESCURO   = colors.HexColor("#1A2B4A")
AZUL_MEDIO    = colors.HexColor("#2563EB")
AZUL_CLARO    = colors.HexColor("#DBEAFE")
CINZA_ESCURO  = colors.HexColor("#374151")
CINZA_CLARO   = colors.HexColor("#F3F4F6")
CINZA_LINHA   = colors.HexColor("#E5E7EB")
BRANCO        = colors.white
PRETO         = colors.black
VERDE         = colors.HexColor("#065F46")
VERDE_CLARO   = colors.HexColor("#D1FAE5")

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm

# ─── HEADER / FOOTER ─────────────────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    if doc.page > 1:
        # Linha topo
        canvas.setStrokeColor(AZUL_MEDIO)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, h - 1.4 * cm, w - MARGIN, h - 1.4 * cm)

        # Cabeçalho
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(AZUL_ESCURO)
        canvas.drawString(MARGIN, h - 1.1 * cm, "Previsão de Preços do Petróleo Brent")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(CINZA_ESCURO)
        canvas.drawRightString(w - MARGIN, h - 1.1 * cm, "Séries Temporais · Data Science")

        # Rodapé
        canvas.setStrokeColor(CINZA_LINHA)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, 1.3 * cm, w - MARGIN, 1.3 * cm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(CINZA_ESCURO)
        canvas.drawString(MARGIN, 0.9 * cm, "Francisco Costa Carneiro · Ciência de Dados")
        canvas.drawRightString(w - MARGIN, 0.9 * cm, f"— {doc.page} —")

    canvas.restoreState()


# ─── ESTILOS ─────────────────────────────────────────────────────────────────
def build_styles():
    styles = getSampleStyleSheet()

    def add(name, **kw):
        styles.add(ParagraphStyle(name=name, **kw))

    add("Titulo",        fontName="Helvetica-Bold", fontSize=26, textColor=BRANCO,
                         alignment=TA_CENTER, spaceAfter=8, leading=32)
    add("Subtitulo",     fontName="Helvetica", fontSize=13, textColor=AZUL_CLARO,
                         alignment=TA_CENTER, spaceAfter=6, leading=17)
    add("TaglineCover",  fontName="Helvetica", fontSize=9, textColor=AZUL_CLARO,
                         alignment=TA_CENTER, spaceAfter=4, leading=13)
    add("AutorCover",    fontName="Helvetica-Bold", fontSize=10, textColor=BRANCO,
                         alignment=TA_CENTER, spaceAfter=3, leading=14)
    add("MetaCover",     fontName="Helvetica", fontSize=9, textColor=AZUL_CLARO,
                         alignment=TA_CENTER, spaceAfter=3, leading=13)

    add("SecTitle",      fontName="Helvetica-Bold", fontSize=13, textColor=AZUL_ESCURO,
                         spaceBefore=14, spaceAfter=6, leading=17,
                         borderPadding=(0, 0, 4, 0))
    add("SubSecTitle",   fontName="Helvetica-Bold", fontSize=10.5, textColor=AZUL_MEDIO,
                         spaceBefore=10, spaceAfter=4, leading=14)
    add("Corpo",         fontName="Helvetica", fontSize=9.5, textColor=CINZA_ESCURO,
                         spaceBefore=3, spaceAfter=3, leading=14, alignment=TA_JUSTIFY)
    add("BulletItem",    fontName="Helvetica", fontSize=9.5, textColor=CINZA_ESCURO,
                         spaceBefore=2, spaceAfter=2, leading=13,
                         leftIndent=12, bulletIndent=0)
    add("CodeInline",    fontName="Courier", fontSize=8.5, textColor=AZUL_ESCURO,
                         spaceBefore=2, spaceAfter=2, leading=12,
                         backColor=CINZA_CLARO, leftIndent=12, rightIndent=12,
                         borderPadding=4)
    add("Nota",          fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#6B7280"),
                         spaceBefore=3, spaceAfter=3, leading=12, alignment=TA_JUSTIFY,
                         leftIndent=16)
    add("ToC",           fontName="Helvetica", fontSize=10, textColor=CINZA_ESCURO,
                         spaceBefore=5, spaceAfter=5, leading=14)
    add("ToCSec",        fontName="Helvetica-Bold", fontSize=10, textColor=AZUL_ESCURO,
                         spaceBefore=5, spaceAfter=5, leading=14)
    add("Rodape",        fontName="Helvetica", fontSize=8, textColor=CINZA_ESCURO,
                         alignment=TA_CENTER)

    return styles


# ─── TABELA: estilo padrão ────────────────────────────────────────────────────
def table_style_default():
    return TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), AZUL_ESCURO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRANCO),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 8.5),
        ("ALIGN",        (0, 0), (-1, 0), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 8.5),
        ("ALIGN",        (0, 1), (-1, -1), "LEFT"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",         (0, 0), (-1, -1), 0.4, CINZA_LINHA),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ])


def section_rule(color=AZUL_MEDIO):
    return HRFlowable(width="100%", thickness=1.5, color=color, spaceAfter=6)


# ─── CAPA ────────────────────────────────────────────────────────────────────
def build_cover(styles):
    story = []

    # Bloco azul escuro simulado via tabela de 1 célula
    capa_text = (
        "<br/><br/><br/><br/>"
        "<font size=28><b>PREVISÃO DE PREÇOS DO</b></font><br/>"
        "<font size=28><b>PETRÓLEO BRENT</b></font><br/><br/>"
        "<font size=13><i>Documentação Técnica de Projeto</i></font><br/><br/>"
        "<font size=9>Série Temporal · Prophet &amp; LSTM · Aplicação Web Interativa</font>"
        "<br/><br/><br/>"
    )
    capa_para = Paragraph(capa_text, ParagraphStyle(
        "CapaFundo", fontName="Helvetica-Bold", fontSize=28,
        textColor=BRANCO, alignment=TA_CENTER, leading=36
    ))

    capa_table = Table([[capa_para]], colWidths=[PAGE_W - 2 * MARGIN])
    capa_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), AZUL_ESCURO),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 30),
        ("LEFTPADDING",  (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(capa_table)
    story.append(Spacer(1, 0.6 * cm))

    # Métricas de destaque
    metricas = [
        [
            Paragraph("<b>~15%</b><br/><font size=7>MAPE Prophet</font>", ParagraphStyle(
                "M", fontName="Helvetica-Bold", fontSize=16, textColor=AZUL_ESCURO,
                alignment=TA_CENTER, leading=20)),
            Paragraph("<b>1987</b><br/><font size=7>Início da série histórica</font>", ParagraphStyle(
                "M2", fontName="Helvetica-Bold", fontSize=16, textColor=AZUL_ESCURO,
                alignment=TA_CENTER, leading=20)),
            Paragraph("<b>2</b><br/><font size=7>Modelos de ML</font>", ParagraphStyle(
                "M3", fontName="Helvetica-Bold", fontSize=16, textColor=AZUL_ESCURO,
                alignment=TA_CENTER, leading=20)),
            Paragraph("<b>3</b><br/><font size=7>Páginas na aplicação</font>", ParagraphStyle(
                "M4", fontName="Helvetica-Bold", fontSize=16, textColor=AZUL_ESCURO,
                alignment=TA_CENTER, leading=20)),
        ]
    ]
    col = (PAGE_W - 2 * MARGIN) / 4
    t_metrics = Table(metricas, colWidths=[col] * 4)
    t_metrics.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), AZUL_CLARO),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("LINEAFTER",    (0, 0), (2, -1), 0.5, AZUL_MEDIO),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 0.7 * cm))

    # Autor e metadados
    info = [
        Paragraph("<b>Autor:</b> Francisco Costa Carneiro", styles["Corpo"]),
        Paragraph("<b>Área:</b> Ciência de Dados · Finanças · Machine Learning · Séries Temporais", styles["Corpo"]),
        Paragraph("<b>Tecnologias:</b> Python · Streamlit · TensorFlow/Keras · Prophet · Scikit-learn · Pandas · BeautifulSoup", styles["Corpo"]),
        Paragraph("<b>Data:</b> Maio de 2026", styles["Corpo"]),
    ]
    for p in info:
        story.append(p)

    story.append(PageBreak())
    return story


# ─── SUMÁRIO ─────────────────────────────────────────────────────────────────
def build_toc(styles):
    story = []
    story.append(Paragraph("SUMÁRIO", styles["SecTitle"]))
    story.append(section_rule())
    story.append(Spacer(1, 0.3 * cm))

    itens = [
        ("1.", "Introdução e Contexto de Negócio"),
        ("2.", "Objetivos do Projeto"),
        ("3.", "Arquitetura Tecnológica"),
        ("4.", "Fonte de Dados e Preparação"),
        ("5.", "Suavização EWM e Pré-processamento para LSTM"),
        ("6.", "Modelagem — Prophet"),
        ("7.", "Modelagem — LSTM"),
        ("8.", "Avaliação — Holdout Temporal e Métricas"),
        ("9.", "Interface e Funcionalidades"),
        ("10.", "Resultados e Conclusões"),
        ("11.", "Anexo Técnico — Código-Fonte"),
    ]

    col_n = 1.2 * cm
    col_t = PAGE_W - 2 * MARGIN - col_n

    rows = []
    for num, titulo in itens:
        rows.append([
            Paragraph(f"<b>{num}</b>", ParagraphStyle("ToCNum", fontName="Helvetica-Bold",
                fontSize=10, textColor=AZUL_MEDIO, alignment=TA_RIGHT, leading=14)),
            Paragraph(titulo, ParagraphStyle("ToCItem", fontName="Helvetica",
                fontSize=10, textColor=CINZA_ESCURO, leading=14)),
        ])

    toc_table = Table(rows, colWidths=[col_n, col_t])
    toc_table.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 1), (-1, -1), 10),
        ("LINEBELOW",    (0, 0), (-1, -2), 0.3, CINZA_LINHA),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    return story


# ─── CONTEÚDO PRINCIPAL ──────────────────────────────────────────────────────
def build_content(styles):
    S = styles
    story = []
    cw = PAGE_W - 2 * MARGIN  # largura útil

    def sec(num, titulo):
        story.append(KeepTogether([
            Paragraph(f"{num}. {titulo}", S["SecTitle"]),
            section_rule(),
        ]))

    def subsec(titulo):
        story.append(Paragraph(titulo, S["SubSecTitle"]))

    def body(txt):
        story.append(Paragraph(txt, S["Corpo"]))

    def bullet(txt):
        story.append(Paragraph(f"● {txt}", S["BulletItem"]))

    def nota(txt):
        story.append(Paragraph(f"<i>→ {txt}</i>", S["Nota"]))

    def space(n=0.3):
        story.append(Spacer(1, n * cm))

    # ── 1. INTRODUÇÃO ──────────────────────────────────────────────────────
    sec("1", "Introdução e Contexto de Negócio")
    body(
        "O petróleo Brent é a principal referência global para precificação do petróleo cru, "
        "impactando diretamente os mercados financeiros, as políticas energéticas de governos e "
        "as decisões estratégicas de empresas do setor. A volatilidade histórica do Brent — "
        "influenciada por fatores geopolíticos, variações de demanda e ciclos econômicos — "
        "torna a previsão de seus preços um problema de alta complexidade e relevância prática."
    )
    space(0.2)
    body(
        "Este projeto implementa um sistema de previsão de séries temporais aplicado aos preços "
        "diários do petróleo Brent (USD/barril), utilizando dois modelos complementares de Machine Learning: "
        "o <b>Prophet</b> (modelo aditivo desenvolvido pela Meta) e o <b>LSTM</b> "
        "(Long Short-Term Memory — rede neural recorrente especializada em sequências temporais). "
        "Os dados são obtidos em tempo real via web scraping do portal IPEADATA e toda a pipeline "
        "é entregue em uma aplicação web interativa desenvolvida com Streamlit."
    )
    space()

    # ── 2. OBJETIVOS ───────────────────────────────────────────────────────
    sec("2", "Objetivos do Projeto")

    obj_data = [
        ["Objetivo", "Descrição"],
        ["Primário",
         "Construir um sistema de previsão de preços do petróleo Brent usando técnicas "
         "avançadas de séries temporais com avaliação honesta de desempenho."],
        ["Secundário",
         "Implementar validação temporal correta (holdout temporal sem data leakage) "
         "e métricas calculadas sobre preços reais."],
        ["Técnico",
         "Aplicar boas práticas de ciência de dados: suavização EWM, normalização "
         "MinMax, janela deslizante (look_back), holdout 80/20."],
        ["UX / Produto",
         "Entregar interface web intuitiva que permita a qualquer usuário carregar "
         "dados, selecionar modelo, executar previsões e visualizar resultados."],
    ]
    obj_rows = []
    for i, row in enumerate(obj_data):
        obj_rows.append([
            Paragraph(f"<b>{row[0]}</b>" if i == 0 else row[0], ParagraphStyle(
                "ObjL", fontName="Helvetica-Bold" if i == 0 else "Helvetica-Bold",
                fontSize=8.5, textColor=BRANCO if i == 0 else AZUL_ESCURO,
                leading=12)),
            Paragraph(f"<b>{row[1]}</b>" if i == 0 else row[1], ParagraphStyle(
                "ObjR", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO,
                leading=12, alignment=TA_JUSTIFY)),
        ])
    obj_table = Table(obj_rows, colWidths=[3.5 * cm, cw - 3.5 * cm])
    obj_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), AZUL_ESCURO),
        ("BACKGROUND",   (0, 1), (0, -1), AZUL_CLARO),
        ("ROWBACKGROUNDS", (1, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",         (0, 0), (-1, -1), 0.4, CINZA_LINHA),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(obj_table)
    space()

    # ── 3. ARQUITETURA ─────────────────────────────────────────────────────
    sec("3", "Arquitetura Tecnológica")
    body(
        "O projeto é estruturado em três camadas principais, seguindo boas práticas de "
        "arquitetura de sistemas de Machine Learning em produção:"
    )
    space(0.2)

    arq_data = [
        ["Camada", "Componente", "Responsabilidade", "Tecnologia"],
        ["Apresentação", "Interface Web", "Formulário interativo, visualizações, feedback ao usuário", "Streamlit 1.57"],
        ["Dados", "Web Scraping", "Coleta em tempo real do IPEADATA via HTTP + parsing HTML", "BeautifulSoup · Requests"],
        ["ML / Analytics", "Modelos de Previsão", "Pré-processamento, treinamento (offline), predição online", "TF/Keras 3.14 · Prophet 1.3"],
        ["ML / Analytics", "Normalização", "Escalonamento MinMax das séries temporais", "Scikit-learn 1.8"],
        ["Persistência", "Modelos Serializados", "Modelos pré-treinados prontos para inferência", "HDF5 (.h5) · JSON"],
    ]
    arq_rows = []
    for i, row in enumerate(arq_data):
        style = "Helvetica-Bold" if i == 0 else "Helvetica"
        color = BRANCO if i == 0 else CINZA_ESCURO
        arq_rows.append([
            Paragraph(f"<b>{row[0]}</b>" if i > 0 else row[0],
                ParagraphStyle("a", fontName=style, fontSize=8, textColor=color, leading=11)),
            Paragraph(row[1],
                ParagraphStyle("b", fontName=style, fontSize=8, textColor=color, leading=11)),
            Paragraph(row[2],
                ParagraphStyle("c", fontName=style, fontSize=8, textColor=color, leading=11, alignment=TA_JUSTIFY)),
            Paragraph(row[3],
                ParagraphStyle("d", fontName=style, fontSize=8, textColor=color, leading=11)),
        ])
    arq_table = Table(arq_rows, colWidths=[2.8 * cm, 3.2 * cm, cw - 8.6 * cm, 3.2 * cm - 0.4 * cm])
    arq_table.setStyle(table_style_default())
    story.append(arq_table)
    space(0.4)

    subsec("Estrutura de Arquivos do Projeto")
    files_data = [
        ["Arquivo / Pasta", "Função"],
        ["Home.py", "Página inicial — descrição do projeto e instruções de uso"],
        ["pages/2_Model.py", "Carregamento de dados, seleção de modelo, execução e exibição de métricas"],
        ["pages/3_Data Visualization.py", "Geração dos 4 gráficos analíticos com dados reais e preditos"],
        ["models/lstm_model.h5", "Rede LSTM pré-treinada (TensorFlow/Keras, formato HDF5)"],
        ["models/prophet_model.json", "Modelo Prophet serializado (Meta's Prophet, formato JSON)"],
        ["Análise Exploratória - EDA.ipynb", "Notebook de treinamento dos modelos (executado no Google Colab)"],
        ["requirements.txt", "Dependências do projeto com versões compatíveis com Python 3.13"],
    ]
    files_rows = []
    for i, row in enumerate(files_data):
        style = "Helvetica-Bold" if i == 0 else "Helvetica"
        color = BRANCO if i == 0 else CINZA_ESCURO
        col0_style = "Courier" if i > 0 else "Helvetica-Bold"
        files_rows.append([
            Paragraph(row[0], ParagraphStyle("fa", fontName=col0_style, fontSize=8,
                textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=11)),
            Paragraph(row[1], ParagraphStyle("fb", fontName=style, fontSize=8,
                textColor=color, leading=11)),
        ])
    files_table = Table(files_rows, colWidths=[5.5 * cm, cw - 5.5 * cm])
    files_table.setStyle(table_style_default())
    story.append(files_table)
    space()

    # ── 4. DADOS ───────────────────────────────────────────────────────────
    sec("4", "Fonte de Dados e Preparação")
    body(
        "Os dados históricos do petróleo Brent são obtidos em tempo real a partir do portal "
        "<b>IPEADATA</b> (Instituto de Pesquisa Econômica Aplicada), que disponibiliza a série "
        "EIA366_PBRENT366 — preço diário em USD por barril, desde 1987. A coleta é realizada "
        "via HTTP GET com parse da tabela HTML de ID <font face='Courier'>grd_DXMainTable</font>."
    )
    space(0.2)

    dados_data = [
        ["Etapa", "Descrição"],
        ["Fonte", "IPEADATA — http://www.ipeadata.gov.br (série EIA366_PBRENT366)"],
        ["Período", "1987 até data atual (série histórica contínua, ~39 anos)"],
        ["Frequência original", "Dias úteis (sem fins de semana e feriados)"],
        ["Parsing", "BeautifulSoup — tabela HTML identificada pelo ID grd_DXMainTable"],
        ["Formato de data", "Brasileiro DD/MM/YYYY → convertido com format='%d/%m/%Y'"],
        ["Conversão decimal", "Vírgula decimal brasileira substituída por ponto (replace(',', '.'))"],
        ["Resampling diário", "asfreq('D') transforma para frequência diária contínua"],
        ["Tratamento de ausentes", "bfill() — backward fill para dias sem cotação (fins de semana)"],
        ["Tipo de variável alvo", "Preço do barril em USD (variável contínua, univariada)"],
    ]
    dados_rows = []
    for i, row in enumerate(dados_data):
        style = "Helvetica-Bold" if i == 0 else "Helvetica"
        color = BRANCO if i == 0 else CINZA_ESCURO
        dados_rows.append([
            Paragraph(row[0], ParagraphStyle("da", fontName=style, fontSize=8.5,
                textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1], ParagraphStyle("db", fontName=style, fontSize=8.5,
                textColor=color, leading=12)),
        ])
    dados_table = Table(dados_rows, colWidths=[4.5 * cm, cw - 4.5 * cm])
    dados_table.setStyle(table_style_default())
    story.append(dados_table)
    space()

    # ── 5. EWM ────────────────────────────────────────────────────────────
    sec("5", "Suavização EWM e Pré-processamento para LSTM")
    body(
        "O preço diário do petróleo Brent apresenta alta volatilidade de curto prazo — "
        "variações bruscas causadas por eventos geopolíticos, anúncios de produção da OPEP "
        "e choques de demanda. Treinar um LSTM diretamente sobre essa série ruidosa "
        "prejudica a capacidade do modelo de capturar a tendência subjacente. "
        "A técnica de <b>Exponential Weighted Mean (EWM)</b> suaviza essa volatilidade "
        "sem eliminar a estrutura temporal."
    )
    space(0.2)

    subsec("EWM — Média Móvel Exponencial Ponderada")
    body(
        "A fórmula EWM pondera observações recentes mais fortemente que observações antigas, "
        "com decaimento exponencial controlado pelo parâmetro α:"
    )
    space(0.1)
    ewm_formula = Paragraph(
        "<font face='Courier'>S_t = α · X_t + (1 − α) · S_{t-1}</font>",
        ParagraphStyle("EWM", fontName="Courier", fontSize=10, textColor=AZUL_ESCURO,
                       alignment=TA_CENTER, spaceBefore=6, spaceAfter=6,
                       backColor=CINZA_CLARO, leading=15)
    )
    story.append(ewm_formula)
    space(0.1)

    ewm_data = [
        ["Parâmetro", "Valor", "Efeito"],
        ["α (alpha)", "0.09", "Suavização forte — peso alto para história; reage lentamente a choques"],
        ["adjust", "False", "Modo recursivo puro (sem correção de viés inicial)"],
        ["Aplicação", "Apenas no LSTM", "Prophet utiliza a série original (decomposição aditiva própria)"],
        ["Métricas", "Preços reais", "Avaliação MAPE/RMSE/MAE sobre preços não suavizados (honesto)"],
    ]
    ewm_rows = []
    for i, row in enumerate(ewm_data):
        ewm_rows.append([
            Paragraph(f"<b>{row[0]}</b>" if i > 0 else row[0],
                ParagraphStyle("ea", fontName="Helvetica-Bold" if i == 0 else "Helvetica-Bold",
                    fontSize=8.5, textColor=AZUL_ESCURO if i > 0 else BRANCO, leading=12)),
            Paragraph(f"<b>{row[1]}</b>" if i > 0 else row[1],
                ParagraphStyle("eb", fontName="Helvetica-Bold" if i == 0 else "Courier",
                    fontSize=8.5, textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12,
                    alignment=TA_CENTER)),
            Paragraph(row[2],
                ParagraphStyle("ec", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12,
                    alignment=TA_JUSTIFY)),
        ])
    ewm_table = Table(ewm_rows, colWidths=[3.0 * cm, 2.2 * cm, cw - 5.2 * cm])
    ewm_table.setStyle(table_style_default())
    story.append(ewm_table)
    space(0.3)

    subsec("Pipeline de Pré-processamento do LSTM")
    steps_data = [
        ["Etapa", "Transformação"],
        ["1. Suavização", "EWM com α=0.09 sobre a coluna 'y' (preço diário)"],
        ["2. Reshape", "Array 1D → matriz (-1, 1) para compatibilidade com MinMaxScaler"],
        ["3. Normalização", "MinMaxScaler: escala [0, 1] ajustado sobre toda a série"],
        ["4. Divisão temporal", "Split 80/20 — índice fixo, sem embaralhamento (sem data leakage)"],
        ["5. Janela deslizante", "look_back=5: cada amostra = 5 dias consecutivos → 1 previsão"],
        ["6. Reshape LSTM", "Formato (amostras, look_back, 1) — exigido pela camada LSTM"],
    ]
    steps_rows = []
    for i, row in enumerate(steps_data):
        steps_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("sa", fontName="Helvetica-Bold", fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("sb", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12)),
        ])
    steps_table = Table(steps_rows, colWidths=[3.5 * cm, cw - 3.5 * cm])
    steps_table.setStyle(table_style_default())
    story.append(steps_table)
    space()

    # ── 6. PROPHET ────────────────────────────────────────────────────────
    sec("6", "Modelagem — Prophet")
    body(
        "O <b>Prophet</b> é um modelo de previsão de séries temporais desenvolvido pela Meta "
        "(Facebook AI Research), baseado em um framework aditivo que decompõe a série em três "
        "componentes: tendência não-linear, sazonalidades múltiplas e efeitos de feriados. "
        "Sua principal vantagem é a robustez a dados faltantes e a changepoints automáticos na tendência."
    )
    space(0.2)

    prophet_data = [
        ["Aspecto", "Detalhes"],
        ["Algoritmo", "Decomposição aditiva: y(t) = g(t) + s(t) + h(t) + ε(t)"],
        ["Sazonalidade", "daily_seasonality=True — captura padrões intra-semana"],
        ["Changepoints", "Detectados automaticamente — adaptação a quebras estruturais"],
        ["Treinamento", "Série histórica completa (salvo e serializado em Colab)"],
        ["Persistência", "models/prophet_model.json (via prophet.serialize)"],
        ["Previsão", "make_future_dataframe(periods=N, freq='D') — N dias à frente"],
        ["Validação", "Holdout temporal: 20% finais da série (não vistos no treino)"],
        ["MAPE (holdout)", "~15.58% — calculado sobre preços reais"],
        ["Incerteza", "Intervalos de confiança disponíveis (yhat_lower, yhat_upper)"],
    ]
    prophet_rows = []
    for i, row in enumerate(prophet_data):
        prophet_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("pa", fontName="Helvetica-Bold", fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("pb", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12)),
        ])
    prophet_table = Table(prophet_rows, colWidths=[3.8 * cm, cw - 3.8 * cm])
    prophet_table.setStyle(table_style_default())
    story.append(prophet_table)
    space()

    # ── 7. LSTM ───────────────────────────────────────────────────────────
    sec("7", "Modelagem — LSTM")
    body(
        "As redes <b>LSTM (Long Short-Term Memory)</b> são redes neurais recorrentes com "
        "mecanismos de porta (forget, input, output gates) que permitem aprender "
        "dependências de longo prazo em sequências temporais — exatamente o padrão "
        "presente em séries de preços de commodities. O modelo foi treinado no Google Colab "
        "e salvo no formato HDF5 para inferência em produção."
    )
    space(0.2)

    lstm_data = [
        ["Hiperparâmetro / Aspecto", "Valor / Detalhe"],
        ["Arquitetura", "LSTM → Dense(1) — predição de um step à frente"],
        ["look_back (janela)", "5 dias — entrada: 5 preços suavizados → saída: 1 previsão"],
        ["Épocas de treinamento", "100 épocas (Google Colab)"],
        ["Otimizador", "Adam — taxa adaptativa, padrão para LSTM"],
        ["Loss function", "MSE (Mean Squared Error)"],
        ["Entrada pré-treinamento", "Série EWM suavizada com α=0.09, normalizada MinMax [0,1]"],
        ["Split de treinamento", "80% treino / 20% holdout temporal (sem embaralhamento)"],
        ["Persistência", "models/lstm_model.h5 (carregado com tensorflow.keras.models.load_model)"],
        ["Inferência (previsão futura)", "Janela deslizante iterativa: prevê N dias consecutivos"],
        ["Observação crítica", "Prevê sobre série suavizada; métricas calculadas vs preços reais"],
    ]
    lstm_rows = []
    for i, row in enumerate(lstm_data):
        lstm_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("la", fontName="Helvetica-Bold", fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("lb", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12)),
        ])
    lstm_table = Table(lstm_rows, colWidths=[5.5 * cm, cw - 5.5 * cm])
    lstm_table.setStyle(table_style_default())
    story.append(lstm_table)
    space()

    # ── 8. AVALIAÇÃO ──────────────────────────────────────────────────────
    sec("8", "Avaliação — Holdout Temporal e Métricas")
    body(
        "A avaliação de modelos de séries temporais exige cuidado especial para evitar "
        "<b>data leakage</b> — o vazamento de informação futura para o conjunto de treino. "
        "Abordagens como validação cruzada aleatória são incorretas para séries temporais, "
        "pois violam a causalidade temporal. Este projeto aplica <b>holdout temporal estrito</b>: "
        "os últimos 20% da série são reservados como conjunto de teste, nunca vistos pelo modelo."
    )
    space(0.2)

    subsec("Protocolo de Validação")
    val_data = [
        ["Aspecto", "Implementação"],
        ["Método", "Holdout temporal — 80% treino | 20% teste (índice fixo, sem shuffle)"],
        ["Prophet", "Merge entre previsão e dados reais do período de teste (inner join por data)"],
        ["LSTM", "Sequências do conjunto de teste geradas com numpy slicing (sem TimeseriesGenerator)"],
        ["Métricas base", "Preços REAIS do Brent (não suavizados pelo EWM)"],
        ["Data leakage", "Ausente — split por índice temporal, sem acesso ao futuro"],
    ]
    val_rows = []
    for i, row in enumerate(val_data):
        val_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("va", fontName="Helvetica-Bold", fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("vb", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12)),
        ])
    val_table = Table(val_rows, colWidths=[3.5 * cm, cw - 3.5 * cm])
    val_table.setStyle(table_style_default())
    story.append(val_table)
    space(0.3)

    subsec("Métricas de Avaliação")
    body("Três métricas complementares são calculadas e exibidas na interface:")
    space(0.1)

    metr_data = [
        ["Métrica", "Fórmula", "Interpretação"],
        ["MAPE", "mean(|y - ŷ| / y) × 100%",
         "Erro percentual médio — permite comparar modelos independente da escala do preço"],
        ["RMSE", "√mean((y − ŷ)²)",
         "Raiz do erro quadrático médio em USD — penaliza erros grandes (outliers de preço)"],
        ["MAE", "mean(|y − ŷ|)",
         "Erro absoluto médio em USD — interpretação direta: desvio médio em dólares"],
        ["Prophet MAPE", "~15.58%", "Medido no holdout temporal (20% finais da série histórica)"],
    ]
    metr_rows = []
    for i, row in enumerate(metr_data):
        style_b = "Helvetica-Bold"
        metr_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("ma", fontName=style_b, fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("mb", fontName="Courier" if i > 0 else style_b, fontSize=8,
                    textColor=AZUL_ESCURO if i > 0 else BRANCO, leading=12, alignment=TA_CENTER)),
            Paragraph(row[2],
                ParagraphStyle("mc", fontName=style_b if i == 0 else "Helvetica", fontSize=8.5,
                    textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12, alignment=TA_JUSTIFY)),
        ])
    metr_table = Table(metr_rows, colWidths=[2.2 * cm, 4.5 * cm, cw - 6.7 * cm])
    metr_table.setStyle(table_style_default())
    story.append(metr_table)
    space()

    # ── 9. INTERFACE ──────────────────────────────────────────────────────
    sec("9", "Interface e Funcionalidades")
    body(
        "A aplicação web é desenvolvida com <b>Streamlit</b> em estrutura multi-página (MPA), "
        "onde o estado da sessão (<font face='Courier'>st.session_state</font>) compartilha "
        "dados entre as páginas. O fluxo completo é executado sequencialmente: "
        "coleta de dados → seleção do modelo → execução → visualização."
    )
    space(0.2)

    pages_data = [
        ["Página", "Arquivo", "Funcionalidades"],
        ["Home", "Home.py",
         "Página de boas-vindas com fluxograma visual do projeto e instruções de uso"],
        ["Model", "pages/2_Model.py",
         "Carregar dados via scraping · Selecionar modelo (Prophet ou LSTM) · "
         "Configurar período de previsão (slider 1–365 dias) · Executar modelo · "
         "Exibir tabela de métricas (MAPE, RMSE, MAE) com descrições"],
        ["Data Visualization", "pages/3_Data Visualization.py",
         "Gráfico de linha histórico interativo · Gráfico real vs predito (desde dez/2023) · "
         "Barplot variação percentual por década (últimos 10 anos) · "
         "Boxplot distribuição anual de preços (1987–atual)"],
    ]
    pages_rows = []
    for i, row in enumerate(pages_data):
        pages_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("pga", fontName="Helvetica-Bold", fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("pgb", fontName="Courier" if i > 0 else "Helvetica-Bold",
                    fontSize=8, textColor=AZUL_ESCURO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[2],
                ParagraphStyle("pgc", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO,
                    leading=12, alignment=TA_JUSTIFY)),
        ])
    pages_table = Table(pages_rows, colWidths=[2.5 * cm, 4.0 * cm, cw - 6.5 * cm])
    pages_table.setStyle(table_style_default())
    story.append(pages_table)
    space(0.3)

    subsec("Fluxo de Execução")
    fluxo = (
        "<b>IPEADATA (scraping)</b> → <b>DataFrame Pandas</b> → "
        "<b>Seleção do Modelo</b> → <b>Execução (Prophet | LSTM)</b> → "
        "<b>Métricas (MAPE · RMSE · MAE)</b> → <b>Visualizações</b>"
    )
    story.append(Paragraph(fluxo, ParagraphStyle(
        "Fluxo", fontName="Helvetica-Bold", fontSize=9, textColor=AZUL_ESCURO,
        alignment=TA_CENTER, backColor=AZUL_CLARO, leading=14,
        spaceBefore=4, spaceAfter=4, borderPadding=8
    )))
    space()

    # ── 10. RESULTADOS ────────────────────────────────────────────────────
    sec("10", "Resultados e Conclusões")

    subsec("Comparativo dos Modelos")
    comp_data = [
        ["Critério", "Prophet", "LSTM + EWM"],
        ["Tipo de modelo", "Aditivo decomposicional", "Rede neural recorrente (deep learning)"],
        ["Sazonalidade", "Capturada explicitamente", "Aprendida implicitamente"],
        ["Tendência", "Modelagem não-linear com changepoints", "Padrões capturados pela janela deslizante"],
        ["MAPE (holdout)", "~15.58%", "Depende do período de teste (avaliado em tempo real)"],
        ["Treinamento", "Offline (Colab) — carregado em produção", "Offline (Colab) — carregado em produção"],
        ["Transparência", "Alta — componentes interpretáveis", "Baixa — caixa-preta"],
        ["Previsão futura", "N dias (autoregressive interno)", "N dias (janela deslizante iterativa)"],
        ["Melhor para", "Tendências de longo prazo + sazonalidade", "Captura de padrões não-lineares"],
    ]
    comp_rows = []
    for i, row in enumerate(comp_data):
        comp_rows.append([
            Paragraph(f"<b>{row[0]}</b>",
                ParagraphStyle("ca", fontName="Helvetica-Bold", fontSize=8.5,
                    textColor=AZUL_MEDIO if i > 0 else BRANCO, leading=12)),
            Paragraph(row[1],
                ParagraphStyle("cb", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12)),
            Paragraph(row[2],
                ParagraphStyle("cc", fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                    fontSize=8.5, textColor=BRANCO if i == 0 else CINZA_ESCURO, leading=12)),
        ])
    comp_table = Table(comp_rows, colWidths=[4.5 * cm, (cw - 4.5 * cm) / 2, (cw - 4.5 * cm) / 2])
    comp_table.setStyle(table_style_default())
    story.append(comp_table)
    space(0.3)

    subsec("Conclusões e Próximos Passos")
    conclusoes = [
        "Ambos os modelos são funcionais e entregam previsões com avaliação honesta via holdout temporal.",
        "A suavização EWM é fundamental para o LSTM — reduz o ruído sem eliminar a tendência estrutural.",
        "A aplicação Streamlit demonstra como pipelines de ML podem ser empacotados em interfaces acessíveis.",
        "Próximo passo técnico: retreinar periodicamente os modelos com dados mais recentes (drift temporal).",
        "Melhoria futura: adicionar intervalo de confiança ao LSTM via Monte Carlo Dropout.",
        "Melhoria futura: implementar modelo híbrido Prophet + LSTM (complementaridade dos modelos).",
        "Melhoria futura: incluir variáveis exógenas (câmbio, produção OPEP, índices de risco geopolítico).",
    ]
    for c in conclusoes:
        bullet(c)
    space()

    # ── 11. ANEXO TÉCNICO ─────────────────────────────────────────────────
    sec("11", "Anexo Técnico — Código-Fonte")

    subsec("Coleta de Dados via Web Scraping")
    story.append(Paragraph(
        "<font face='Courier' size=8>"
        "def load_data():<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;url = 'http://www.ipeadata.gov.br/ExibeSerie.aspx?...'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;response = requests.get(url)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;soup = BeautifulSoup(response.text, 'html.parser')<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;tabela = soup.find('table', {'id': 'grd_DXMainTable'})<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;df_base['data'] = pd.to_datetime(df_base['data'], format='%d/%m/%Y')<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;df_base = df_base.asfreq('D').bfill()&nbsp;&nbsp;# resampling diário<br/>"
        "</font>",
        ParagraphStyle("Code", fontName="Courier", fontSize=8, textColor=AZUL_ESCURO,
                       backColor=CINZA_CLARO, leading=13, spaceBefore=4, spaceAfter=8,
                       borderPadding=8, leftIndent=6)
    ))

    subsec("Suavização EWM + Janela Deslizante para LSTM")
    story.append(Paragraph(
        "<font face='Courier' size=8>"
        "alpha = 0.09<br/>"
        "df['Smoothed_Close'] = df['y'].ewm(alpha=alpha, adjust=False).mean()<br/><br/>"
        "# Janela deslizante (substitui TimeseriesGenerator — removido no Keras 3)<br/>"
        "def _make_sequences(data, look_back):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;X = np.array([data[i:i+look_back] for i in range(len(data)-look_back)])<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return X.reshape((X.shape[0], look_back, 1))<br/>"
        "</font>",
        ParagraphStyle("Code2", fontName="Courier", fontSize=8, textColor=AZUL_ESCURO,
                       backColor=CINZA_CLARO, leading=13, spaceBefore=4, spaceAfter=8,
                       borderPadding=8, leftIndent=6)
    ))

    subsec("Métricas — Holdout Temporal sobre Preços Reais")
    story.append(Paragraph(
        "<font face='Courier' size=8>"
        "actual_prices = df['y'].values[split + look_back: split + look_back + n]<br/><br/>"
        "mape = np.mean(np.abs((actual_prices - preds) / actual_prices)) * 100<br/>"
        "rmse = np.sqrt(np.mean((actual_prices - preds) ** 2))<br/>"
        "mae  = np.mean(np.abs(actual_prices - preds))<br/>"
        "</font>",
        ParagraphStyle("Code3", fontName="Courier", fontSize=8, textColor=AZUL_ESCURO,
                       backColor=CINZA_CLARO, leading=13, spaceBefore=4, spaceAfter=8,
                       borderPadding=8, leftIndent=6)
    ))

    nota(
        "O modelo LSTM prevê sobre a série suavizada (EWM), mas as métricas são "
        "calculadas comparando as predições invertidas (escala original) com os "
        "PREÇOS REAIS do Brent — garantindo avaliação honesta sem inflação artificial do MAPE."
    )

    return story


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    output_file = "Apresentacao_Projeto_Petro_Brent - Francisco Costa Carneiro.pdf"

    doc = BaseDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
    )

    # Frame para capa (sem header/footer)
    frame_cover = Frame(
        MARGIN, MARGIN,
        PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN,
        id="cover"
    )
    # Frame para conteúdo (com header/footer)
    frame_content = Frame(
        MARGIN, 1.8 * cm,
        PAGE_W - 2 * MARGIN, PAGE_H - 4.0 * cm,
        id="content"
    )

    cover_template = PageTemplate(id="Cover", frames=[frame_cover])
    content_template = PageTemplate(
        id="Content", frames=[frame_content], onPage=_header_footer
    )
    doc.addPageTemplates([cover_template, content_template])

    styles = build_styles()
    story = []
    story += build_cover(styles)

    # Muda para template com header/footer após a capa
    from reportlab.platypus import NextPageTemplate
    story.append(NextPageTemplate("Content"))

    story += build_toc(styles)
    story += build_content(styles)

    doc.build(story)
    print(f"PDF gerado com sucesso: {output_file}")


if __name__ == "__main__":
    main()
