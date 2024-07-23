from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
latest_frame = None

def generate():
    global latest_frame
    while True:
        if latest_frame is not None:
            yield (b'--BoundaryString\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        else:
            yield (b'--BoundaryString\r\n'
                   b'Content-Type: text/plain\r\n\r\nNo frame available\r\n')

@app.route('/upload', methods=['POST'])
def upload():
    global latest_frame
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    latest_frame = file.read()
    socketio.emit('frame', latest_frame.decode('latin-1'))
    return jsonify({'message': 'Frame received'}), 200

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=BoundaryString')

@app.route('/snapshot')
def snapshot():
    global latest_frame
    if latest_frame is None:
        return jsonify({'error': 'No frame available'}), 404
    return Response(latest_frame, mimetype='image/jpeg')

@socketio.on('connect')
def handle_connect():
    global latest_frame
    if latest_frame:
        emit('frame', latest_frame.decode('latin-1'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
