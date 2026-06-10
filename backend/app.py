import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from entities.simulador import Simulador

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/simular', methods=['POST'])
def simular():
    try:
        data = request.get_json()
        X = float(data['X'])
        i = int(data['i'])
        j = float(data['j'])
        params = data.get('params', {})

        if X <= 0 or i <= 0 or j < 0:
            return jsonify({'error': 'Valores inválidos en los parámetros.'}), 400

        # Creamos el simulador y lo ejecutamos
        simulador = Simulador(X, i, j, params)
        filas, columnas, metricas, clientes_por_fila = simulador.ejecutar()

        return jsonify({
            'columnas': columnas,
            'filas': filas,
            'metricas': metricas,
            'clientes_por_fila': clientes_por_fila
        })
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)