from flask import Flask
from flask_cors import CORS
from .routes.visualization_routes import visualization_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(visualization_bp, url_prefix='/visualization')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=False)