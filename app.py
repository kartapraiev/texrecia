import os
import subprocess
import uuid
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'pdfFile' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    
    file = request.files['pdfFile']
    
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido."}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            temp_filename = str(uuid.uuid4()) + ".pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            
            file.save(filepath)
            
            result = subprocess.run(
                [
                    "python",
                    'main.py',
                    filepath
                ],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            os.remove(filepath)
            
            if result.returncode != 0:
                error_message = result.stderr or "Ocorreu um erro desconhecido durante a análise."
                return jsonify({"error": error_message}), 500

            return jsonify({"report": result.stdout})

        except Exception as e:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Ocorreu um erro interno no servidor: {str(e)}"}), 500
    else:
        return jsonify({"error": "Formato de arquivo inválido. Por favor, envie um PDF."}), 400

if __name__ == '__main__':
    app.run(debug=True)