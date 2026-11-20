# Herramientas de Visualización

Dashboard interactivo desarrollado con Python y Streamlit para consultar y visualizar datos del Sistema de Información Económica (SIE) de Banco de México.

## Funcionalidades

- Consulta de series económicas mediante la API REST de Banxico.
- Selección de claves y periodos.
- Indicadores estadísticos.
- Series temporales y medias móviles.
- Variaciones porcentuales mensuales.
- Diagramas de caja por año.
- Mapas de calor.
- Visualización y descarga de datos CSV.

## Requisitos

- Python 3.10 o superior.
- Token gratuito del SIE de Banxico.

## Instalación

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

## Configuración

Crear .streamlit/secrets.toml:

    banxico_token = "TU_TOKEN"

No compartir ni subir este archivo a GitHub.

Solicitar token:
https://www.banxico.org.mx/SieAPIRest/service/v1/token

## Ejecución

    .\.venv\Scripts\python.exe -m streamlit run dashboard_banxico.py

## Dependencias

- Streamlit
- Requests
- Pandas
- Matplotlib
- Seaborn

## Fuente

Banco de México. Sistema de Información Económica (SIE).
https://www.banxico.org.mx/SieAPIRest/
