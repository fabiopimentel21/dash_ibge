import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("Dashboard Interativo - IBGE")


# Carregando a base (usando o arquivo CSV que você forneceu)
try:
    df = pd.read_csv(r'C:\Users\devma\Desktop\DEMANDAS\IBGE\dash_ibge\dados_atualizados\df_editados\base_completa_final.csv') # Alterado para read_csv
    st.success("Base de dados carregada com sucesso!")
except FileNotFoundError:
    st.error("Arquivo 'base_completa_final.xlsx - Sheet1.csv' não encontrado. Certifique-se de que o arquivo está no mesmo diretório do script.")
    st.stop()


# -------------------------------
# Filtros no Sidebar
# -------------------------------
st.sidebar.header("Filtros de Bairros")

bairros_unicos = sorted(df["NM_BAIRRO"].unique())
bairros_selecionados = st.sidebar.multiselect("Selecione um ou mais bairros para análise:", bairros_unicos)

# -------------------------------
# Análise por bairro separadamente
# -------------------------------
st.subheader("Análise Detalhada por Bairro")

if not bairros_selecionados:
    st.info("Por favor, selecione um ou mais bairros no painel lateral para iniciar a análise detalhada.")
else:
    for bairro in bairros_selecionados:
        # Filtra os dados para o bairro atual no loop
        df_bairro = df[df["NM_BAIRRO"] == bairro].copy()
        
        with st.expander(f"Análise do Bairro: {bairro}", expanded=True):
            
            st.markdown("---")
            
            # 1. Indicadores Chave
            st.subheader("Indicadores Chave")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("População Total", f'{df_bairro["Quantidade de moradores"].iloc[0]:,.0f}')
            with col2:
                st.metric("Moradores do Sexo Masculino", f'{df_bairro["Sexo masculino"].iloc[0]:,.0f}')
            with col3:
                st.metric("Moradores do Sexo Feminino", f'{df_bairro["Sexo feminino"].iloc[0]:,.0f}')
                
            st.markdown("---")
            
            # 2. Gráfico de População por Sexo
            st.subheader("Distribuição da População por Sexo")
            dados_sexo = pd.DataFrame({
                'Sexo': ['Masculino', 'Feminino'],
                'População': [df_bairro["Sexo masculino"].iloc[0], df_bairro["Sexo feminino"].iloc[0]]
            })
            fig_sexo = px.bar(dados_sexo, x='Sexo', y='População',
                              title=f"População do Bairro {bairro} por Sexo",
                              color='Sexo',
                              labels={'População': 'Número de Moradores', 'Sexo': 'Sexo'})
            st.plotly_chart(fig_sexo, use_container_width=True)
            
            st.markdown("---")
            
            # 3. Gráfico de População por Faixa Etária e Sexo
            st.subheader("Distribuição da População por Faixa Etária e Sexo")
            
            # Coleta as colunas de faixas etárias
            colunas_masculino = [col for col in df_bairro.columns if 'Sexo masculino' in col and 'anos' in col]
            colunas_feminino = [col for col in df_bairro.columns if 'Sexo feminino' in col and 'anos' in col]
            
            # Cria um DataFrame para o gráfico
            dados_faixa_etaria = pd.DataFrame({
                'Faixa Etária': [c.replace('Sexo masculino, ', '') for c in colunas_masculino],
                'Masculino': [df_bairro[c].iloc[0] for c in colunas_masculino],
                'Feminino': [df_bairro[c.replace('Sexo masculino', 'Sexo feminino')].iloc[0] for c in colunas_masculino]
            })

            fig_faixa_etaria = px.bar(dados_faixa_etaria, x='Faixa Etária', y=['Masculino', 'Feminino'],
                                      title=f"População do Bairro {bairro} por Faixa Etária",
                                      barmode='group',
                                      labels={'value': 'Número de Moradores', 'variable': 'Sexo'})
            
            st.plotly_chart(fig_faixa_etaria, use_container_width=True)
            
            st.markdown("---")
            
            # 4. Outros Gráficos (Exemplo: Domicílios)
            st.subheader("Informações sobre Domicílios")
            
            # Crie um DataFrame para a visualização
            dados_domicilios = pd.DataFrame({
                'Tipo de Habitação': ['Domicílios Particulares Permanentes Ocupados', 'Unidades de Habitação em Domicílios Coletivos Com Mor'],
                'Quantidade': [df_bairro["Domicílios Particulares Permanentes Ocupados"].iloc[0], df_bairro["Unidades de Habitação em Domicílios Coletivos Com Mor"].iloc[0]]
            })

            fig_domicilios = px.pie(dados_domicilios, values='Quantidade', names='Tipo de Habitação',
                                    title=f"Distribuição de Habitações no Bairro {bairro}")
            st.plotly_chart(fig_domicilios, use_container_width=True)
            
            # 5. Adicione outros gráficos conforme sua necessidade...
            # Por exemplo, para "Variância do rendimento nominal..."
            # fig_rendimento = ...
            # st.plotly_chart(fig_rendimento, use_container_width=True)

# -------------------------------
# Visualização da base completa
st.subheader("Visualização da Base de Dados Completa")
st.dataframe(df)