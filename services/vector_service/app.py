from flask import Flask, request, jsonify
from .ingest import handle_ingest
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


@app.route('/ingest', methods=['POST'])
def ingest():
    return handle_ingest(request)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5020))
    app.run(host='0.0.0.0', port=port)
