import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------------
# CONFIGURAÇÃO INICIAL
# -------------------------
st.set_page_config(page_title="Dashboard SUS - Ceará", layout="wide")
st.title("📊 Dashboard de Atendimentos SUS - Ceará")

# -------------------------
# CARREGAMENTO DO CSV
# -------------------------
df = pd.read_csv("atendimentos.csv")
df.columns = [c.strip().upper() for c in df.columns]
df["UF"] = "CE"

# -------------------------
# AGREGAÇÃO DOS DADOS
# -------------------------
agg = (
    df.groupby(["MUNICÍPIO", "UF", "POPULAÇÃO", "ÁREA_KM2",
                "TAXA_ALFABETIZAÇÃO", "CENTROIDE_LONGITUDE", "CENTROIDE_LATITUDE"])
    .agg(VOLUME_ATENDIMENTOS=("ID", "count"))
    .reset_index()
)
agg["ATENDIMENTOS_POR_100MIL"] = (agg["VOLUME_ATENDIMENTOS"] / agg["POPULAÇÃO"]) * 100000

# -------------------------
# 🎚️ SIDEBAR - MODO DE VISUALIZAÇÃO
# -------------------------
st.sidebar.header("🔎 Filtro de Município")

modo = st.sidebar.radio(
    "Modo de visualização:",
    ("Visão geral", "Foco em um município")
)

# Se for modo detalhado
if modo == "Foco em um município":
    municipio_escolhido = st.sidebar.selectbox("Selecione o município:", sorted(agg["MUNICÍPIO"].unique()))
    filtered = agg[agg["MUNICÍPIO"] == municipio_escolhido]
    st.subheader(f"📍 Análise detalhada - {municipio_escolhido}")
else:
    filtered = agg.copy()
    municipio_escolhido = None
    st.subheader("🌎 Visão geral dos municípios do Ceará")

# -------------------------
# VISUALIZAÇÃO 1 - Volume de atendimentos
# -------------------------
if modo == "Visão geral":
    st.header("1️⃣ Volume de atendimentos por município")
    fig1 = px.bar(
        filtered.sort_values("VOLUME_ATENDIMENTOS", ascending=False),
        x="MUNICÍPIO",
        y="VOLUME_ATENDIMENTOS",
        color="UF",
        labels={"VOLUME_ATENDIMENTOS": "Volume de atendimentos"},
    )
else:
    st.header("1️⃣ Volume total de atendimentos")
    fig1 = px.bar(
        filtered,
        x="MUNICÍPIO",
        y="VOLUME_ATENDIMENTOS",
        color="MUNICÍPIO",
        text="VOLUME_ATENDIMENTOS",
        labels={"VOLUME_ATENDIMENTOS": "Atendimentos"},
    )

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# VISUALIZAÇÃO 2 - Indicadores / Proporção
# -------------------------
if modo == "Visão geral":
    st.header("2️⃣ Proporção de atendimentos por 100 mil habitantes")
    fig2 = px.bar(
        filtered.sort_values("ATENDIMENTOS_POR_100MIL", ascending=False),
        x="MUNICÍPIO",
        y="ATENDIMENTOS_POR_100MIL",
        color="UF",
        labels={"ATENDIMENTOS_POR_100MIL": "Atendimentos por 100 mil hab."},
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.header("2️⃣ Indicadores demográficos e proporcionais")
    info = filtered.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("População", f"{int(info['POPULAÇÃO']):,}".replace(",", "."))
    col2.metric("Área (km²)", f"{info['ÁREA_KM2']:.1f}")
    col3.metric("Taxa de alfabetização", f"{info['TAXA_ALFABETIZAÇÃO']*100:.1f}%")
    col4.metric("Atendimentos / 100 mil hab.", f"{info['ATENDIMENTOS_POR_100MIL']:.1f}")

# -------------------------
# VISUALIZAÇÃO 3 - Ranking (somente visão geral)
# -------------------------
if modo == "Visão geral":
    st.header("3️⃣ Ranking dos municípios por proporção de atendimentos")

    top5 = agg.nlargest(5, "ATENDIMENTOS_POR_100MIL")[["MUNICÍPIO", "ATENDIMENTOS_POR_100MIL"]]
    bottom5 = agg.nsmallest(5, "ATENDIMENTOS_POR_100MIL")[["MUNICÍPIO", "ATENDIMENTOS_POR_100MIL"]]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top 5 - Maior proporção")
        st.table(top5.set_index("MUNICÍPIO").round(2))
    with col2:
        st.subheader("⚠️ Bottom 5 - Menor proporção")
        st.table(bottom5.set_index("MUNICÍPIO").round(2))

# -------------------------
# VISUALIZAÇÃO 4 - Mapa interativo
# -------------------------
st.header(f"{'3️⃣' if modo == "Foco em um município" else '4️⃣'} Mapa interativo dos atendimentos SUS")

fig_map = px.scatter_mapbox(
    filtered,
    lat="CENTROIDE_LATITUDE",
    lon="CENTROIDE_LONGITUDE",
    hover_name="MUNICÍPIO",
    hover_data={
        "VOLUME_ATENDIMENTOS": True,
        "ATENDIMENTOS_POR_100MIL": True,
        "POPULAÇÃO": True
    },
    size="VOLUME_ATENDIMENTOS",
    color="ATENDIMENTOS_POR_100MIL",
    color_continuous_scale="YlOrRd",
    mapbox_style="carto-positron",
    zoom=6 if modo == "Visão geral" else 8,
    height=600,
)
st.plotly_chart(fig_map, use_container_width=True)

# -------------------------
# RODAPÉ
# -------------------------
st.markdown("---")
st.markdown("**Fonte:** Dados de atendimentos SUS - Estado do Ceará")
