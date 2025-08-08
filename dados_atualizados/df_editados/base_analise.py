import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("Dashboard Interativo - IBGE")

# Texto explicativo sobre o painel
st.markdown("""
Este painel interativo foi desenvolvido para proporcionar uma visualização clara, dinâmica e georreferenciada dos dados demográficos e socioeconômicos da cidade de **Belém (PA)**. As informações apresentadas foram extraídas da base oficial do **IBGE (Instituto Brasileiro de Geografia e Estatística)**, garantindo alta confiabilidade, abrangência e precisão estatística.

---

### Objetivo

O principal objetivo deste dashboard é auxiliar empresas, instituições públicas, ONGs e pesquisadores na **compreensão do perfil populacional e econômico por bairro**, permitindo decisões mais estratégicas, personalizadas e baseadas em dados.

---

### O que você pode analisar neste painel?

- **Distribuição por Gênero e Faixa Etária:** Dados detalhados sobre o número de moradores por sexo e idade, fundamentais para estratégias de marketing segmentado, lançamento de produtos, políticas públicas ou planejamento urbano.
- **Renda Média e Distribuição Social:** Visualização da renda média mensal e outros indicadores relacionados ao poder de compra, auxiliando na definição de preços, expansão de serviços ou identificação de regiões economicamente vulneráveis.
- **Tipologia dos Domicílios:** Classificação dos tipos de moradias (casas, apartamentos, vilas, cortiços), útil para mapear demandas por reformas, construção civil ou serviços residenciais.

---

### Aplicações Práticas

- **Empresas:** Análise de mercado por bairro para expansão de unidades, definição de preços e campanhas direcionadas.
- **Órgãos Públicos:** Planejamento de políticas públicas, ações sociais e alocação de recursos com base em dados reais.
- **Pesquisadores e ONGs:** Estudo de desigualdade social, urbanismo, saúde pública e inclusão digital.
- **Cidadãos:** Entendimento do seu próprio bairro em comparação com outros da cidade.

---

Este painel é um exemplo de como dados públicos podem ser transformados em conhecimento valioso quando combinados com boas ferramentas de análise e visualização.
""")

# Carregando a base
try:
    df = pd.read_csv(r'C:\Users\devma\Desktop\DEMANDAS\IBGE\dash_ibge\dados_atualizados\df_editados\base_completa_final.csv')
    st.success("Base de dados carregada com sucesso!")
except FileNotFoundError:
    st.error("Arquivo 'base_completa_final.csv' não encontrado. Certifique-se de que o arquivo está no caminho correto.")
    st.stop()

# -------------------------------
# VISÃO GERAL DA CIDADE
# -------------------------------
st.subheader("📊 Visão Geral da Cidade de Belém")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("População Total", f"{df['Quantidade de moradores'].sum():,.0f}")
with col2:
    st.metric("Total Masculino", f"{df['Sexo masculino'].sum():,.0f}")
with col3:
    st.metric("Total Feminino", f"{df['Sexo feminino'].sum():,.0f}")
with col4:
    renda_media_geral = df["Valor do rendimento nominal médio mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados"].mean()
    st.metric("Renda Média Mensal", f"R$ {renda_media_geral:,.2f}")

st.markdown("---")

# População por Bairro
pop_bairro = df.groupby("NM_BAIRRO")["Quantidade de moradores"].sum().reset_index()
fig_pop_bairro = px.bar(pop_bairro, x="NM_BAIRRO", y="Quantidade de moradores",
                        title="População Total por Bairro",
                        labels={"Quantidade de moradores": "População", "NM_BAIRRO": "Bairro"})
st.plotly_chart(fig_pop_bairro, use_container_width=True)

# Distribuição por Sexo
dados_sexo_total = pd.DataFrame({
    "Sexo": ["Masculino", "Feminino"],
    "População": [df["Sexo masculino"].sum(), df["Sexo feminino"].sum()]
})
fig_sexo_total = px.bar(dados_sexo_total, x="Sexo", y="População",
                        title="Distribuição Total por Sexo",
                        color="Sexo",
                        labels={"População": "Número de Moradores"})
st.plotly_chart(fig_sexo_total, use_container_width=True)

# População por Faixa Etária
colunas_masculino_total = [col for col in df.columns if 'Sexo masculino' in col and 'anos' in col]
dados_faixa_total = pd.DataFrame({
    'Faixa Etária': [c.replace('Sexo masculino, ', '') for c in colunas_masculino_total],
    'Masculino': [df[c].sum() for c in colunas_masculino_total],
    'Feminino': [df[c.replace('Sexo masculino', 'Sexo feminino')].sum() for c in colunas_masculino_total]
})
fig_faixa_total = px.bar(dados_faixa_total, x='Faixa Etária', y=['Masculino', 'Feminino'],
                         title="Distribuição por Faixa Etária - Total da Cidade",
                         barmode='group',
                         labels={'value': 'Número de Moradores', 'variable': 'Sexo'})
st.plotly_chart(fig_faixa_total, use_container_width=True)

# Dispersão População vs Renda Média
df_disp = df.groupby("NM_BAIRRO").agg({
    "Quantidade de moradores": "sum",
    "Valor do rendimento nominal médio mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados": "mean"
}).reset_index()

fig_disp = px.scatter(df_disp,
                      x="Quantidade de moradores",
                      y="Valor do rendimento nominal médio mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados",
                      text="NM_BAIRRO",
                      title="Correlação entre População e Renda Média por Bairro",
                      labels={"Quantidade de moradores": "População Total",
                              "Valor do rendimento nominal médio mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados": "Renda Média (R$)"},
                      size="Quantidade de moradores")
st.plotly_chart(fig_disp, use_container_width=True)

st.markdown("---")

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
        df_bairro = df[df["NM_BAIRRO"] == bairro].copy()
        
        with st.expander(f"Análise do Bairro: {bairro}", expanded=True):
            st.markdown("---")

            # Indicadores de População
            st.subheader("Indicadores de População")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("População Total", f'{df_bairro["Quantidade de moradores"].iloc[0]:,.0f}')
            with col2:
                st.metric("Moradores do Sexo Masculino", f'{df_bairro["Sexo masculino"].iloc[0]:,.0f}')
            with col3:
                st.metric("Moradores do Sexo Feminino", f'{df_bairro["Sexo feminino"].iloc[0]:,.0f}')
                
            st.markdown("---")

            # Métricas de Renda e Domicílios
            st.subheader("Métricas de Renda e Domicílios")
            col_renda_1, col_renda_2, col_renda_3, col_renda_4 = st.columns(4)

            try:
                valor_pessoas_responsaveis = df_bairro["Pessoas responsáveis em domicílios particulares permanentes ocupados"].iloc[0]
                with col_renda_1:
                    st.metric("Pessoas Responsáveis", f'{valor_pessoas_responsaveis:,.0f}')
            except KeyError:
                with col_renda_1:
                    st.warning("Coluna não encontrada: Pessoas responsáveis...")

            try:
                valor_moradores_por_domicilio = df_bairro["Moradores em domicílios particulares permanentes ocupados"].iloc[0]
                with col_renda_2:
                    st.metric("Moradores por Domicílio", f'{valor_moradores_por_domicilio:,.0f}')
            except KeyError:
                with col_renda_2:
                    st.warning("Coluna não encontrada: Moradores em domicílios...")

            try:
                valor_renda_media = df_bairro["Valor do rendimento nominal médio mensal das pessoas responsáveis com rendimentos por domicílios particulares permanentes ocupados"].iloc[0]
                with col_renda_3:
                    st.metric("Renda Média Mensal", f'R$ {valor_renda_media:,.2f}')
            except KeyError:
                with col_renda_3:
                    st.warning("Coluna não encontrada: Valor do rendimento...")

            st.markdown("---")
            
            # Gráfico de População por Sexo
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
            
            # Gráfico de População por Faixa Etária e Sexo
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
            
            # Gráfico de Domicílios
            st.subheader("Distribuição de Domicílios Particulares Ocupados")
            try:
                colunas_domicilios_particulares = {
                    'Casa': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é casa',
                    'Casa de vila ou condomínio': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é casa de vila ou em condomínio',
                    'Apartamento': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é apartamento',
                    'Casa de cômodos ou cortiço': 'Domicílios Particulares Permanentes Ocupados, Tipo de espécie é habitação em casa de cômodos ou cortiço'
                }

                dados_domicilios_particulares = pd.DataFrame({
                    'Tipo de Domicílio': list(colunas_domicilios_particulares.keys()),
                    'Quantidade': [df_bairro[col].iloc[0] for col in colunas_domicilios_particulares.values()]
                })

                fig_dom_particulares = px.pie(dados_domicilios_particulares, values='Quantidade', names='Tipo de Domicílio',
                                              title=f"Distribuição de Domicílios Particulares em {bairro}")
                st.plotly_chart(fig_dom_particulares, use_container_width=True)
            except KeyError as e:
                st.warning(f"Erro ao gerar o gráfico de domicílios. A coluna {e} não foi encontrada. Verifique o nome das colunas na sua base de dados.")

# -------------------------------
# Visualização da base completa
# -------------------------------
st.subheader("Visualização da Base de Dados Completa")
st.dataframe(df)
