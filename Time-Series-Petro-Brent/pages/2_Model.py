import json
import numpy as np
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from prophet.serialize import model_from_json
from sklearn.preprocessing import MinMaxScaler

# Tentar importar TensorFlow; se não conseguir, usar Prophet como fallback
TENSORFLOW_AVAILABLE = False
try:
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except (ImportError, OSError):
    load_model = None


def _make_sequences(data, look_back):
    """Gera sequências temporais para o LSTM (substitui TimeseriesGenerator removido no Keras 3)."""
    X = np.array([data[i:i + look_back] for i in range(len(data) - look_back)])
    return X.reshape((X.shape[0], look_back, 1))

# Checa e cria o estado da sessão se ainda não existe o dataframe "df_base".
if "df_base" not in st.session_state:
    st.session_state.df_base = False

# Checa e cria o estado da sessão se o botao "model_clicked" ainda não foi acionado.
if 'model_clicked' not in st.session_state:
    st.session_state.model_clicked = False

def click_model_button():
    st.session_state.model_clicked = True


def load_data():
    # URL do site Ipeadata
    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view"

    # Fazendo a requisição para o site
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrando os dados na página
    dados = []
    tabela = soup.find('table', {'id': 'grd_DXMainTable'})  # Identificando a tabela correta pelo ID
    if tabela:
        for linha in tabela.find_all('tr'):
            colunas = linha.find_all('td')
            if len(colunas) == 2:  # Verificando se temos exatamente 2 colunas
                data = colunas[0].text.strip()
                preco = colunas[1].text.strip().replace(',', '.')
                dados.append([data, preco])

    df_base = pd.DataFrame(dados[2:], columns=['data', 'valor'])
    df_base['data'] = pd.to_datetime(df_base['data'], format='%d/%m/%Y')
    df_base['valor'] = df_base['valor'].astype(float)
    df_base.set_index('data', inplace=True)
    df_base = df_base.asfreq('D').bfill()
    df_base = df_base.reset_index(drop=False)


    return df_base


def preparar_dataframe(df):
    # df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df = df.rename(columns={'data': 'ds', 'valor': 'y'})
    return df


def prever_lsmt(df, periodo):

    alpha = 0.09
    df['Smoothed_Close'] = df['y'].ewm(alpha=alpha, adjust=False).mean()
    df['tipo_dado'] = "Dado Real"

    close_data = df['Smoothed_Close'].values
    close_data = close_data.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler = scaler.fit(close_data)
    close_data = scaler.transform(close_data)

    close_data = close_data.reshape((-1))

    look_back = 5

    prediction_list = close_data[-look_back:]

    for _ in range(periodo):
        x = prediction_list[-look_back:]
        x = x.reshape((1, look_back, 1))
        out = model.predict(x)[0][0]
        prediction_list = np.append(prediction_list, out)
    forecast = prediction_list[look_back - 1:]

    last_date = df['ds'].values[-1]
    forecast_dates = pd.date_range(last_date, periods=periodo + 1).tolist()

    forecast = forecast.reshape(-1, 1)  # reshape para array
    forecast = scaler.inverse_transform(forecast)

    df_modelo = pd.DataFrame(columns=['ds', 'y', 'tipo_dado'])
    df_modelo['ds'] = forecast_dates[1:]
    df_modelo['y'] = forecast.flatten()[1:]
    df_modelo['tipo_dado'] = 'Dado Predito'
    df_modelo['y'] = df_modelo['y'].round(2).astype(float)

    df_final = pd.concat([df, df_modelo], ignore_index=True)

    df_final = df_final[['ds', 'y', 'tipo_dado']].rename(columns={'ds': 'data', 'y': 'valor'})

    return df_final

def validacao_lsmt(df):
    alpha = 0.09
    df = df.copy()
    df['Smoothed_Close'] = df['y'].ewm(alpha=alpha, adjust=False).mean()

    close_data = df['Smoothed_Close'].values
    close_data = close_data.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler = scaler.fit(close_data)
    close_data_scaled = scaler.transform(close_data)

    split_percent = 0.80
    split = int(split_percent * len(close_data_scaled))

    close_test = close_data_scaled[split:]
    look_back = 5  # consistente com o treinamento do modelo

    X_test = _make_sequences(close_test, look_back)
    test_predictions = model.predict(X_test)
    test_predictions_inv = scaler.inverse_transform(test_predictions.reshape(-1, 1))

    # Métricas calculadas sobre os preços REAIS (não suavizados) — holdout temporal
    n = len(test_predictions_inv)
    actual_prices = df['y'].values[split + look_back: split + look_back + n].reshape(-1, 1)

    mape = np.mean(np.abs((actual_prices - test_predictions_inv) / actual_prices)) * 100
    rmse = np.sqrt(np.mean((actual_prices - test_predictions_inv) ** 2))
    mae = np.mean(np.abs(actual_prices - test_predictions_inv))

    return mape, rmse, mae

def prever_prophet(df, periodo):
    futuro = model.make_future_dataframe(periods=periodo, freq='D')
    previsao = model.predict(futuro)
    previsao = previsao[['ds', 'yhat']]
    return previsao

def validacao_prophet(df, previsao):
    # Holdout temporal: últimos 20% dos dados como conjunto de teste (não vistos pelo modelo)
    split = int(0.80 * len(df))
    test_data = df.iloc[split:][['ds', 'y']].copy()

    resultados = pd.merge(previsao, test_data, on='ds', how='inner')

    mape = np.mean(np.abs((resultados['y'] - resultados['yhat']) / resultados['y'])) * 100
    rmse = np.sqrt(np.mean((resultados['y'] - resultados['yhat']) ** 2))
    mae = np.mean(np.abs(resultados['y'] - resultados['yhat']))

    return mape, rmse, mae

def construcao_df_prophet(df, previsao):

    df_final = pd.merge(df, previsao, on='ds', how='outer')
    df_final['tipo_dado'] = 'Dado Real'
    df_final.loc[df_final['y'].isnull(), 'tipo_dado'] = 'Dado Predito'
    df_final['y'] = df_final['y'].fillna(df_final['yhat'])
    df_final['y'] = df_final['y'].round(2).astype(float)
    df_final = df_final[['ds', 'y', 'tipo_dado']].rename(columns={'ds': 'data', 'y': 'valor'})

    return df_final


st.title("Machine Learning Models")
st.markdown("""Esta página web foi desenvolvida com o propósito de facilitar a execução de modelos de séries temporais, 
oferecendo ao usuário a opção de escolher entre os modelos Prophet ou LSTM.

A execução se da através dos seguintes passos:""")
st.caption("1. Busca dos dados;")
st.caption("2. Seleção e Configuração do modelo;")
st.caption("3. Execução do modelo;")
st.caption("4. Analise dos Dados e Metricas Retornadas.")

# st.write("### Executando o modelo:")

st.button('Carregar Dados', on_click=click_model_button)

if st.session_state.model_clicked:
    # Executando a função quando o botão é pressionado

    if not isinstance(st.session_state.df_base, pd.DataFrame):
        st.session_state.df_base = load_data()

    min_max_date = [st.session_state.df_base['data'].min().strftime('%d/%m/%Y'), st.session_state.df_base['data'].max().strftime('%d/%m/%Y')]

    # Exibindo o DataFrame retornado pela função
    st.write('Amostra dos dados retornados:')
    st.dataframe(st.session_state.df_base, width=400)
    st.caption(f"""
    Data Minima: {min_max_date[0]} \n
    Data Maxima: {min_max_date[1]}
    """)

    st.markdown("### Configurações do Modelo")

    coluna1, coluna2, coluna3 = st.columns([1,1,2])
    with coluna1:
        if TENSORFLOW_AVAILABLE:
            modelo = st.selectbox("Modelo:", ["Prophet", "LSTM"])
        else:
            modelo = st.selectbox("Modelo:", ["Prophet"])
            st.info("💡 Apenas Prophet está disponível. TensorFlow não foi instalado no ambiente de deploy.")
    with coluna3:
        periodo = st.slider('Número de Dias para Previsão', 1, 365, 30)


    if st.button("Executar Modelo"):

        if modelo == 'Prophet':

            with open('models/prophet_model.json', 'r') as path:
                model = model_from_json(json.load(path))

            st.session_state.processed_df = preparar_dataframe(st.session_state.df_base)

            previsao = prever_prophet(st.session_state.processed_df, periodo)

            mape, rmse, mae = validacao_prophet(st.session_state.processed_df, previsao)

            st.session_state.processed_df = construcao_df_prophet(st.session_state.processed_df, previsao)

        elif modelo == 'LSTM':
            
            # Tentar carregar modelo LSTM com fallback para Prophet
            if not TENSORFLOW_AVAILABLE:
                st.warning("❌ LSTM não disponível. Usando Prophet como alternativa.")
                with open('models/prophet_model.json', 'r') as path:
                    model = model_from_json(json.load(path))
                st.session_state.processed_df = preparar_dataframe(st.session_state.df_base)
                previsao = prever_prophet(st.session_state.processed_df, periodo)
                mape, rmse, mae = validacao_prophet(st.session_state.processed_df, previsao)
                st.session_state.processed_df = construcao_df_prophet(st.session_state.processed_df, previsao)
            else:
                try:
                    model = load_model('models/lstm_model.h5')
                    st.session_state.processed_df = preparar_dataframe(st.session_state.df_base)
                    mape, rmse, mae = validacao_lsmt(st.session_state.processed_df)
                    st.session_state.processed_df = prever_lsmt(st.session_state.processed_df, periodo)
                except Exception as e:
                    st.error(f"❌ Erro ao carregar LSTM: {str(e)}")
                    st.warning("Usando Prophet como alternativa...")
                    with open('models/prophet_model.json', 'r') as path:
                        model = model_from_json(json.load(path))
                    st.session_state.processed_df = preparar_dataframe(st.session_state.df_base)
                    previsao = prever_prophet(st.session_state.processed_df, periodo)
                    mape, rmse, mae = validacao_prophet(st.session_state.processed_df, previsao)
                    st.session_state.processed_df = construcao_df_prophet(st.session_state.processed_df, previsao)

        else:
            st.stop()

        st.success('Modelo aplicado com sucesso!')
        st.markdown(f"""
        #### Métricas de Avaliação — Holdout Temporal (últimos 20% dos dados)

        | Métrica | Valor | Descrição |
        |---|---|---|
        | **MAPE** | {mape:.2f}% | Erro percentual absoluto médio sobre preços reais |
        | **RMSE** | {rmse:.2f} USD | Raiz do erro quadrático médio (mesma unidade do preço) |
        | **MAE** | {mae:.2f} USD | Erro absoluto médio |

        > As métricas são calculadas comparando as previsões do modelo com os **preços reais**
        > do conjunto de teste (holdout temporal — dados não utilizados no treinamento).
        
        Para visualizar os dados retornados acesse a aba **Data Visualization**.
        """)

        st.dataframe(st.session_state.processed_df, width= 400)