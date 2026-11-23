import os
from datetime import date, datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

from dashboard_utils import variaciones_diarias, volatilidad_anual

GRIS = "#B9C3D1"
AZUL = "#1C4C9A"
ROJO = "#B2182B"
AZUL_POS = "#2166AC"
CUALI = ["#E69F00", "#56B4E9", "#009E73", "#0072B2"]
SIE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
sns.set_theme(style="whitegrid")

st.set_page_config(page_title="Tablero del SIE", layout="wide")


def leer_token():
    try:
        if "banxico_token" in st.secrets:
            return str(st.secrets["banxico_token"]).strip()
    except Exception:
        pass
    return os.environ.get("BANXICO_TOKEN", "").strip() or None


@st.cache_data(ttl=3600, show_spinner=False)
def consultar(claves, inicio, fin, token):
    url = f"{SIE}/{','.join(claves)}/datos/{inicio}/{fin}"
    respuesta = requests.get(
        url,
        headers={
            "Bmx-Token": token,
            "Accept": "application/json",
            "User-Agent": "UPQ-IDIA224/1.0",
        },
        timeout=60,
    )
    if respuesta.status_code == 401:
        raise PermissionError("El token no fue aceptado.")
    if respuesta.status_code == 429:
        raise PermissionError("Demasiadas peticiones. Espera un momento.")
    respuesta.raise_for_status()

    tipo = respuesta.headers.get("Content-Type", "")
    if "json" not in tipo.lower():
        raise ValueError(f"El servidor no devolvió JSON ({tipo}). Revisa token y clave.")

    tablas, faltantes = [], {}
    for serie in respuesta.json()["bmx"]["series"]:
        if "datos" not in serie:
            continue
        tabla = pd.DataFrame(serie["datos"])
        tabla["Fecha"] = pd.to_datetime(tabla.pop("fecha"), format="%d/%m/%Y")
        dato = tabla.pop("dato").astype(str)
        faltantes[serie["idSerie"]] = int((dato == "N/E").sum())
        tabla["Valor"] = pd.to_numeric(
            dato.str.replace(",", "", regex=False), errors="coerce"
        )
        tabla["Clave"] = serie["idSerie"]
        tabla["Serie"] = serie.get("titulo", serie["idSerie"])
        tablas.append(tabla)

    if not tablas:
        raise ValueError("Ninguna clave devolvió datos en ese periodo.")

    df = pd.concat(tablas, ignore_index=True)
    df["Anio"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    return df, faltantes


TOKEN = leer_token()
if TOKEN and len(TOKEN) < 32:
    st.error("El token parece incompleto. Verifica que tenga los 64 caracteres.")
    st.stop()
if not TOKEN:
    st.error("Falta el token del SIE de Banxico.")
    st.markdown(
        "Solicítalo en https://www.banxico.org.mx/SieAPIRest/service/v1/token "
        "y guárdalo en `.streamlit/secrets.toml` como "
        '`banxico_token = "TU_TOKEN"`.'
    )
    st.stop()

with st.sidebar:
    st.header("Qué consultar")
    texto = st.text_input("Claves de las series", "SF43718")
    inicio = st.date_input("Desde", date(2021, 1, 1))
    fin = st.date_input("Hasta", date(2025, 12, 31))
    suavizado = st.slider("Días de media móvil", 1, 90, 30)
    st.caption("Fuente: SIE, Banco de México")

claves = [c.strip().upper() for c in texto.split(",") if c.strip()]
if not claves:
    st.info("Escribe al menos una clave.")
    st.stop()
if inicio >= fin:
    st.error("La fecha inicial debe ser anterior a la final.")
    st.stop()

with st.spinner("Consultando el SIE..."):
    try:
        df, faltantes = consultar(tuple(claves), str(inicio), str(fin), TOKEN)
    except PermissionError as error:
        st.error(str(error))
        st.stop()
    except ValueError as error:
        st.warning(str(error))
        st.stop()
    except requests.exceptions.RequestException as error:
        st.error(f"No se pudo consultar el SIE: {error}")
        st.stop()

limpio = df.dropna(subset=["Valor"]).copy()
if limpio.empty:
    st.warning("No hay valores numéricos en el periodo.")
    st.stop()

principal = limpio[limpio["Clave"] == claves[0]].sort_values("Fecha").copy()
if principal.empty:
    st.warning(f"La primera clave ({claves[0]}) no devolvió datos numéricos.")
    st.stop()

st.title("Tablero de series del SIE")
st.caption(
    f"{principal['Serie'].iloc[0]} · del {inicio} al {fin} · "
    f"consultado el {datetime.now():%d/%m/%Y %H:%M}"
)

primero, ultimo = principal["Valor"].iloc[0], principal["Valor"].iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Días con dato", len(principal))
c2.metric("Días inhábiles (N/E)", faltantes.get(claves[0], 0))
c3.metric("Último valor", f"{ultimo:,.4f}",
          delta=f"{(ultimo / primero - 1) * 100:+.1f} % en el periodo")
c4.metric("Mínimo y máximo",
          f"{principal['Valor'].min():,.2f} – {principal['Valor'].max():,.2f}")
st.divider()

izquierda, derecha = st.columns(2)
with izquierda:
    if len(claves) == 1:
        st.subheader("La serie y su tendencia")
        principal["Suave"] = principal["Valor"].rolling(suavizado).mean()
        fig, ax = plt.subplots(figsize=(6, 3.4))
        ax.plot(principal["Fecha"], principal["Valor"], color=GRIS,
                linewidth=0.9, label="Valor observado")
        ax.plot(principal["Fecha"], principal["Suave"], color=AZUL,
                linewidth=2, label=f"Media móvil {suavizado} días")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Valor de la serie")
        ax.legend(frameon=False)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.subheader("Comparación en base 100")
        comparacion = limpio.sort_values("Fecha").copy()
        comparacion["Base100"] = comparacion.groupby("Clave")["Valor"].transform(
            lambda serie: serie / serie.iloc[0] * 100
        )
        fig, ax = plt.subplots(figsize=(6, 3.4))
        for i, clave in enumerate(claves):
            parte = comparacion[comparacion["Clave"] == clave]
            if not parte.empty:
                ax.plot(parte["Fecha"], parte["Base100"],
                        color=CUALI[i % len(CUALI)], linewidth=1.8, label=clave)
        ax.axhline(100, color="gray", linewidth=0.8)
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Índice base 100")
        ax.legend(frameon=False)
        st.pyplot(fig)
        plt.close(fig)

with derecha:
    st.subheader("Cambio de un mes a otro")
    mensual = principal.set_index("Fecha")["Valor"].resample("ME").last()
    cambio = (mensual.pct_change() * 100).dropna()
    if cambio.empty:
        st.info("No hay suficientes meses para calcular cambios mensuales.")
    else:
        fig, ax = plt.subplots(figsize=(6, 3.4))
        ax.bar(cambio.index, cambio.values,
               color=[ROJO if v > 0 else AZUL_POS for v in cambio.values],
               width=20)
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_xlabel("Mes")
        ax.set_ylabel("Cambio respecto al mes anterior (%)")
        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            "Rojo: el valor subió. Azul: bajó. En el tipo de cambio FIX, "
            "un aumento significa que se necesitan más pesos por dólar."
        )

# Las dos visualizaciones siguientes analizan las variaciones porcentuales.
principal["Variacion"] = variaciones_diarias(principal["Valor"])
por_anio = principal.dropna(subset=["Variacion"])
abajo_izq, abajo_der = st.columns(2)

with abajo_izq:
    st.subheader("Variabilidad por año (Boxplot)")
    if por_anio.empty:
        st.info("No hay suficientes observaciones para construir el Boxplot.")
    else:
        fig, ax = plt.subplots(figsize=(6, 3.4))
        sns.boxplot(data=por_anio, x="Anio", y="Variacion", color=GRIS, ax=ax)
        ax.axhline(0, color=ROJO, linewidth=1, linestyle="--")
        ax.set_xlabel("Año")
        ax.set_ylabel("Variación entre observaciones consecutivas (%)")
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Compara la dispersión, la mediana y los valores atípicos por año.")

with abajo_der:
    st.subheader("Distribución de variaciones diarias")
    distribucion = por_anio["Variacion"].replace([np.inf, -np.inf], np.nan).dropna()
    if distribucion.empty:
        st.info("No hay suficientes variaciones válidas para construir el histograma.")
    else:
        media, mediana = distribucion.mean(), distribucion.median()
        fig, ax = plt.subplots(figsize=(6, 3.4))
        ax.hist(distribucion, bins="auto", color=AZUL_POS,
                edgecolor="white", alpha=0.88)
        ax.axvline(0, color="gray", linewidth=1, linestyle=":",
                   label="Sin variación")
        ax.axvline(media, color=ROJO, linewidth=1.5, linestyle="--",
                   label=f"Media: {media:.3f} %")
        ax.axvline(mediana, color=AZUL, linewidth=1.5, linestyle="-.",
                   label=f"Mediana: {mediana:.3f} %")
        ax.set_xlabel("Variación porcentual")
        ax.set_ylabel("Frecuencia")
        ax.legend(frameon=False)
        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            "Muestra la frecuencia de los cambios entre observaciones consecutivas. "
            "La media resume el promedio y la mediana el valor central."
        )

# Quinta gráfica: resume la variabilidad de los cambios diarios por año.
st.divider()
st.subheader("Volatilidad anual de la serie")
volatilidad = volatilidad_anual(por_anio)
if volatilidad.empty:
    st.info("No hay suficientes variaciones válidas para calcular la volatilidad anual.")
else:
    fig, ax = plt.subplots(figsize=(12, 3.4))
    ax.bar(volatilidad.index.astype(str), volatilidad.values, color=AZUL_POS)
    ax.set_xlabel("Año")
    ax.set_ylabel("Desviación estándar de las variaciones (%)")
    ax.grid(axis="y", alpha=0.25)
    st.pyplot(fig)
    plt.close(fig)
    st.caption(
        "Permite comparar qué años tuvieron cambios diarios más variables. "
        "Una barra más alta representa mayor volatilidad en las variaciones."
    )

with st.expander("Ver y descargar los datos"):
    st.write("Días marcados como N/E por serie:", faltantes)
    st.dataframe(df)
    st.download_button(
        "Descargar CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"sie_{'_'.join(claves)}_{inicio}_{fin}.csv",
        mime="text/csv",
    )
