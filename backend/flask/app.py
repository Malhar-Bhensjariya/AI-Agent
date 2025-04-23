from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from utils.file_handler import save_file, load_dataframe
from utils.analyzer import basic_analysis
from utils.langchain_agent import query_df
import os

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['STATIC_FOLDER'] = 'static/plots'

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        filepath = save_file(file)
        df = load_dataframe(filepath)
        return jsonify({
            **basic_analysis(df),
            'filename': os.path.basename(filepath)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    required_fields = ['filename', 'question']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        df = load_dataframe(f"uploads/{data['filename']}")
        result = query_df(df, data['question'])
        
        if result['type'] == 'plot':
            return jsonify({
                'answer': result.get('caption', ''),
                'plot_url': f"/plot/{result['plot_path']}"
            })
        elif result['type'] == 'error':
            return jsonify({'error': result['message']}), 400
        else:
            return jsonify({'answer': result['content']})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/plot/<filename>')
def serve_plot(filename):
    return send_file(f"static/plots/{filename}", mimetype='image/png')

if __name__ == '__main__':
    os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)