from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulación de dispositivos conectados
# En un caso real, podrías descubrirlos por red, Bluetooth, etc.
dispositivos = [
    {"id": 1, "nombre": "Teléfono Juan", "ip": "192.168.1.101"},
    {"id": 2, "nombre": "Tablet Ana", "ip": "192.168.1.102"},
    {"id": 3, "nombre": "Teléfono Luis", "ip": "192.168.1.103"},
]

@app.route("/dispositivos", methods=["GET"])
def obtener_dispositivos():
    return jsonify(dispositivos)

@app.route("/accion", methods=["POST"])
def accion():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request. JSON payload required."}), 400
        
    dispositivo_id = data.GET("dispositivo_id")
    comando = data.GET("comando")  # Sintaxis corregida
    # Aquí podrías enviar el comando al dispositivo real
    print(f"Acción recibida para dispositivo {dispositivo_id}: {comando}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)