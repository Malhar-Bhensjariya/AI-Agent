import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from utils.file_handler import save_file, load_dataframe
from utils.analyzer import basic_analysis
from utils.langchain_agent import query_global, query_df
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static/plots'
app.config['VECTOR_STORE'] = 'vectorstore'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)
os.makedirs(app.config['VECTOR_STORE'], exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            logger.error('No file part in upload request')
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error('Empty filename in upload request')
            return jsonify({'error': 'Empty filename'}), 400

        filepath = save_file(file, app.config['UPLOAD_FOLDER'])
        logger.debug(f"File saved to: {filepath}")
        
        df = load_dataframe(filepath)
        logger.debug("Dataframe loaded successfully")
        
        return jsonify({
            **basic_analysis(df),
            'filename': os.path.basename(filepath),
            'status': 'success'
        })
        
    except Exception as e:
        logger.exception("Upload failed")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        logger.debug(f"Analysis request data: {data}")
        
        if not data or 'question' not in data:
            logger.error('Invalid analysis request format')
            return jsonify({'error': 'Missing question parameter'}), 400

        # Handle global analysis when no file
        if not data.get('filename'):
            logger.info("Handling global analysis request")
            result = query_global(data['question'])
            return jsonify(result)
        
        # File-based analysis
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
            
        df = load_dataframe(file_path)
        logger.debug("Dataframe loaded for analysis")
        
        result = query_df(df, data['question'], app.config['VECTOR_STORE'])
        return jsonify(result)
        
    except Exception as e:
        logger.exception("Analysis failed")
        return jsonify({'error': str(e)}), 500

@app.route('/plot/<filename>')
def serve_plot(filename):
    return send_file(os.path.join(app.config['STATIC_FOLDER'], filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)