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

        N = int(data['N'])
        X = float(data['X'])
        i = int(data['i'])
        j = float(data['j'])

        if N <= 0 or X <= 0 or i <= 0 or j < 0:
            return jsonify({'error': 'Todos los valores deben ser positivos y j debe ser mayor o igual a 0.'}), 400

        simulador = Simulador(N, X, i, j)
        filas, columnas = simulador.ejecutar()

        return jsonify({
            'columnas': columnas,
            'filas': filas
        })

    except KeyError as e:
        return jsonify({'error': f'Campo faltante: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
