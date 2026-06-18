from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Ukládáme aktivace jako seznam: {"group": 13, "timestamp": 1234567890.123}
activations = []

# Jak dlouho (v sekundách) si pamatujeme aktivace
RETENTION_SECONDS = 10

@app.route("/")
def home():
    return "Co-op Trigger Server běží!"

@app.route("/activate", methods=["POST"])
def activate():
    data = request.get_json()
    group = data.get("group")
    if group is None:
        return jsonify({"error": "missing group"}), 400

    activations.append({"group": group, "timestamp": time.time()})
    print(f"Aktivace přijata: group={group}")
    return jsonify({"status": "ok"})

@app.route("/poll", methods=["GET"])
def poll():
    # since = timestamp posledni aktivace kterou klient uz zpracoval
    since = float(request.args.get("since", 0))
    now = time.time()

    # Vycistime stare zaznamy
    global activations
    activations = [a for a in activations if now - a["timestamp"] < RETENTION_SECONDS]

    # Vratime jen nove aktivace
    new_activations = [a for a in activations if a["timestamp"] > since]

    return jsonify({
        "activations": new_activations,
        "server_time": now
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8765))
    app.run(host="0.0.0.0", port=port)
