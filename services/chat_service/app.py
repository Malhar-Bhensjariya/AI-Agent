from flask import Flask
from flask_cors import CORS
from .routes.chat_routes import chat_bp
from .routes.memory_routes import memory_bp
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(memory_bp, url_prefix='/memory')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)