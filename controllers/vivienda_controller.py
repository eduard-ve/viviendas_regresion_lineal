from models.data_model import ViviendaModel

class ViviendaController:
    """Controlador para manejar la lógica de negocio relacionada con las viviendas"""
    def __init__(self):
        self.model = ViviendaModel()
        self.datos_cargados = False
        
    def inicializar_datos(self, archivo_path='dataset_vivienda.xlsx'):
        resultados = {
            'tasa_cambio': None,
            'carga_datos': None,
            'estadisticas': None,
            'regresion': None,
            'graficos': {'dispersion': None, 'regresion': None}
        }
        
        resultados['tasa_cambio'] = self.model.obtener_tasa_cambio()
        resultados['carga_datos'] = self.model.cargar_datos(archivo_path)
        
        if resultados['carga_datos']['success']:
            self.datos_cargados = True
            # Obtener estadísticas
            resultados['estadisticas'] = self.model.obtener_estadisticas()
        
            # Entrenar modelo de regresión
            resultados['regresion'] = self.model.entrenar_modelo_regresion()
            
            # Generar gráficos
            resultados['graficos']['dispersion'] = self.model.generar_grafico_dispersion()
            resultados['graficos']['regresion'] = self.model.generar_grafico_regresion()
        
        return resultados
    
    def obtener_resumen_completo(self):
        """Obtiene un resumen completo de todos los datos procesados"""
        if not self.datos_cargados:
            return None
            
        return {
            'estadisticas': self.model.obtener_estadisticas(),
            'regresion': {
                'intercepto': self.model.modelo_regresion.intercept_,
                'pendiente': self.model.modelo_regresion.coef_[0],
                'score': self.model.modelo_regresion.score(
                    self.model.df[['area']], 
                    self.model.df['precio']
                )
            },
            'graficos': {
                'dispersion': self.model.generar_grafico_dispersion(),
                'regresion': self.model.generar_grafico_regresion()
            },
            'tasa_cambio': self.model.tasa_cambio_cop_a_usd
        }
    
    def obtener_datos_tabla(self, limite=10):
        """Obtiene una muestra de los datos para mostrar en tabla"""
        if not self.datos_cargados:
            return None
            
        # Seleccionar columnas 
        columnas_relevantes = ['area', 'precio', 'precio_USD', 'tipo_vivienda', 'descripcion']
        df_muestra = self.model.df[columnas_relevantes].head(limite)
        return df_muestra.to_dict('records')
    
    # Filtrar busqueda de viviendas
    def buscar_viviendas(self, tipo_vivienda=None, area_min=None, area_max=None, precio_min=None, precio_max=None):
        if not self.datos_cargados:
            return None
            
        df_filtrado = self.model.df.copy()
        
        if tipo_vivienda and tipo_vivienda != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['tipo_vivienda'] == tipo_vivienda]
            
        if area_min:
            df_filtrado = df_filtrado[df_filtrado['area'] >= area_min]
            
        if area_max:
            df_filtrado = df_filtrado[df_filtrado['area'] <= area_max]
            
        if precio_min:
            df_filtrado = df_filtrado[df_filtrado['precio'] >= precio_min]
            
        if precio_max:
            df_filtrado = df_filtrado[df_filtrado['precio'] <= precio_max]
        
        columnas_relevantes = ['area', 'precio', 'precio_USD', 'tipo_vivienda', 'descripcion']
        return df_filtrado[columnas_relevantes].to_dict('records')
    
