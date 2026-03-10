from flask import Flask
from flask_cors import CORS
from .routes.auth_routes import auth_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5006))
    app.run(host='0.0.0.0', port=port, debug=False)