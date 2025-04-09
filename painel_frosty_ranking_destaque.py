import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

df = pd.read_csv(r"C:\Users\brend\Downloads\base_frosty_indicadores_industriais.csv", sep=';')
coluna_motivo = [col for col in df.columns if "Motivo" in col]
df["Data Abertura"] = pd.to_datetime(df["Data Abertura"])
df["Data Início"] = pd.to_datetime(df["Data Início"])
df["Data Finalização"] = pd.to_datetime(df["Data Finalização"])
df["Mês/Ano"] = df["Data Abertura"].dt.to_period("M").astype(str)

st.set_page_config(layout="wide", page_title="Painel Frosty Premium", page_icon="❄️")

# Layout Frosty Premium com cores e ícones
st.markdown("""
<style>
body {
    background: #E3F2FD;
    font-family: 'Segoe UI', sans-serif;
}
.big-title {
    font-size: 42px;
    text-align: center;
    font-weight: bold;
    color: #0D47A1;
    margin-bottom: 10px;
}
.section-title {
    font-size: 24px;
    font-weight: 600;
    color: #004D40;
    margin-top: 30px;
    margin-bottom: 10px;
}
.kpi-box {
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    color: white;
    font-weight: bold;
    font-size: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.kpi-oee {
    background-color: #1E88E5;
}
.kpi-mttr {
    background-color: #E53935;
}
.kpi-prod {
    background-color: #43A047;
}
.trofeu-card {
    background: linear-gradient(145deg, #BBDEFB, #E3F2FD);
    padding: 20px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    color: #0D47A1;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Título e logo
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.image("logo_frosty.png", width=100)
    st.markdown("<div class='big-title'>📊 Painel Industrial Frosty</div>", unsafe_allow_html=True)

meses = sorted(df["Mês/Ano"].unique())
mes_escolhido = st.selectbox("📅 Selecione o mês:", meses)
df_mes = df[df["Mês/Ano"] == mes_escolhido]

# KPIs com ícones e cores nos cards
col1, col2, col3 = st.columns(3)
with col1:
    oee = 0.84
    st.markdown(f"<div class='kpi-box kpi-oee'>🔧 OEE<br>{oee*100:.2f}%</div>", unsafe_allow_html=True)
with col2:
    mttr = (df_mes["Data Finalização"] - df_mes["Data Início"]).dt.total_seconds().mean() / 60
    st.markdown(f"<div class='kpi-box kpi-mttr'>🛠️ MTTR Médio<br>{mttr:.1f} min</div>", unsafe_allow_html=True)
with col3:
    produtividade = df_mes["Produto Produzido"].sum() / df_mes["Horas Trabalhadas"].sum()
    st.markdown(f"<div class='kpi-box kpi-prod'>⚙️ Produtividade<br>{produtividade:.1f} prod/h</div>", unsafe_allow_html=True)

# Gráfico Equipamentos com mais paradas


# Gráfico Equipamentos com mais paradas (barra vertical)
st.markdown("<div class='section-title'>🧊 Equipamentos com Mais Paradas</div>", unsafe_allow_html=True)
equip = df_mes["Equipamento"].value_counts().head(5).reset_index()
equip.columns = ["Equipamento", "Paradas"]
fig_vert = px.bar(equip, x="Equipamento", y="Paradas", text="Paradas", color="Paradas", color_continuous_scale="Blues")
fig_vert.update_layout(template="simple_white", height=400, font=dict(color="#004D40", size=14))
fig_vert.update_traces(textposition="outside", marker_line_color="black", marker_line_width=1)
st.plotly_chart(fig_vert, use_container_width=True)

# Top 5 motivos com alertas visuais
st.markdown("<div class='section-title'>🚦 Top 5 Motivos de Parada (Alerta)</div>", unsafe_allow_html=True)
if coluna_motivo:
    top_motivos = df_mes[coluna_motivo[0]].value_counts().head(5).reset_index()
    top_motivos.columns = ["Motivo", "Ocorrências"]

    def color_alerta(val):
        if val >= 15:
            return "background-color: #E53935; color: white; font-weight: bold"
        elif val >= 10:
            return "background-color: #FDD835; color: black; font-weight: bold"
        else:
            return "background-color: #C8E6C9; color: black; font-weight: bold"

    st.dataframe(top_motivos.style
        .applymap(color_alerta, subset=["Ocorrências"])
        .set_table_styles([{'selector': 'th', 'props': [('background-color', '#1E88E5'), ('color', 'white')]}])
        .set_properties(**{'text-align': 'center'})
    , use_container_width=True)


# 📅 Ranking por Mês - Técnicos mais produtivos
st.markdown("## 🥇 Ranking por Mês")
meses_disponiveis = sorted(df["Data Abertura"].dt.to_period("M").astype(str).unique())
mes_ranking = st.selectbox("📅 Selecione o mês do ranking:", meses_disponiveis)

df_mes_ranking = df[df["Data Abertura"].dt.to_period("M").astype(str) == mes_ranking]
prod_tecnicos = (
    df_mes_ranking.groupby("Técnico")[["Produto Produzido", "Horas Trabalhadas"]]
    .sum()
    .assign(**{"Prod/h": lambda x: x["Produto Produzido"] / x["Horas Trabalhadas"]})
    .reset_index()
    .sort_values("Prod/h", ascending=False)
)

# Adicionando emojis de colocação
emojis = ["🥇", "🥈", "🥉", "#4", "#5"]
prod_tecnicos = prod_tecnicos.head(5).reset_index(drop=True)
prod_tecnicos.insert(0, "", emojis[:len(prod_tecnicos)])

st.markdown("### 🏆 Técnicos mais produtivos")
st.dataframe(prod_tecnicos[["", "Técnico", "Prod/h"]], use_container_width=True)

# Painel destaque técnico do mês
st.markdown("## 👤 Técnico Destaque do Mês")
destaque = prod_tecnicos.iloc[0]
with st.container():
    st.markdown(f"""<div style='padding: 20px; background-color: #E8F5E9; border-left: 5px solid #43A047; border-radius: 5px;'>
        <h3 style='margin:0;'>🏆 {destaque['Técnico']}</h3>
        <p style='margin:0;'>Produtividade: <strong>{destaque['Prod/h']:.1f} prod/h</strong></p>
        <p style='margin:0;'>Mês: <strong>{mes_ranking}</strong></p>
    </div>""", unsafe_allow_html=True)
