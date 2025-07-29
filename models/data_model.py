import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

class ViviendaModel:
    def __init__(self):
        self.df = None
        self.tasa_cambio_cop_a_usd = None
        self.modelo_regresion = None
        
    def obtener_tasa_cambio(self):
        api_url = "https://open.er-api.com/v6/latest/USD"
        
        try:
            respuesta = requests.get(api_url)
            if respuesta.status_code == 200:#No responde
                datos = respuesta.json()
                self.tasa_cambio_cop_a_usd = 1 / datos['rates']['COP']
                return {
                    'success': True,
                    'tasa_usd_cop': datos['rates']['COP'],
                    'tasa_cop_usd': self.tasa_cambio_cop_a_usd
                }
            else:
                # Tasa de respaldo caso1
                self.tasa_cambio_cop_a_usd = 0.00025
                return {
                    'success': False,
                    'message': f"Error API: {respuesta.status_code}",
                    'tasa_cop_usd': self.tasa_cambio_cop_a_usd
                }
        except requests.exceptions.RequestException as e:
            # Tasa de respaldo caso2
            self.tasa_cambio_cop_a_usd = 0.00025
            return {
                'success': False,
                'message': f"Error de conexión: {str(e)}",
                'tasa_cop_usd': self.tasa_cambio_cop_a_usd
            }
    
    def cargar_datos(self, archivo_path='dataset_vivienda.xlsx'):# Cargar los datos
        try:
            self.df = pd.read_excel(archivo_path)
            self.df.columns = self.df.columns.str.lower().str.strip()
            
            # Procesar descripción
            self.df['descripcion'] = self.df['descripcion'].astype(str)
            self.df['descripcion'] = self.df['descripcion'].apply(
                lambda x: x.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore') 
                if isinstance(x, str) else x
            )
            
            # Clasificar tipo de vivienda
            self.df['tipo_vivienda'] = np.where(
                self.df['descripcion'].str.contains('apartamento|Apartamento', case=False, na=False), 
                'Apartamento',
                np.where(
                    self.df['descripcion'].str.contains('casa|Casa', case=False, na=False), 
                    'Casa', 
                    'Otro'
                )
            )
            
            # Crear columna precio en USD-Dolares
            if self.tasa_cambio_cop_a_usd:
                self.df['precio_USD'] = self.df['precio'] * self.tasa_cambio_cop_a_usd
            
            return {'success': True, 'message': 'Datos cargados correctamente'}
            
        except FileNotFoundError:
            return {'success': False, 'message': 'Archivo no encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def obtener_estadisticas(self):
        if self.df is None:
            return None
            
        total_viviendas = len(self.df)
        promedio_precio_m2_COP = (self.df['precio'] / self.df['area']).mean()
        clasificacion_viviendas = self.df['tipo_vivienda'].value_counts().to_dict()
        
        return {
            'total_viviendas': total_viviendas,
            'promedio_precio_m2_COP': promedio_precio_m2_COP,
            'clasificacion_viviendas': clasificacion_viviendas
        }
    
    def entrenar_modelo_regresion(self):
        if self.df is None:
            return None
            
        X = self.df[['area']]
        y = self.df['precio']
        
        self.modelo_regresion = LinearRegression()
        self.modelo_regresion.fit(X, y)
        
        return {
            'intercepto': self.modelo_regresion.intercept_,
            'pendiente': self.modelo_regresion.coef_[0],
            'score': self.modelo_regresion.score(X, y)
        }
    
    def generar_grafico_dispersion(self):
        if self.df is None:
            return None
            
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='area', y='precio', hue='tipo_vivienda', data=self.df)
        plt.title('Relación entre Área y Precio (COP) por Tipo de Vivienda')
        plt.xlabel('Área (metros cuadrados)')
        plt.ylabel('Precio (Pesos Colombianos - COP)')
        plt.grid(True)
        plt.legend(title='Tipo de Vivienda')
        
        # Convertir a base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return graph_url
    
    def generar_grafico_regresion(self):
        if self.df is None or self.modelo_regresion is None:
            return None
            
        plt.figure(figsize=(10, 6))
        X = self.df[['area']]
        
        sns.scatterplot(x='area', y='precio', data=self.df, label='Datos Reales')
        plt.plot(X, self.modelo_regresion.predict(X), color='red', linewidth=2, label='Línea de Regresión')
        plt.title('Regresión Lineal: Área vs. Precio (COP)')
        plt.xlabel('Área (metros cuadrados)')
        plt.ylabel('Precio (Pesos Colombianos - COP)')
        plt.grid(True)
        plt.legend()
        
        # Convertir a base64
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return graph_url