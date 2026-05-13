#Importação das bibliotecas
import streamlit as st 
import pandas as pd
from sklearn.model_selection import train_test_split
from utils import DropFeatures, OneHotEncodingNames, OrdinalFeature, MinMaxWithFeatNames
from sklearn.pipeline import Pipeline
import joblib
from joblib import load

# URL da imagem
url = "https://www.cora.com.br/blog/wp-content/uploads/elementor/thumbs/emprestimo_com_garantia_de_veiculo-py61qnprw8q3sxgh445cnoctoswl9vyy0vu26a21kw.jpg.webp"

# Exibir a imagem
st.image(url, use_container_width=True)

#carregando os dados 
dados = pd.read_csv('https://raw.githubusercontent.com/alura-tech/alura-tech-pos-data-science-credit-scoring-streamlit/main/df_clean.csv')


############################# Streamlit ############################
st.markdown('<style>div[role="listbox"] ul{background-color: #6e42ad}; </style>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; '> Formulário para Solicitação de Cartão de Crédito 🤑</h1>", unsafe_allow_html = True)

st.warning('Preencha o formulário com todos os seus dados pessoais e clique no botão **ENVIAR** no final da página.')

# Idade
st.write('### Idade')
input_idade = float(st.slider('Selecione a sua idade', 18, 100))

# Grau de escolaridade
st.write('### Nível de escolaridade')
input_grau_escolaridade = st.selectbox('Qual o Grau de Escolaridade ?', dados['Grau_escolaridade'].unique())

# Estado civil
st.write('### Estado civil')
input_estado_civil = st.selectbox('Qual é o seu estado civil ?', dados['Estado_civil'].unique())

# Número de membros da família
st.write('### Família')
membros_familia = float(st.slider('Selecione quantos membros tem na sua família', 1, 20))

# Carro próprio
st.write('### Carro próprio')
input_carro_proprio = st.radio('Você possui um automóvel?',['Sim','Não'], index=0)
input_carro_proprio_dict = {'Sim': 1, 'Não':0}
input_carro_proprio = input_carro_proprio_dict.get(input_carro_proprio)

# Casa própria
st.write('### Casa própria')
input_casa_propria = st.radio('Você possui uma propriedade?',['Sim','Não'], index=0)
input_casa_propria_dict = {'Sim': 1, 'Não':0}
input_casa_propria = input_casa_propria_dict.get(input_casa_propria)

# Moradia
st.write('### Tipo de residência')
input_tipo_moradia = st.selectbox('Qual é o seu tipo de moradia ?', dados['Moradia'].unique())

# Situação de emprego
st.write('### Categoria de renda')
input_categoria_renda = st.selectbox('Qual é a sua categoria de renda ?', dados['Categoria_de_renda'].unique())

# Ocupação
st.write('### Ocupação')
input_ocupacao = st.selectbox('Qual é a sua ocupação ?', dados['Ocupacao'].unique())

# Tempo de experiência
st.write('### Experiência')
input_tempo_experiencia = float(st.slider('Selecione o seu tempo de experiência em anos', 0,30))

# Rendimentos
st.write('### Rendimentos')
input_rendimentos = float(st.text_input('Digite o seu rendimento anual (em reais) e pressione ENTER para confirmar',0))

# Telefone trabalho
st.write('### Telefone corporativo')
input_telefone_trabalho = st.radio('Você tem um telefone corporativo?',['Sim','Não'], index=0)
telefone_trabalho_dict = {'Sim': 1, 'Não':0}
telefone_trabalho = telefone_trabalho_dict.get(input_telefone_trabalho)

# Telefone fixo
st.write('### Telefone fixo')
input_telefone = st.radio('Você tem um telefone fixo?',['Sim','Não'], index=0)
telefone_dict = {'Sim': 1, 'Não':0}
telefone = telefone_dict.get(input_telefone)

# Email 
st.write('### Email')
input_email = st.radio('Você tem um email?',['Sim','Não'], index=0)
email_dict = {'Sim': 1, 'Não':0}
email = email_dict.get(input_email)

# ─── Regras de negócio (Policy Layer) ───────────────────────────────────────
def aplicar_regras_negocio(
    rendimento, membros_familia, categoria_renda, grau_escolaridade,
    idade, anos_emprego, carro, casa, tipo_moradia
):
    """
    Regras de política de crédito baseadas em práticas do mercado financeiro.
    Retorna (aprovado: bool, motivos: list[str])
    """
    motivos = []

    RENDA_MINIMA_ANUAL    = 7_200    # R$ 600/mês — mínimo absoluto
    RENDA_PER_CAPITA_MIN  = 3_600    # R$ 300/mês por membro da família
    RENDA_ESTUDANTE_MIN   = 18_000   # R$ 1.500/mês — estudante sem fiador
    RENDA_DATASET_MIN     = 27_000   # mínimo observado nos dados de treino

    renda_per_capita = rendimento / max(membros_familia, 1)

    # Regra 1 – Renda mínima absoluta
    if rendimento < RENDA_MINIMA_ANUAL:
        motivos.append(
            f"Renda anual declarada (R$ {rendimento:,.0f}) está abaixo do mínimo exigido "
            f"de R$ {RENDA_MINIMA_ANUAL:,.0f}/ano (R$ 600/mês)."
        )

    # Regra 2 – Renda per capita familiar insuficiente
    if renda_per_capita < RENDA_PER_CAPITA_MIN:
        motivos.append(
            f"Renda per capita familiar de R$ {renda_per_capita:,.0f}/ano/pessoa é insuficiente "
            f"para cobrir os compromissos de crédito com {int(membros_familia)} dependentes."
        )

    # Regra 3 – Estudante sem renda mínima comprovada
    if categoria_renda == 'Estudante' and rendimento < RENDA_ESTUDANTE_MIN:
        motivos.append(
            "Estudantes precisam comprovar renda mínima de R$ 1.500/mês "
            "ou apresentar fiador com renda própria."
        )

    # Regra 4 – Jovem sem patrimônio, emprego recente e renda baixa
    sem_patrimonio = (carro == 0 and casa == 0)
    if idade < 21 and sem_patrimonio and anos_emprego < 1 and rendimento < RENDA_DATASET_MIN:
        motivos.append(
            "Perfil de alto risco: idade inferior a 21 anos, sem patrimônio, "
            "menos de 1 ano de experiência profissional e renda insuficiente."
        )

    # Regra 5 – Renda fora do intervalo de treinamento (predição não confiável)
    aviso_fora_distribuicao = None
    if rendimento < RENDA_DATASET_MIN and not motivos:
        aviso_fora_distribuicao = (
            f"⚠️ Renda declarada (R$ {rendimento:,.0f}) está abaixo da faixa de treinamento "
            f"do modelo (mín. R$ {RENDA_DATASET_MIN:,.0f}). A predição pode ser imprecisa."
        )

    aprovado = len(motivos) == 0
    return aprovado, motivos, aviso_fora_distribuicao
# ─────────────────────────────────────────────────────────────────────────────

# Lista de todas as variáveis: 
novo_cliente = [0, # ID_Cliente
                    input_carro_proprio, # Tem_carro
                    input_casa_propria, # Tem_Casa_Propria
                    telefone_trabalho, # Tem_telefone_trabalho
                    telefone, # Tem_telefone_fixo
                    email,  # Tem_email
                    membros_familia,  # Tamanho_Familia
                    input_rendimentos, # Rendimento_anual	
                    input_idade, # Idade
                    input_tempo_experiencia, # Anos_empregado
                    input_categoria_renda, # Categoria_de_renda
                    input_grau_escolaridade, # Grau_Escolaridade
                    input_estado_civil, # Estado_Civil	
                    input_tipo_moradia, # Moradia                                                  
                    input_ocupacao, # Ocupacao
                     0 # target (Mau)
                    ]


# Separando os dados em treino e teste
def data_split(df, test_size):
    SEED = 1561651
    treino_df, teste_df = train_test_split(df, test_size=test_size, random_state=SEED)
    return treino_df.reset_index(drop=True), teste_df.reset_index(drop=True)

treino_df, teste_df = data_split(dados, 0.2)

# Feature engineering — mesmas features criadas no retreinamento
def criar_features_derivadas(df):
    df = df.copy()
    df['Renda_per_capita']     = df['Rendimento_anual'] / df['Tamanho_familia'].clip(lower=1)
    df['Score_patrimonio']     = df['Tem_carro'] + df['Tem_casa_propria']
    df['Score_contatos']       = df['Tem_telefone_trabalho'] + df['Tem_telefone_fixo'] + df['Tem_email']
    df['Renda_por_ano_emprego']= df['Rendimento_anual'] / (df['Anos_empregado'].clip(lower=0.5))
    return df

#Criando novo cliente
cliente_predict_df = pd.DataFrame([novo_cliente], columns=teste_df.columns)

#Concatenando novo cliente ao dataframe dos dados de teste e aplicando feature engineering
teste_novo_cliente = pd.concat([teste_df, cliente_predict_df], ignore_index=True)
teste_novo_cliente = criar_features_derivadas(teste_novo_cliente)

#Pipeline
def pipeline_teste(df):
    pipeline = Pipeline([
        ('feature_dropper', DropFeatures()),
        ('OneHotEncoding', OneHotEncodingNames()),
        ('ordinal_feature', OrdinalFeature()),
        ('min_max_scaler', MinMaxWithFeatNames()),
    ])
    df_pipeline = pipeline.fit_transform(df)
    return df_pipeline

#Aplicando a pipeline
teste_novo_cliente = pipeline_teste(teste_novo_cliente)

#retirando a coluna target
cliente_pred = teste_novo_cliente.drop(['Mau'], axis=1)

# Threshold de risco (sidebar)
st.sidebar.markdown("## ⚙️ Configuração do modelo")
st.sidebar.info(
    "**Limiar de risco**: define a partir de qual probabilidade de inadimplência o crédito é negado. "
    "Valores menores = mais conservador (mais rejeições, menos risco de crédito ruim)."
)
threshold = st.sidebar.slider(
    "Limiar de risco para rejeição",
    min_value=0.05,
    max_value=0.50,
    value=0.10,
    step=0.05,
    help="Se a probabilidade de inadimplência for maior que este valor, o crédito é negado. "
         "Valores menores tornam o modelo mais conservador (mais rejeições)."
)

#Predições 
if st.button('Enviar'):
    st.markdown("---")
    st.markdown("### 📊 Resultado da Avaliação")

    # ── Camada 1: Regras de negócio (Policy Rules) ──────────────────────────
    aprovado_regras, motivos_rejeicao, aviso_dist = aplicar_regras_negocio(
        rendimento=input_rendimentos,
        membros_familia=membros_familia,
        categoria_renda=input_categoria_renda,
        grau_escolaridade=input_grau_escolaridade,
        idade=input_idade,
        anos_emprego=input_tempo_experiencia,
        carro=input_carro_proprio,
        casa=input_casa_propria,
        tipo_moradia=input_tipo_moradia,
    )

    if not aprovado_regras:
        st.error("### ❌ Crédito Negado — Política de Concessão")
        st.markdown("**Motivo(s) da rejeição:**")
        for motivo in motivos_rejeicao:
            st.markdown(f"- {motivo}")
        st.info(
            "A solicitação foi bloqueada pelas políticas de concessão de crédito antes mesmo "
            "da avaliação pelo modelo de risco. Entre em contato para orientação."
        )
    else:
        # ── Camada 2: Modelo de ML ───────────────────────────────────────────
        if aviso_dist:
            st.warning(aviso_dist)

        model = joblib.load('modelo/xgb.joblib')
        prob = model.predict_proba(cliente_pred)
        prob_mau = prob[-1][1]
        prob_bom = prob[-1][0]

        col1, col2 = st.columns(2)
        col1.metric("Risco de inadimplência", f"{prob_mau * 100:.1f}%")
        col2.metric("Perfil positivo", f"{prob_bom * 100:.1f}%")
        st.progress(float(prob_mau), text=f"Nível de risco pelo modelo: {prob_mau * 100:.1f}%")

        if prob_mau < threshold:
            st.success('### ✅ Parabéns! Você teve o cartão de crédito aprovado')
            st.balloons()
        else:
            st.error('### ❌ Infelizmente, não podemos liberar crédito para você agora!')
            st.info(
                f"Probabilidade de inadimplência estimada pelo modelo: {prob_mau * 100:.1f}% "
                f"(limiar de rejeição: {threshold * 100:.0f}%)."
            )
 
