from flask import Flask, request, jsonify, Response
from .controllers import upload_controller, file_controller
from dotenv import load_dotenv
import os
from .utils.preview_broadcaster import event_generator

load_dotenv()

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload():
    return upload_controller.handle_upload(request)


@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    return file_controller.get_file(file_id)


@app.route('/file/<file_id>/metadata', methods=['GET'])
def get_metadata(file_id):
    return file_controller.get_metadata(file_id)


@app.route('/file/<file_id>/preview', methods=['GET'])
def get_preview(file_id):
    return file_controller.get_preview(file_id)


@app.route('/stream/preview/<file_id>', methods=['GET'])
def stream_preview(file_id):
    """SSE endpoint to stream preview updates for a given file_id.
    Clients should connect with EventSource and listen for `message` events.
    """
    # Note: Production should consider authentication, rate-limiting, and
    # moving broadcast to an external pub/sub (Redis) for multi-process support.
    return Response(event_generator(file_id), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })


@app.route('/file/<file_id>', methods=['PUT'])
def put_file(file_id):
    return file_controller.overwrite_file(file_id, request)


@app.route('/file/<file_id>', methods=['PATCH'])
def patch_file(file_id):
    return file_controller.apply_op(file_id, request)


@app.route('/file/<file_id>/apply-op', methods=['POST'])
def apply_op(file_id):
    return file_controller.apply_op(file_id, request)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5010))
    app.run(host='0.0.0.0', port=port)
