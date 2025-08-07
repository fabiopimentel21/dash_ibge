import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("Dashboard Interativo - IBGE")


# Carregando a base (usando o arquivo CSV que você forneceu)
try:
    df = pd.read_csv(r'C:\Users\devma\Desktop\DEMANDAS\IBGE\dash_ibge\dados_atualizados\df_editados\base_completa_final.csv')
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
            
            # 1. Indicadores Chave de População
            st.subheader("Indicadores de População")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("População Total", f'{df_bairro["Quantidade de moradores"].iloc[0]:,.0f}')
            with col2:
                st.metric("Moradores do Sexo Masculino", f'{df_bairro["Sexo masculino"].iloc[0]:,.0f}')
            with col3:
                st.metric("Moradores do Sexo Feminino", f'{df_bairro["Sexo feminino"].iloc[0]:,.0f}')
                
            st.markdown("---")

            # Métricas de Renda e Domicílios em Cartões
            st.subheader("Métricas de Renda e Domicílios")
            
            col_renda_1, col_renda_2, col_renda_3, col_renda_4 = st.columns(4)

            # Métrica: Pessoas Responsáveis
            try:
                valor_pessoas_responsaveis = df_bairro["Pessoas responsáveis em domicílios particulares permanentes ocupados"].iloc[0]
                with col_renda_1:
                    st.metric("Pessoas Responsáveis", f'{valor_pessoas_responsaveis:,.0f}')
            except KeyError:
                with col_renda_1:
                    st.warning("Coluna não encontrada: Pessoas responsáveis...")

            # Métrica: Moradores por Domicílio
            try:
                valor_moradores_por_domicilio = df_bairro["Moradores em domicílios particulares permanentes ocupados"].iloc[0]
                with col_renda_2:
                    st.metric("Moradores por Domicílio", f'{valor_moradores_por_domicilio:,.0f}')
            except KeyError:
                with col_renda_2:
                    st.warning("Coluna não encontrada: Moradores em domicílios...")

            # Métrica: Rendimento Médio Mensal
            try:
                valor_renda_media = df_bairro["Valor do rendimento nominal médio mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados"].iloc[0]
                with col_renda_3:
                    st.metric("Renda Média Mensal", f'R$ {valor_renda_media:,.2f}')
            except KeyError:
                with col_renda_3:
                    st.warning("Coluna não encontrada: Valor do rendimento...")

            # Métrica: Variância do Rendimento Mensal
            #try:
                #valor_variancia_renda = df_bairro["Variância do rendimento nominal mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados"].iloc[0]
                #with col_renda_4:
                   # st.metric("Variância da Renda", f'{valor_variancia_renda:,.2f}')
            #except KeyError:
                #with col_renda_4:
                   # st.warning("Coluna não encontrada: Variância do rendimento...")

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
            
            colunas_masculino = [col for col in df_bairro.columns if 'Sexo masculino' in col and 'anos' in col]
            
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
            
            # NOVO GRÁFICO: Domicílios Particulares
            st.subheader("Distribuição de Domicílios Particulares Ocupados")
            
            try:
                colunas_domicilios_particulares = {
                    'Casa': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é casa',
                    'Casa de vila ou condomínio': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é casa de vila ou em condomínio',
                    'Apartamento': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é apartamento',
                    'Casa de cômodos ou cortiço': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é habitação em casa de cômodos ou cortiço'
                }
                
                # Coleta os dados para as colunas detalhadas de domicílios
                dados_domicilios_particulares = pd.DataFrame({
                    'Tipo de Domicílio': list(colunas_domicilios_particulares.keys()),
                    'Quantidade': [df_bairro[coluna].iloc[0] for coluna in colunas_domicilios_particulares.values()]
                })

                fig_dom_particulares = px.pie(dados_domicilios_particulares, values='Quantidade', names='Tipo de Domicílio',
                                              title=f"Distribuição de Domicílios Particulares em {bairro}")
                
                st.plotly_chart(fig_dom_particulares, use_container_width=True)
            except KeyError as e:
                st.warning(f"Erro ao gerar o gráfico de domicílios. A coluna {e} não foi encontrada. Verifique o nome das colunas na sua base de dados.")

# -------------------------------
# Visualização da base completa
st.subheader("Visualização da Base de Dados Completa")
st.dataframe(df)