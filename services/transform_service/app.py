from flask import Flask
from flask_cors import CORS
from .routes.transform_routes import transform_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(transform_bp, url_prefix='/transform')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)