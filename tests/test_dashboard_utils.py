import unittest

import pandas as pd

from dashboard_utils import variaciones_diarias, volatilidad_anual


class VariacionesDiariasTests(unittest.TestCase):
    def test_calcula_cambios_porcentuales(self):
        resultado = variaciones_diarias(pd.Series([100, 110, 99]))
        self.assertEqual(len(resultado), 2)
        self.assertAlmostEqual(resultado.iloc[0], 10.0, places=8)
        self.assertAlmostEqual(resultado.iloc[1], -10.0, places=8)

    def test_ignora_el_primer_valor(self):
        resultado = variaciones_diarias(pd.Series([50]))
        self.assertTrue(resultado.empty)

    def test_descarta_resultados_infinitos(self):
        resultado = variaciones_diarias(pd.Series([0, 10, 20]))
        self.assertEqual(len(resultado), 1)
        self.assertAlmostEqual(resultado.iloc[0], 100.0, places=8)

    def test_descarta_datos_faltantes(self):
        resultado = variaciones_diarias(pd.Series([100, None, 110]))
        self.assertTrue(resultado.empty)


class VolatilidadAnualTests(unittest.TestCase):
    def test_calcula_desviacion_estandar_por_anio(self):
        datos = pd.DataFrame({
            "Anio": [2024, 2024, 2025, 2025, 2025],
            "Variacion": [1.0, 3.0, 2.0, 4.0, 6.0],
        })
        resultado = volatilidad_anual(datos)
        self.assertEqual(list(resultado.index), [2024, 2025])
        self.assertAlmostEqual(resultado.loc[2024], 2 ** 0.5, places=8)
        self.assertAlmostEqual(resultado.loc[2025], 2.0, places=8)

    def test_descarta_valores_invalidos_y_anios_sin_muestra_suficiente(self):
        datos = pd.DataFrame({
            "Anio": [2024, 2024, 2025, 2025],
            "Variacion": [1.0, 3.0, float("inf"), None],
        })
        resultado = volatilidad_anual(datos)
        self.assertEqual(list(resultado.index), [2024])


if __name__ == "__main__":
    unittest.main()
