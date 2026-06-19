from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

# Uložené aktivace: seznam {"group": int, "timestamp": float, "sender_id": str}
activations = []
lock = threading.Lock()

# Jak dlouho (v sekundách) zůstává aktivace "platná" pro polling
ACTIVATION_LIFETIME = 5.0


@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json()
    if not data or "group" not in data:
        return jsonify({"error": "missing group"}), 400

    group = data["group"]
    sender_id = data.get("sender_id", "unknown")

    with lock:
        activations.append({
            "group": group,
            "timestamp": time.time(),
            "sender_id": sender_id
        })
        cutoff = time.time() - ACTIVATION_LIFETIME
        activations[:] = [a for a in activations if a["timestamp"] > cutoff]

    print(f"[Server] Aktivace skupiny {group} od {sender_id}")
    return jsonify({"status": "ok"})


@app.route("/poll", methods=["GET"])
def poll():
    since = float(request.args.get("since", 0))
    sender_id = request.args.get("sender_id", "")

    with lock:
        new_activations = [
            a for a in activations
            if a["timestamp"] > since and a["sender_id"] != sender_id
        ]

    return jsonify({
        "activations": new_activations,
        "server_time": time.time()
    })


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running", "active_count": len(activations)})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
