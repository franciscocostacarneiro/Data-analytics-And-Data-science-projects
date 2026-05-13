"""
Script para retreinar o modelo GradientBoostingClassifier com as versões atuais
das bibliotecas e salvar em modelo/xgb.joblib.
"""

import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, OrdinalEncoder
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, classification_report
from imblearn.over_sampling import SMOTE
import joblib
import os

print("Carregando dados...")
df = pd.read_csv("df_clean.csv")

print(f"Shape dos dados: {df.shape}")
print(f"Distribuição do target:\n{df['Mau'].value_counts(normalize=True) * 100}\n")


# ------- Feature Engineering: variáveis mais preditivas -------
def criar_features_derivadas(df):
    """Cria features financeiras que capturam melhor o risco de crédito."""
    df = df.copy()
    # Renda per capita familiar (maior família + renda baixa = maior risco)
    df["Renda_per_capita"] = df["Rendimento_anual"] / df["Tamanho_familia"].clip(lower=1)
    # Score de patrimônio (0 = sem nada, 2 = carro + casa)
    df["Score_patrimonio"] = df["Tem_carro"] + df["Tem_casa_propria"]
    # Score de contatos verificáveis
    df["Score_contatos"] = df["Tem_telefone_trabalho"] + df["Tem_telefone_fixo"] + df["Tem_email"]
    # Renda por ano de experiência (estabilidade financeira)
    df["Renda_por_ano_emprego"] = df["Rendimento_anual"] / (df["Anos_empregado"].clip(lower=0.5))
    return df

df = criar_features_derivadas(df)

# Split treino/teste (estratificado para manter proporção de maus)
SEED = 1561651
train_df, test_df = train_test_split(df, test_size=0.2, random_state=SEED, stratify=df["Mau"])

class DropFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, feature_to_drop=["ID_Cliente"]):
        self.feature_to_drop = feature_to_drop

    def fit(self, df):
        return self

    def transform(self, df):
        if set(self.feature_to_drop).issubset(df.columns):
            df.drop(self.feature_to_drop, axis=1, inplace=True)
        return df



class OneHotEncodingNames(BaseEstimator, TransformerMixin):
    def __init__(self, OneHotEncoding=["Estado_civil", "Moradia", "Categoria_de_renda", "Ocupacao"]):
        self.OneHotEncoding = OneHotEncoding

    def fit(self, df):
        return self

    def transform(self, df):
        if set(self.OneHotEncoding).issubset(df.columns):
            enc = OneHotEncoder()
            enc.fit(df[self.OneHotEncoding])
            feature_names = enc.get_feature_names_out(self.OneHotEncoding)
            ohe_df = pd.DataFrame(
                enc.transform(df[self.OneHotEncoding]).toarray(),
                columns=feature_names,
                index=df.index,
            )
            outras = [c for c in df.columns if c not in self.OneHotEncoding]
            return pd.concat([ohe_df, df[outras]], axis=1)
        return df


class OrdinalFeature(BaseEstimator, TransformerMixin):
    def __init__(self, ordinal_feature=["Grau_escolaridade"]):
        self.ordinal_feature = ordinal_feature

    def fit(self, df):
        return self

    def transform(self, df):
        if "Grau_escolaridade" in df.columns:
            enc = OrdinalEncoder()
            df[self.ordinal_feature] = enc.fit_transform(df[self.ordinal_feature])
        return df


class MinMaxWithFeatNames(BaseEstimator, TransformerMixin):
    # Inclui as novas features derivadas no escalonamento
    def __init__(self, min_max_scaler_ft=[
        "Idade", "Rendimento_anual", "Tamanho_familia", "Anos_empregado",
        "Renda_per_capita", "Score_patrimonio", "Score_contatos", "Renda_por_ano_emprego"
    ]):
        self.min_max_scaler_ft = min_max_scaler_ft

    def fit(self, df):
        return self

    def transform(self, df):
        cols_presentes = [c for c in self.min_max_scaler_ft if c in df.columns]
        if cols_presentes:
            scaler = MinMaxScaler()
            df[cols_presentes] = scaler.fit_transform(df[cols_presentes])
        return df


class Oversample(BaseEstimator, TransformerMixin):
    def fit(self, df):
        return self

    def transform(self, df):
        if "Mau" in df.columns:
            smote = SMOTE(sampling_strategy="minority", random_state=SEED)
            X_bal, y_bal = smote.fit_resample(df.loc[:, df.columns != "Mau"], df["Mau"])
            return pd.concat([pd.DataFrame(X_bal), pd.DataFrame(y_bal)], axis=1)
        return df


# ------- Pipeline de treino (inclui SMOTE) -------
def pipeline_treino(df):
    p = Pipeline([
        ("feature_dropper", DropFeatures()),
        ("OneHotEncoding", OneHotEncodingNames()),
        ("ordinal_feature", OrdinalFeature()),
        ("min_max_scaler", MinMaxWithFeatNames()),
        ("oversample", Oversample()),
    ])
    return p.fit_transform(df)


def pipeline_teste(df):
    """Pipeline sem SMOTE para avaliação no conjunto de teste."""
    p = Pipeline([
        ("feature_dropper", DropFeatures()),
        ("OneHotEncoding", OneHotEncodingNames()),
        ("ordinal_feature", OrdinalFeature()),
        ("min_max_scaler", MinMaxWithFeatNames()),
    ])
    return p.fit_transform(df)


print("Aplicando pipeline de treino...")
train = pipeline_treino(train_df.copy())

X_train = train.loc[:, train.columns != "Mau"]
y_train = train["Mau"]

print(f"Shape treino após SMOTE: {train.shape}")

# ------- Treino do modelo com hiperparâmetros otimizados -------
print("\nTreinando GradientBoostingClassifier com hiperparâmetros ajustados...")
modelo = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    min_samples_leaf=20,
    subsample=0.8,
    random_state=SEED,
)
modelo.fit(X_train, y_train)
print("Modelo treinado com sucesso!")

# ------- Avaliação no conjunto de teste -------
print("\nAvaliando no conjunto de teste...")
test = pipeline_teste(test_df.copy())
X_test = test.drop("Mau", axis=1)
y_test = test["Mau"]

probs = modelo.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, probs)
print(f"AUC no teste: {auc:.4f}")
print()

print(f"{'Threshold':>10} | {'Recall Mau':>10} | {'Maus aprovados (FN)':>22}")
print("-" * 50)
total_maus = int(y_test.sum())
for thresh in [0.10, 0.15, 0.20, 0.25, 0.30]:
    preds = (probs >= thresh).astype(int)
    from sklearn.metrics import recall_score
    recall = recall_score(y_test, preds, zero_division=0)
    fn = total_maus - int(recall * total_maus)
    print(f"{thresh:>10.2f} | {recall:>10.2f} | {fn:>22}")

# ------- Salvar modelo -------
os.makedirs("modelo", exist_ok=True)
joblib.dump(modelo, "modelo/xgb.joblib")
print("\nModelo salvo em modelo/xgb.joblib")

# ------- Verificação rápida -------
print("\nVerificando carregamento do modelo...")
modelo_carregado = joblib.load("modelo/xgb.joblib")
print(f"Tipo do modelo: {type(modelo_carregado)}")
print("Tudo OK!")
