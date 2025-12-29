import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if "processed_df" not in st.session_state:
    st.session_state.processed_df = False

if not isinstance(st.session_state.processed_df, pd.DataFrame):
    st.error('Dados não carregados, execute o modulo "Model" por completo antes de carregar os graficos.')
    st.stop()

processed_df = st.session_state.processed_df

# Definir estilo do Seaborn
sns.set(style="whitegrid", rc={"axes.facecolor": "#0d1116", "figure.facecolor":"#0d1116","grid.color": "#4F4F4F"})

def click_button():
    st.session_state.clicked = True

def generate_plot_variacao(df):

    df_variacao = df[df['tipo_dado'] == 'Dado Real']

    df_variacao['ano'] = df_variacao['data'].dt.year
    df_variacao = df_variacao.groupby('ano')['valor'].mean().reset_index()

    ultimos_anos = df_variacao['ano'].max() - 9  # Para obter os últimos 10 anos

    # Filtrando o DataFrame para incluir apenas os últimos 10 anos
    df_variacao = df_variacao[df_variacao['ano'] >= ultimos_anos]

    # Calcular a diferença percentual em relação ao ano anterior
    df_variacao['Variacao_Percentual'] = ((df_variacao['valor'].shift(1) - df_variacao['valor']) / (
        df_variacao['valor']) * -1) * 100

    # Criar o gráfico de barras usando Seaborn
    plt.figure(figsize=(10, 6))
    barplot = sns.barplot(x='ano', y='valor', data=df_variacao, color='#3071f2')

    bbox_props = dict(boxstyle="round,pad=0.1", fc="#0d1116", ec="#0d1116", lw=1)

    # Adicionar rótulos de porcentagem de variação
    for index, value in enumerate(df_variacao['Variacao_Percentual'], start=0):
        color = '#F24F30' if value < 0 else '#B3F230'
        if (index > 0):
            barplot.text(index, df_variacao['valor'].iloc[index] + 6, f'{value:.2f}%', ha='center', va='bottom',
                         color=color, bbox=bbox_props)

        barplot.text(index, df_variacao['valor'].iloc[index] + 1, f'{df_variacao["valor"].iloc[index]:.2f}',
                     ha='center', va='bottom', color='white', fontsize=12, bbox=bbox_props)

    # Adicionar rótulos e título

    barplot.set(ylim=(0, df_variacao['valor'].max() + 15))

    plt.title('Variação Percentual do Preço em Relação ao Ano Anterior', color="white", fontsize=16)
    plt.xlabel('Ano', color="white", fontsize=14)
    plt.ylabel('Preço Médio (USD)', color="white", fontsize=14)
    plt.tick_params(axis='x', labelcolor='white')
    plt.tick_params(axis='y', labelcolor='white')

    # Exibir o gráfico
    st.pyplot(plt)

def generate_plot_modelo_ml(df):
    # Criando dados fictícios para o exemplo
    df_modelo = df[df['data'] >= pd.to_datetime('2023-12-01')]

    # data específica para mudar a cor
    data_limite = df_modelo[df_modelo['tipo_dado'] == 'Dado Real']['data'].max()

    # Criar o gráfico de linha usando Seaborn
    plt.figure(figsize=(10, 6))

    # Linha antes da data limite
    sns.lineplot(x='data', y='valor', data=df_modelo[df_modelo['data'] <= data_limite], color='#3071f2',
                 label='Valor Real')

    # Linha após a data limite
    sns.lineplot(x='data', y='valor', data=df_modelo[df_modelo['data'] >= data_limite], color='#f2a20c',
                 label='Valor Predito')

    # Conectar visualmente as duas partes
    plt.axvline(x=data_limite, color='gray', linestyle='--', linewidth=2,
                label='Data de Transição: {}'.format(data_limite.strftime('%d-%m-%Y')))

    # Adicionar rótulos e título
    plt.title('Visualização Dados Reais x Dados Preditos', color="white", fontsize=16)
    plt.xlabel('Data', color="white", fontsize=14)
    plt.ylabel('Preço (USD)', color="white", fontsize=14)
    plt.tick_params(axis='x', labelcolor='white')
    plt.tick_params(axis='y', labelcolor='white')
    plt.xticks(rotation=45)

    # Adicionar legenda
    legend = plt.legend()
    legend.get_frame().set_facecolor('#32363e')

    for texto in legend.get_texts():
        texto.set_color('white')

    # Exibindo os gráficos
    st.pyplot(plt)

def generate_plot_boxplot(df):
    df_boxplot = df[df['tipo_dado'] == 'Dado Real']
    df_boxplot['ano'] = df_boxplot['data'].dt.year

    plt.figure(figsize=(10, 6))

    sns.boxplot(data=df_boxplot, x='ano', y='valor', color='#3071f2', linecolor="white")

    plt.title("Distribuição de preços do barril de petróleo por ano (1986-Atual)", color="white", fontsize=16)
    plt.xlabel("Ano", color="white", fontsize=14)
    plt.ylabel("Preço (USD)", color="white", fontsize=14)
    plt.xticks(rotation=90)
    plt.tick_params(axis='x', labelcolor='white')
    plt.tick_params(axis='y', labelcolor='white')

    st.pyplot(plt)

def generate_plot_interativo(df, agrupamento, range_ano):

    df_generico = df[df['tipo_dado'] == 'Dado Real']

    df_generico = df_generico[(df_generico['data'].dt.year >= range_ano[0]) & (df_generico['data'].dt.year <= range_ano[1])]

    # Agrupando os dados conforme especificado
    if agrupamento == 'Diario':
        df_generico2 = df_generico.groupby(df_generico['data'].dt.date)['valor'].mean().reset_index()
        xlabel = 'Data (Dia)'
    elif agrupamento == 'Mensal':
        df_generico = df_generico.groupby(df_generico['data'].dt.to_period("M"))['valor'].mean().reset_index()
        df_generico['data'] = df_generico['data'].dt.to_timestamp()
        xlabel = 'Data (Mês)'
    elif agrupamento == 'Anual':
        df_generico = df_generico.groupby(df_generico['data'].dt.to_period("Y"))['valor'].mean().reset_index()
        df_generico['data'] = df_generico['data'].dt.to_timestamp()
        xlabel = 'Data (Ano)'
    else:
        raise ValueError("O parâmetro 'agrupamento' deve ser 'dia', 'mes' ou 'ano'.")

    # Plotando o gráfico de linhas usando Seaborn
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='data', y='valor', data=df_generico, marker='o')
    # plt.title(f'Gráfico de Linhas', color="white", fontsize=16)
    plt.xlabel(xlabel, color="white", fontsize=14)
    plt.ylabel('Preço (USD)', color="white", fontsize=14)
    plt.tick_params(axis='x', labelcolor='white')
    plt.tick_params(axis='y', labelcolor='white')
    plt.grid(True)
    st.pyplot(plt)

#Inicio da construção da pagina
col1, col2 = st.columns([4,1])

with col1:
    st.markdown("""
    ## Data Visualization
    """)

with col2:
    st.text("")
    st.button('Exibir Graficos', on_click=click_button)

if st.session_state.clicked:

    st.header("Grafico 1")
    st.subheader("Lineplot: Grafico interativo")

    with st.form("form_parametros"):
        coluna1, coluna2, coluna3, coluna4=st.columns(4)
        with coluna1:
            abertura = st.selectbox("Abertura:", ["Anual", "Mensal", "Diario"])
        with coluna4:
            range_ano = st.slider(
                "Range de ano",
                value=(1987, 2024),
                min_value=(1987),
                max_value=(2024)
            )
        st.form_submit_button("Aplicar")

    generate_plot_interativo(processed_df, abertura, range_ano)
    st.markdown("""
    O gráfico interativo que apresenta o preço do barril de petróleo desde 1987 
    até os dias atuais oferecendo uma valiosa ferramenta para compreender a dinâmica volátil desse mercado crucial. 
    Ao permitir a visualização das variações de preços em aberturas diárias, mensais ou anuais, 
    esse recurso proporciona insights valiosos sobre os eventos que moldaram a economia global ao longo das décadas.
    
    #### Insights Sugeridos: 
    ##### 2007-2009
    
    Um execelente periodo para analise é o periodo entre 2007-2009, onde a demanda por petroleo subiu por diversos fatores, 
    dentre eles os principais foram:
    - O equilíbrio tenso entre uma oferta limitada e uma demanda puxada pelos países emergentes;
    - A conscientização de que as reservas são limitadas e de acesso cada vez mais difícil;
    - Questoes socioeconomicas que geraram uma febre dos fundos de investimento por matérias-primas.
     
    Esse aumento desenfreado na demanda por petroleo gerou uma bolha que inflou os preços quase que exponencialmente, porém
    ao mesmo tempo se iniciou a crise financeira nos Estados Unidos e com a quebra do banco Lehman Brothers em setembro, 
    esta lógica se inverte. 
    
    Temendo a deflação, os investidores abandonam o petróleo, porque precisam urgentemente de liquidez.
    Também ao mesmo tempo, o petróleo caro derruba o consumo de combustível dos países industrializados, causando assim 
    uma queda tao brusca quando a subida dos preços.
    
    ##### 2019-2023
    
    Outro periodo extremamente relevante para analise, é o periodo de 2019 a 2023, em que conseguimos identificar o 
    impacto da crise sanitária de Covid19. 
    
    Inicialmente, as medidas de lockdown global resultaram em uma queda abrupta na demanda por energia, levando a um 
    excesso de oferta no mercado. A disputa de preços entre a Arábia Saudita e a Rússia, que se desenrolou simultaneamente, 
    exacerbou a situação, desencadeando uma guerra de preços e inundando o mercado com barris adicionais. Essa combinação 
    de eventos resultou em uma queda sem precedentes nos preços do petróleo, impactando negativamente os produtores e 
    evidenciando a extrema sensibilidade do setor a choques econômicos e geopolíticos.
    
    Após os lockdowns associados à pandemia de COVID-19, o mercado de petróleo experimentou uma notável recuperação nos 
    preços. Com a retomada gradual das atividades econômicas, o aumento da mobilidade global e os esforços de vacinação 
    em massa, a demanda por energia voltou a ser presente, porém como o mercado ainda estava instavel devido ao contexto 
    global, essa alta na demanda impactou negativamente nos preços, disparando os valores para patamares muito além do 
    que era visto antes da crise sanitária.
    
    Apenas após alguns meses a retomada das atividades, mesmo em alta, o preço passou a se estabilizar.
    """)

    st.header("Grafico 2")
    st.subheader("Lineplot: Predição de Preços dos Barris de Petróleo")
    generate_plot_modelo_ml(processed_df)
    st.markdown(
        """
        O gráfico apresenta uma análise abrangente dos preços do petróleo, combinando dados reais e previsões. 
        
        Utilizando um modelo de séries temporais, seja LSTM ou Prophet, esta visualização oferece uma visão dinâmica das 
        tendências passadas e futuras, permitindo uma melhor 
        compreensão do comportamento do mercado petrolífero e potencializando estratégias de tomada de decisão.
        """
    )

    st.header("Grafico 3")
    st.subheader("Barplot: Variação ultima decada")
    generate_plot_variacao(processed_df)
    st.markdown("""
        O grafico revela uma notável flutuação nos preços do barril de petróleo ao longo dos anos, refletindo as 
        complexidades do mercado global de energia. 
        
        Em 2016, uma queda acentuada de 20.77% marcou um período desafiador, possivelmente influenciado por fatores 
        econômicos e geopolíticos. Contudo, a recuperação nos anos subsequentes, particularmente em 2017 e 2018, 
        evidencia a sensibilidade do mercado a eventos externos. O ano de 2020, marcado pela pandemia de COVID-19, 
        apresentou uma drástica queda de 53.77%, indicando o impacto direto das interrupções globais nas atividades 
        econômicas. 
        
        A rápida recuperação em 2021, com um aumento significativo de 41.13%, sugere uma resiliência 
        surpreendente do mercado, enquanto as variações em 2022 e 2023 revelam a persistência da volatilidade, 
        possivelmente associada a dinâmicas econômicas e decisões estratégicas de importantes produtores.
    """)

    st.header("Grafico 4")
    st.subheader("Boxplot: Distribuição de preços anuais")
    generate_plot_boxplot(processed_df)
    st.markdown(
        """
         Analisando os valores, observamos flutuações significativas no preço do petróleo desde 1987 até os últimos 
         registros disponíveis. 
         
         Inicialmente, os preços eram relativamente estáveis, mas houve um aumento notável na década de 1990 indicando um 
         aumento na demanda por energia possivelmente pelo aumento da industrialização, aumento populacional e 
         populirazação do consumo de combustiveis derivados do petroleo. 
         Esse crescimento ocorre até nos dias atuais e a tendencia é que continue crescendo.
         
         Também é possível notar a inconsistência nos preços em períodos de crise. Como mencionado anteriormente, 
         durante o ano de 2008, observamos a maior discrepância nos preços das últimas três décadas, acompanhada por uma 
         significativa concentração de valores atípicos nesse mesmo período. Outro exemplo notável de inconsistência 
         ocorreu durante a pandemia de 2019, evidenciando um comportamento semelhante de alta variação nos preços.        
        """
    )