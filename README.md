# Dashboard Streamlit — API SIE de Banxico

Implementación reproducible de un panel interactivo que consume datos reales de la API REST de Banco de México (SIE). Incluye indicadores, cinco visualizaciones (serie y media móvil; variación; histograma; boxplot; volatilidad), comparación base 100, filtros y exportación CSV.

**Origen:** adaptación propuesta para la tarea de visualización relacionada con https://github.com/AxMrls/HerramientasVisualizacion. Este paquete no afirma haber sido publicado en ese repositorio.

## Ejecutar en Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
notepad .streamlit\secrets.toml
.\.venv\Scripts\python.exe -m streamlit run dashboard_banxico.py
```

Sustituir `PON_AQUI_TU_TOKEN_PERSONAL` por el token obtenido en https://www.banxico.org.mx/SieAPIRest/service/v1/token. El archivo `secrets.toml` **nunca** se sube a GitHub. Alternativa: usar variable de entorno `BANXICO_TOKEN`.

## Evidencia real

1. Inicia la aplicación y confirma que muestra datos sin errores; requiere conexión y token Banxico válido.
2. Abre http://localhost:8501 y toma capturas con `Win + Shift + S`, o graba la ventana con `Win + Alt + R`.
3. Guarda capturas en `evidencias/` con nombres `01_panel.png`, `02_graficas.png`, `03_descarga.png`; deben mostrar el funcionamiento real, no simulaciones.
4. Ejecuta `git status`, agrega cambios con `git add .`, crea commit con `git commit -m "feat: dashboard SIE en Streamlit"`, y publica con `git push`. Necesitas permiso de escritura en el repositorio destino; si no lo tienes, usa tu fork o pide acceso al propietario.

## Seguridad y reproducibilidad

Token excluido por `.gitignore`; caché con TTL de una hora; peticiones HTTP con timeout; valores no numéricos tratados como faltantes; protección ante división por cero.
