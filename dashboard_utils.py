"""Funciones de análisis reutilizables para el dashboard."""
import numpy as np
import pandas as pd


def variaciones_diarias(valores: pd.Series) -> pd.Series:
    """Calcula variaciones porcentuales entre observaciones consecutivas."""
    serie = pd.to_numeric(pd.Series(valores), errors="coerce")
    cambios = serie.pct_change(fill_method=None) * 100
    cambios = cambios.replace([np.inf, -np.inf], np.nan)
    return cambios.dropna()


def volatilidad_anual(datos: pd.DataFrame) -> pd.Series:
    """Calcula la desviación estándar de las variaciones para cada año."""
    requeridas = {"Anio", "Variacion"}
    if not requeridas.issubset(datos.columns):
        raise ValueError("El DataFrame debe contener Anio y Variacion.")

    trabajo = datos[["Anio", "Variacion"]].copy()
    trabajo["Variacion"] = pd.to_numeric(
        trabajo["Variacion"], errors="coerce"
    ).replace([np.inf, -np.inf], np.nan)
    return trabajo.groupby("Anio")["Variacion"].std().dropna().sort_index()
