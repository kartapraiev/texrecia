import os
import subprocess
import uuid
from flask import Flask, request, render_template, jsonify

# Inicializa a aplicação Flask
app = Flask(__name__)
# Define a pasta para uploads temporários
UPLOAD_FOLDER = 'uploads'
# Garante que a pasta de uploads exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """ Rota principal que renderiza a página de upload (index.html). """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """ Rota que recebe o arquivo PDF, executa a análise e retorna o resultado. """
    # Verifica se um arquivo foi enviado na requisição
    if 'pdfFile' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    
    file = request.files['pdfFile']
    
    # Verifica se o nome do arquivo está vazio
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido."}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            # Cria um nome de arquivo único para evitar conflitos
            temp_filename = str(uuid.uuid4()) + ".pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            
            # Salva o arquivo temporariamente
            file.save(filepath)
            
            # Executa o script main.py como um processo separado, passando o caminho do arquivo
            # Usamos sys.executable para garantir que estamos usando o mesmo interpretador Python
            result = subprocess.run(
                [
                    "python",
                    'main.py',
                    filepath
                ],
                capture_output=True,
                text=True,
                encoding='utf-8' # Garante a decodificação correta da saída
            )
            
            # Remove o arquivo temporário após a análise
            os.remove(filepath)
            
            # Verifica se o script executou com erro
            if result.returncode != 0:
                # Retorna o erro do script para o frontend
                error_message = result.stderr or "Ocorreu um erro desconhecido durante a análise."
                return jsonify({"error": error_message}), 500

            # Retorna a saída padrão do script (o relatório)
            return jsonify({"report": result.stdout})

        except Exception as e:
            # Garante que, em caso de erro no servidor, o arquivo seja removido se existir
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Ocorreu um erro interno no servidor: {str(e)}"}), 500
    else:
        return jsonify({"error": "Formato de arquivo inválido. Por favor, envie um PDF."}), 400

if __name__ == '__main__':
    # Executa a aplicação em modo de depuração para facilitar o desenvolvimento
    app.run(debug=True)