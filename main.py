from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple in-memory trigger map
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
    return "Flask Stream Trigger Server Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)