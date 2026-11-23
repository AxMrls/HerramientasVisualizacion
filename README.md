# Herramientas de Visualización

Dashboard interactivo desarrollado con Python y Streamlit para consultar y visualizar datos del Sistema de Información Económica (SIE) del Banco de México.

## Funcionalidades

- Consulta de series económicas mediante la API REST de Banxico.
- Selección de claves y periodos.
- Indicadores estadísticos del periodo consultado.
- Serie temporal y media móvil.
- Comparación de varias series en base 100.
- Variaciones porcentuales mensuales.
- Diagrama de caja (Boxplot) de variaciones por año.
- Histograma de distribución de variaciones porcentuales.
- Comparación de volatilidad anual mediante desviación estándar.
- Visualización y descarga de datos CSV.

## Repositorio base consultado

La implementación parte del código de:
https://github.com/BOWadapter/HerramientasVisualizacion

Se verificó que `dashboard_banxico.py` y `requirements.txt` tienen el mismo
SHA de archivo en el repositorio base y en el repositorio del estudiante.
El detalle de la comparación se encuentra en `evidencias/origen_base.txt`.

## Cambio realizado en la práctica

Se retiró el mapa de calor de promedios mensuales por año y se incorporó un histograma de variaciones porcentuales entre observaciones consecutivas. Además, para cumplir con el requisito de cinco gráficas, se añadió una comparación de volatilidad anual mediante la desviación estándar de las variaciones.

El histograma permite observar la frecuencia de los cambios, identificar dónde se concentran los valores y comparar la media con la mediana. El gráfico de volatilidad anual permite comparar la variabilidad de los cambios entre años. Se conserva el Boxplot porque aporta una lectura complementaria de dispersión y valores atípicos por año.

## Requisitos

- Python 3.10 o superior.
- Token gratuito del SIE de Banxico.

## Instalación

### Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Configuración del token

Crea la carpeta `.streamlit` y dentro el archivo `secrets.toml`:

```toml
banxico_token = "TU_TOKEN"
```

También se admite la variable de entorno `BANXICO_TOKEN`.

**No compartas ni subas `secrets.toml` a GitHub.**

Solicitar token:
https://www.banxico.org.mx/SieAPIRest/service/v1/token

## Ejecución

### Windows

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard_banxico.py
```

### Linux

```bash
.venv/bin/python -m streamlit run dashboard_banxico.py
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

Las pruebas verifican el cálculo de variaciones porcentuales, el tratamiento del primer dato, los valores infinitos y los datos faltantes.

## Dependencias

- Streamlit
- Requests
- Pandas
- NumPy
- Matplotlib
- Seaborn

## Fuente de datos

Banco de México. Sistema de Información Económica (SIE).
https://www.banxico.org.mx/SieAPIRest/
