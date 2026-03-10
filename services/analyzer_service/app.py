from flask import Flask
from flask_cors import CORS
from .routes.analyzer_routes import analyzer_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(analyzer_bp, url_prefix='/analyzer')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)