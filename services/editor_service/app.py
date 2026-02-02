from flask import Flask
from flask_cors import CORS
from .routes.editor_routes import editor_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(editor_bp, url_prefix='/editor')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)