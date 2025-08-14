# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Hashtag Eletro",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard de Vendas - Hashtag Eletro")

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Faça upload da base 'Base Vendas.xlsx'",
    type=["xlsx"]
)

if uploaded_file:
    # Carregar dados
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Conversões de tipos
    df['Data da Venda'] = pd.to_datetime(df['Data da Venda'])
    df['Qtd Vendida'] = df['Qtd Vendida'].astype(int)
    df['Faturamento'] = df['Faturamento'].astype(float)

    # Sidebar: filtros
    st.sidebar.header("Filtros")
    min_date = df['Data da Venda'].min().date()
    max_date = df['Data da Venda'].max().date()
    date_range = st.sidebar.date_input("Período", [min_date, max_date])
    produtos = st.sidebar.multiselect("Produto", df['Produto'].unique())
    marcas   = st.sidebar.multiselect("Marca", df['Marca'].unique())
    lojas    = st.sidebar.multiselect("Loja", df['Loja'].unique())
    categorias = st.sidebar.multiselect("Categoria", df['Categoria'].unique())

    # Aplicar filtros
    mask = (
        (df['Data da Venda'].dt.date >= date_range[0]) &
        (df['Data da Venda'].dt.date <= date_range[1])
    )
    if produtos:   mask &= df['Produto'].isin(produtos)
    if marcas:     mask &= df['Marca'].isin(marcas)
    if lojas:      mask &= df['Loja'].isin(lojas)
    if categorias: mask &= df['Categoria'].isin(categorias)
    df_f = df[mask]

    # KPIs
    total_faturamento   = df_f['Faturamento'].sum()
    total_quantidade    = df_f['Qtd Vendida'].sum()
    ticket_medio        = (total_faturamento / total_quantidade) if total_quantidade else 0
    total_vendas        = len(df_f)

    # Exibir KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")
    kpi2.metric("Qtd. Vendida", f"{total_quantidade:,}")
    kpi3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    kpi4.metric("Total de Vendas", f"{total_vendas:,}")

    st.markdown("---")

    # Gráfico: Faturamento por mês
    df_f['Mes'] = df_f['Data da Venda'].dt.to_period('M').dt.to_timestamp()
    rev_mes = df_f.groupby('Mes')['Faturamento'].sum().reset_index()
    fig1 = px.line(
        rev_mes, x='Mes', y='Faturamento',
        title="Faturamento por Mês",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Layout de dois gráficos lado a lado
    col1, col2 = st.columns(2)

    # Gráfico: Faturamento por Loja
    rev_loja = df_f.groupby('Loja')['Faturamento'].sum().reset_index().sort_values('Faturamento', ascending=False)
    fig2 = px.bar(
        rev_loja, x='Loja', y='Faturamento',
        title="Faturamento por Loja",
        text_auto='.2s'
    )
    col1.plotly_chart(fig2, use_container_width=True)

    # Gráfico: Pizza Tipo Loja
    rev_tipo = df_f.groupby('Tipo Loja')['Faturamento'].sum().reset_index()
    fig3 = px.pie(
        rev_tipo, names='Tipo Loja', values='Faturamento',
        title="Faturamento por Tipo de Loja"
    )
    col2.plotly_chart(fig3, use_container_width=True)

    # Gráfico: Qtd Vendida por Marca
    qtd_marca = df_f.groupby('Marca')['Qtd Vendida'].sum().reset_index().sort_values('Qtd Vendida', ascending=False)
    fig4 = px.bar(
        qtd_marca, x='Marca', y='Qtd Vendida',
        title="Quantidade Vendida por Marca",
        text_auto=True
    )
    st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("Aguardando upload da base de dados...")

