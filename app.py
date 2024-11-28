import os
import requests
import ffmpeg
from flask import Flask, request, jsonify

# Definir o diretório onde os arquivos convertidos serão salvos
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configurar o Flask para servir arquivos estáticos do diretório 'static'
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Função para baixar o arquivo via URL
def download_file(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return False

# Função para converter o arquivo usando ffmpeg
def convert_file(input_file, output_file, sample_rate=11025):
    try:
        ffmpeg.input(input_file).output(output_file, ar=sample_rate, ac=1).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        print(f"Erro na conversão: {e}")
        return False

# Endpoint para receber o URL do arquivo de áudio
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Receber a URL do arquivo via JSON
        data = request.json
        file_url = data.get('file_url')

        if not file_url:
            return jsonify({'message': 'URL do arquivo não fornecida', 'success': False}), 400
        
        # Nome do arquivo temporário para salvar o arquivo baixado
        temp_filename = 'temp_audio.mp3'
        converted_filename = os.path.join(UPLOAD_FOLDER, 'converted_audio.mp3')  # Salvar no diretório 'static/uploads'

        # Baixar o arquivo
        if download_file(file_url, temp_filename):
            print("Arquivo baixado com sucesso")

            # Converter o arquivo
            if convert_file(temp_filename, converted_filename):
                # Excluir o arquivo original após a conversão
                os.remove(temp_filename)
                
                # Retornar sucesso com a URL do arquivo convertido
                return jsonify({
                    'message': 'Arquivo convertido com sucesso',
                    'converted_file': f'/static/uploads/converted_audio.mp3',  # Caminho público do arquivo convertido
                    'success': True
                }), 200
            else:
                return jsonify({'message': 'Erro na conversão do arquivo', 'success': False}), 500
        else:
            return jsonify({'message': 'Erro ao baixar o arquivo', 'success': False}), 500
    except Exception as e:
        return jsonify({'message': f'Ocorreu um erro: {str(e)}', 'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True)
