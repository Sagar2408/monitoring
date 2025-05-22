import eventlet
eventlet.monkey_patch()  # ✅ must be first

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)

# ✅ use eventlet mode for socketio
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# ---------------- Memory maps ----------------
trigger_map = {}
online_map = {}

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json()
    executive_id = str(data.get("executive_id"))
    online_map[executive_id] = True
    print(f"[💓] Heartbeat received from Executive {executive_id}")
    return jsonify({"status": "online"})

@app.route("/trigger-stream", methods=["POST"])
def trigger_stream():
    data = request.get_json()
    executive_id = str(data.get("executive_id"))
    stream = data.get("stream")
    trigger_map[executive_id] = stream
    print(f"[⚡] Admin triggered '{stream}' for Executive {executive_id}")
    return jsonify({"status": "triggered"})

@app.route("/should-start", methods=["GET"])
def should_start():
    executive_id = request.args.get("executive_id")
    stream = trigger_map.pop(executive_id, None)
    if stream:
        print(f"[🚀] EXEC {executive_id} START -> {stream}")
        return jsonify({"start": True, "stream": stream})
    return jsonify({"start": False})

@app.route("/", methods=["GET"])
def home():
    return "Flask Stream Trigger + Socket Server Running!"

# ---------------- Socket.IO events ----------------

@socketio.on("screen-data")
def handle_screen(data):
    executive_id = str(data.get("executiveId"))
    exec_name = str(data.get("executiveName"))
    image = data.get("image")
    emit("screen-data", {
        "executiveId": executive_id,
        "executiveName": exec_name,
        "image": image
    }, broadcast=True)
    print(f"[📺] screen-data from Exec {executive_id} ({exec_name}) broadcasted")

@socketio.on("video-data")
def handle_video(data):
    executive_id = str(data.get("executiveId"))
    exec_name = str(data.get("executiveName"))
    buffer = data.get("buffer")
    emit("video-data", {
        "executiveId": executive_id,
        "executiveName": exec_name,
        "buffer": buffer
    }, broadcast=True)
    print(f"[🎥] video-data from Exec {executive_id} ({exec_name}) broadcasted")

@socketio.on("audio-data")
def handle_audio(data):
    executive_id = str(data.get("executiveId"))
    exec_name = str(data.get("executiveName"))
    buffer = data.get("buffer")
    emit("audio-data", {
        "executiveId": executive_id,
        "executiveName": exec_name,
        "buffer": buffer
    }, broadcast=True)
    print(f"[🎙️] audio-data from Exec {executive_id} ({exec_name}) broadcasted")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
