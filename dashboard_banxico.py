"""Dashboard de indicadores del SIE Banxico. Ejecutar: streamlit run dashboard_banxico.py"""
import os
from datetime import date
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px

API = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series'

def token_configurado():
    try:
        if st.secrets.get('banxico_token'):
            return str(st.secrets['banxico_token']).strip()
    except Exception:
        pass
    return os.environ.get('BANXICO_TOKEN', '').strip()

@st.cache_data(ttl=3600, show_spinner=False)
def consultar_series(claves: tuple[str, ...], inicio: str, fin: str, token: str):
    respuesta = requests.get(
        f"{API}/{','.join(claves)}/datos/{inicio}/{fin}",
        headers={'Bmx-Token': token, 'Accept': 'application/json'}, timeout=30,
    )
    respuesta.raise_for_status()
    series = respuesta.json().get('bmx', {}).get('series', [])
    filas = []
    for s in series:
        clave = s.get('idSerie', '')
        titulo = s.get('titulo', clave)
        for x in s.get('datos', []):
            valor = str(x.get('dato', '')).replace(',', '')
            filas.append({'Fecha': x.get('fecha'), 'Valor': valor, 'Clave': clave, 'Serie': titulo})
    if not filas:
        return pd.DataFrame(columns=['Fecha', 'Valor', 'Clave', 'Serie'])
    df = pd.DataFrame(filas)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    return df.dropna(subset=['Fecha']).sort_values(['Clave', 'Fecha'])

def calculos(df):
    tmp = df.dropna(subset=['Valor']).copy().sort_values(['Clave', 'Fecha'])
    if tmp.empty:
        return tmp
    tmp['Variación %'] = tmp.groupby('Clave')['Valor'].pct_change(fill_method=None) * 100
    tmp['Variación %'] = tmp['Variación %'].replace([np.inf, -np.inf], np.nan)
    tmp['Media móvil'] = tmp.groupby('Clave')['Valor'].transform(lambda s: s.rolling(7, min_periods=1).mean())
    tmp['Año'] = tmp['Fecha'].dt.year
    return tmp

st.set_page_config(page_title='Indicadores Banxico · SIE', page_icon='📊', layout='wide')
st.title('📊 Indicadores económicos — Banco de México')
st.caption('Dashboard conectado a la API pública del Sistema de Información Económica (SIE).')
with st.sidebar:
    st.header('Consulta')
    claves_texto = st.text_input('Claves (separadas por coma)', value='SF43718')
    inicio = st.date_input('Fecha inicial', value=date(2024, 1, 1))
    fin = st.date_input('Fecha final', value=date.today())
    token = token_configurado()
    st.caption('Configura BANXICO_TOKEN o .streamlit/secrets.toml; nunca publiques el token.')
claves = tuple(dict.fromkeys(c.strip().upper() for c in claves_texto.split(',') if c.strip()))
if not claves or len(claves) > 5:
    st.warning('Introduce entre 1 y 5 claves de series.'); st.stop()
if inicio > fin:
    st.error('La fecha inicial no puede superar la fecha final.'); st.stop()
if not token:
    st.info('Falta configurar el token gratuito de la API SIE de Banxico.'); st.stop()
try:
    with st.spinner('Consultando el SIE...'):
        datos = consultar_series(claves, inicio.isoformat(), fin.isoformat(), token)
except requests.HTTPError as e:
    st.error(f'La API devolvió un error HTTP: {e}'); st.stop()
except (requests.RequestException, ValueError, KeyError) as e:
    st.error(f'No se pudo consultar o procesar la respuesta: {e}'); st.stop()
trabajo = calculos(datos)
if trabajo.empty:
    st.warning('No se encontraron observaciones numéricas en el periodo.'); st.stop()
seleccion = st.selectbox('Serie principal', list(trabajo['Clave'].unique()))
principal = trabajo[trabajo['Clave'] == seleccion]
actual, previo = principal['Valor'].iloc[-1], principal['Valor'].iloc[0]
a,b,c,d = st.columns(4)
a.metric('Observaciones', f'{len(principal):,}')
b.metric('Último valor', f'{actual:,.4f}')
c.metric('Cambio acumulado', f'{((actual/previo)-1)*100:+.2f} %' if previo else 'N/D')
d.metric('Valor máximo', f"{principal['Valor'].max():,.4f}")
st.subheader('Evolución temporal y media móvil (7 observaciones)')
graf = px.line(principal, x='Fecha', y=['Valor', 'Media móvil'], labels={'value':'Valor','variable':'Serie'})
st.plotly_chart(graf, use_container_width=True)
izq, der = st.columns(2)
with izq:
    st.subheader('Variación porcentual')
    fig = px.bar(principal.dropna(subset=['Variación %']), x='Fecha', y='Variación %')
    st.plotly_chart(fig, use_container_width=True)
with der:
    st.subheader('Distribución de variaciones')
    fig = px.histogram(principal.dropna(subset=['Variación %']), x='Variación %', nbins=50)
    st.plotly_chart(fig, use_container_width=True)
izq, der = st.columns(2)
with izq:
    st.subheader('Variabilidad por año')
    fig = px.box(principal.dropna(subset=['Variación %']), x='Año', y='Variación %')
    st.plotly_chart(fig, use_container_width=True)
with der:
    st.subheader('Volatilidad anual')
    vola = principal.groupby('Año', as_index=False)['Variación %'].std().dropna()
    fig = px.bar(vola, x='Año', y='Variación %', labels={'Variación %':'Desviación estándar (%)'})
    st.plotly_chart(fig, use_container_width=True)
if len(claves)>1:
    st.subheader('Comparación de series (base 100)')
    comparacion = trabajo.copy()
    comparacion['Base 100'] = comparacion.groupby('Clave')['Valor'].transform(lambda x: (x/x.iloc[0]*100) if x.iloc[0] else np.nan)
    st.plotly_chart(px.line(comparacion, x='Fecha', y='Base 100', color='Clave'), use_container_width=True)
with st.expander('Datos y descarga'):
    st.dataframe(datos, use_container_width=True)
    st.download_button('Descargar datos CSV', datos.to_csv(index=False).encode('utf-8'), 'banxico_datos.csv', 'text/csv')
st.caption('Fuente: Banco de México, SIE. Los valores se obtienen de la API al consultar, no son datos simulados.')
