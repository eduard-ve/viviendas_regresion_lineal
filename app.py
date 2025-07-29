import sys
import os
from controllers.vivienda_controller import ViviendaController
from flask import Flask, render_template, request, jsonify, url_for

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Configurar archivos estáticos
app.static_folder = 'static'
controller = ViviendaController()
datos_inicializados = False
datos_globales = None

@app.route('/')
def index(): # Página principal - Dashboard
    global datos_inicializados, datos_globales
    
    if not datos_inicializados:
        datos_globales = controller.inicializar_datos()
        datos_inicializados = True
    
    return render_template('dashboard.html', datos=datos_globales)

@app.route('/api/datos') #API obtener datos actualizados
def api_datos():
    global datos_globales
    
    if datos_globales:
        return jsonify(datos_globales)
    else:
        return jsonify({'error': 'Datos no inicializados'}), 500

@app.route('/api/tabla')
def api_tabla():
    limite = request.args.get('limite', 10, type=int)
    datos_tabla = controller.obtener_datos_tabla(limite)
    
    if datos_tabla:
        return jsonify({'datos': datos_tabla})
    else:
        return jsonify({'error': 'No se pudieron obtener los datos'}), 500

@app.route('/api/buscar')#API endpoint para buscar viviendas con filtros
def api_buscar():
    tipo_vivienda = request.args.get('tipo_vivienda')
    area_min = request.args.get('area_min', type=float)
    area_max = request.args.get('area_max', type=float)
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    
    resultados = controller.buscar_viviendas(
        tipo_vivienda=tipo_vivienda,
        area_min=area_min,
        area_max=area_max,
        precio_min=precio_min,
        precio_max=precio_max
    )
    
    if resultados is not None:
        return jsonify({'datos': resultados, 'total': len(resultados)})
    else:
        return jsonify({'error': 'No se pudieron buscar las viviendas'}), 500

@app.route('/api/actualizar')
def api_actualizar():
    global datos_inicializados, datos_globales
    
    try:
        controller_nuevo = ViviendaController()
        datos_globales = controller_nuevo.inicializar_datos()
        datos_inicializados = True
        
        return jsonify({'success': True, 'message': 'Datos actualizados correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)