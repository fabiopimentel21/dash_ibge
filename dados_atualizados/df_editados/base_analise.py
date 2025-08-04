import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Dashboard Interativo - IBGE")


# Diretório onde os arquivos atualizados serão salvos
caminho_base = "df_editados/"
arquivo_base = r"C:\Users\devma\Desktop\DEMANDAS\IBGE\dados_atualizados\df_editados\base_completa_final.xlsx"
caminho_completo = os.path.join(r'C:\Users\devma\Desktop\DEMANDAS\IBGE\dados_atualizados\df_editados\base_completa_final.xlsx')

# Verificação simples
if not os.path.exists(r'C:\Users\devma\Desktop\DEMANDAS\IBGE\dados_atualizados\df_editados\base_completa_final.xlsx'):
    st.error(f"Arquivo não encontrado: {caminho_completo}")
    st.stop()

# Carregando a base
df = pd.read_excel(r'C:\Users\devma\Desktop\DEMANDAS\IBGE\dados_atualizados\df_editados\base_completa_final.xlsx')

# -------------------------------
# Filtros no Sidebar
# -------------------------------
st.sidebar.header("Filtros de Bairros")

cd_bairro = st.sidebar.multiselect("Código do Bairro (CD_BAIRRO):", df["CD_BAIRRO"].unique())
nm_bairro = st.sidebar.multiselect("Nome do Bairro (NM_BAIRRO):", df["NM_BAIRRO"].unique())

df_filtrado = df.copy()
if cd_bairro:
    df_filtrado = df_filtrado[df_filtrado["CD_BAIRRO"].isin(cd_bairro)]
if nm_bairro:
    df_filtrado = df_filtrado[df_filtrado["NM_BAIRRO"].isin(nm_bairro)]

# -------------------------------
# Análise Numérica
# -------------------------------
st.sidebar.header("Análise Numérica")

colunas_disponiveis = df_filtrado.select_dtypes(include='number').columns.difference(['CD_BAIRRO'])
coluna = st.sidebar.selectbox("Escolha uma coluna para análise:", colunas_disponiveis)

# -------------------------------
# Visualização da base
st.subheader("Visualização da base filtrada")
st.dataframe(df_filtrado)

# -------------------------------
# Gráfico de Dispersão
coluna_variancia = "Variância do rendimento nominal mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados"

st.subheader(f"Dispersão da {coluna_variancia} por Bairro")

# Gráfico de dispersão
fig = px.scatter(
    df_filtrado,
    x="NM_BAIRRO",
    y=coluna_variancia,
    color="NM_BAIRRO",  # cores por bairro (pode usar outra variável se preferir)
    size_max=10,
    labels={
        "NM_BAIRRO": "Bairro",
        coluna_variancia: "Variância do Rendimento"
    }
)

fig.update_layout(
    xaxis_title="Bairro",
    yaxis_title="Variância do Rendimento",
    xaxis_tickangle=-45,
    showlegend=False  # Se quiser remover a legenda de cores por bairro
)

st.plotly_chart(fig, use_container_width=True)





# -------------------------------
# Mapa de bairros (se houver latitude e longitude)
# -------------------------------
if {'LATITUDE', 'LONGITUDE'}.issubset(df_filtrado.columns):
    st.subheader("Mapa dos Bairros")
    fig_mapa = px.scatter_mapbox(
        df_filtrado,
        lat="LATITUDE",
        lon="LONGITUDE",
        hover_name="NM_BAIRRO",
        zoom=10,
        color=coluna,
        height=600
    )
    fig_mapa.update_layout(mapbox_style="open-street-map")
    fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_mapa, use_container_width=True)
else:
    st.info("Colunas 'LATITUDE' e 'LONGITUDE' não encontradas na base. Adicione-as para habilitar o mapa.")
