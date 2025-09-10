from flask import Flask, request, jsonify
import time
import pyautogui
import threading
import socket

app = Flask(__name__)

# Lista dinámica de dispositivos disponibles (no conectados)
dispositivos_disponibles = {}
# Lista de dispositivos conectados (autorizados)
dispositivos_conectados = {}
# Solicitudes de conexión pendientes
solicitudes_pendientes = {}

# Configurar pyautogui
# pyautogui.FAILSAFE = False  # Comentado para evitar error de tipo

def get_local_ip() -> str:
    """Obtiene la IP local (LAN) de esta máquina."""
    ip = "127.0.0.1"
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No necesita ser accesible, sólo fuerza a elegir la interfaz de salida
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        pass
    finally:
        try:
            if s:
                s.close()
        except Exception:
            pass
    return ip

@app.route("/health", methods=["GET"])
def health():
    """Salud del servidor y su IP LAN detectada."""
    return jsonify({"status": "ok", "server_ip": get_local_ip()}), 200

@app.route("/dispositivos", methods=["GET"])
def obtener_dispositivos():
    # Devolver dispositivos conectados y autorizados
    return jsonify(list(dispositivos_conectados.values()))

@app.route("/dispositivos_disponibles", methods=["GET"])
def obtener_dispositivos_disponibles():
    # Devolver dispositivos disponibles (no conectados aún)
    return jsonify(list(dispositivos_disponibles.values()))

@app.route("/obtener_ip_cliente", methods=["GET"])
def obtener_ip_cliente():
    """Endpoint para que el cliente móvil obtenga su IP real"""
    # Obtener la IP del cliente desde la request
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR') or 'unknown'
    
    # Si hay múltiples IPs (proxies), tomar la primera
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    return jsonify({"ip": client_ip})

@app.route("/publicar", methods=["POST"])
def publicar_dispositivo():
    """Endpoint para que dispositivos móviles publiquen su disponibilidad"""
    data = request.json
    if not data or "nombre" not in data or "ip" not in data:
        return jsonify({"error": "Se requiere nombre e IP del dispositivo."}), 400

    ip = data["ip"]
    dispositivos_disponibles[ip] = {
        "nombre": data["nombre"],
        "ip": ip,
        "timestamp": time.time(),
        "tipo": "mobile"
    }
    print(f"Dispositivo móvil disponible: {data['nombre']} en la IP {ip}")
    return jsonify({"status": "ok", "message": f"Dispositivo {data['nombre']} publicado."})

@app.route("/solicitar_conexion", methods=["POST"])
def solicitar_conexion():
    """Endpoint para solicitar conexión a un dispositivo móvil"""
    data = request.json
    if not data or "ip_destino" not in data:
        return jsonify({"error": "Se requiere IP del dispositivo destino."}), 400
    
    ip_destino = data["ip_destino"]
    if ip_destino not in dispositivos_disponibles:
        return jsonify({"error": "Dispositivo no disponible."}), 404
    
    # Crear solicitud pendiente
    solicitud_id = f"req_{int(time.time())}"
    solicitudes_pendientes[solicitud_id] = {
        "ip_destino": ip_destino,
        "timestamp": time.time(),
        "estado": "pendiente"
    }
    
    print(f"Solicitud de conexión enviada a {ip_destino}")
    return jsonify({"status": "ok", "solicitud_id": solicitud_id})

@app.route("/verificar_solicitudes", methods=["GET"])
def verificar_solicitudes():
    """Endpoint para que dispositivos móviles verifiquen si hay solicitudes de conexión"""
    ip_cliente = request.remote_addr
    
    # Buscar solicitudes pendientes para esta IP
    solicitudes = []
    for solicitud_id, solicitud in solicitudes_pendientes.items():
        if solicitud["ip_destino"] == ip_cliente and solicitud["estado"] == "pendiente":
            solicitudes.append({
                "solicitud_id": solicitud_id,
                "timestamp": solicitud["timestamp"]
            })
    
    return jsonify({"solicitudes": solicitudes})

@app.route("/responder_solicitud", methods=["POST"])
def responder_solicitud():
    """Endpoint para que dispositivos móviles respondan a solicitudes de conexión"""
    data = request.json
    if not data or "solicitud_id" not in data or "aceptar" not in data:
        return jsonify({"error": "Se requiere solicitud_id y aceptar (true/false)."}), 400
    
    solicitud_id = data["solicitud_id"]
    aceptar = data["aceptar"]
    
    if solicitud_id not in solicitudes_pendientes:
        return jsonify({"error": "Solicitud no encontrada."}), 404
    
    solicitud = solicitudes_pendientes[solicitud_id]
    ip_dispositivo = solicitud["ip_destino"]
    
    if aceptar:
        # Mover dispositivo de disponible a conectado
        if ip_dispositivo in dispositivos_disponibles:
            dispositivo = dispositivos_disponibles[ip_dispositivo]
            dispositivos_conectados[ip_dispositivo] = dispositivo
            del dispositivos_disponibles[ip_dispositivo]
            print(f"Dispositivo {dispositivo['nombre']} conectado exitosamente")
        
        solicitud["estado"] = "aceptada"
        return jsonify({"status": "ok", "message": "Conexión autorizada"})
    else:
        solicitud["estado"] = "rechazada"
        return jsonify({"status": "ok", "message": "Conexión rechazada"})

@app.route("/register", methods=["POST"])
def registrar_dispositivo():
    """Endpoint legacy - redirigir a publicar"""
    return publicar_dispositivo()

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    if not data or "command" not in data:
        return jsonify({"error": "Se requiere comando."}), 400

    command = data["command"]
    command_data = data.get("data", {})
    
    try:
        if command == "left_click":
            pyautogui.click()
        elif command == "right_click":
            pyautogui.rightClick()
        elif command == "mouse_move":
            deltaX = command_data.get("deltaX", 0)
            deltaY = command_data.get("deltaY", 0)
            pyautogui.moveRel(deltaX, deltaY)
        elif command == "key_press":
            key = command_data.get("key")
            if key in ['up', 'down', 'left', 'right']:
                pyautogui.press(key)
        else:
            return jsonify({"error": "Comando no reconocido."}), 400
            
        print(f"Comando ejecutado: {command}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/comando", methods=["POST"])
def comando():
    data = request.json
    if not data or "comando" not in data:
        return jsonify({"error": "Se requiere comando."}), 400

    comando = data["comando"]
    datos = data.get("datos", {})
    
    try:
        # Comandos de mouse
        if comando == "left_click":
            pyautogui.click()
        elif comando == "right_click":
            pyautogui.rightClick()
        elif comando == "mouse_move":
            deltaX = datos.get("deltaX", 0)
            deltaY = datos.get("deltaY", 0)
            pyautogui.moveRel(deltaX, deltaY)
        elif comando == "scroll":
            direction = datos.get("direction", "up")
            scroll_amount = 3 if direction == "up" else -3
            pyautogui.scroll(scroll_amount)
            
        # Comandos de teclado
        elif comando == "arrow_key":
            direction = datos.get("direction")
            if direction in ['up', 'down', 'left', 'right']:
                pyautogui.press(direction)
        elif comando == "special_key":
            key = datos.get("key")
            if key == "escape":
                pyautogui.press('esc')
            elif key == "tab":
                pyautogui.press('tab')
            elif key == "enter":
                pyautogui.press('enter')
            elif key == "space":
                pyautogui.press('space')
            elif key == "alt_tab":
                pyautogui.hotkey('alt', 'tab')
            elif key == "win_key":
                pyautogui.press('win')
            elif key == "ctrl_c":
                pyautogui.hotkey('ctrl', 'c')
            elif key == "ctrl_v":
                pyautogui.hotkey('ctrl', 'v')
        elif comando == "key_press":
            key = datos.get("key")
            if key in ['up', 'down', 'left', 'right']:
                pyautogui.press(key)
        else:
            return jsonify({"error": "Comando no reconocido."}), 400
            
        print(f"Comando ejecutado: {comando}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/accion", methods=["POST"])
def accion():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request. JSON payload required."}), 400
        
    dispositivo_id = data.get("dispositivo_id")
    comando = data.get("comando")
    # Aquí podrías enviar el comando al dispositivo real
    print(f"Acción recibida para dispositivo {dispositivo_id}: {comando}")
    return jsonify({"status": "ok"})

@app.route("/desconectar", methods=["POST"])
def desconectar_dispositivo():
    """Endpoint para desconectar un dispositivo y liberarlo para nueva conexión"""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request. JSON payload required."}), 400
    
    dispositivo_ip = data.get("ip")
    dispositivo_nombre = data.get("nombre")
    
    if not dispositivo_ip:
        return jsonify({"error": "IP del dispositivo requerida."}), 400
    
    # Buscar el dispositivo en conectados y moverlo de vuelta a disponibles
    dispositivo_encontrado = None
    for device_id, device in list(dispositivos_conectados.items()):
        if device.get("ip") == dispositivo_ip or device.get("nombre") == dispositivo_nombre:
            dispositivo_encontrado = device
            del dispositivos_conectados[device_id]
            break
    
    if dispositivo_encontrado:
        # Mover el dispositivo de vuelta a disponibles con nuevo timestamp
        nuevo_id = f"device_{len(dispositivos_disponibles) + 1}_{int(time.time())}"
        dispositivos_disponibles[nuevo_id] = {
            "id": nuevo_id,
            "nombre": dispositivo_encontrado["nombre"],
            "ip": dispositivo_encontrado["ip"],
            "timestamp": time.time()
        }
        
        print(f"Dispositivo desconectado: {dispositivo_encontrado['nombre']} ({dispositivo_encontrado['ip']})")
        return jsonify({"status": "ok", "message": "Dispositivo desconectado exitosamente"})
    else:
        # Si no se encuentra en conectados, asegurar que esté en disponibles
        print(f"Dispositivo no encontrado en conectados, liberando IP: {dispositivo_ip}")
        return jsonify({"status": "ok", "message": "Dispositivo liberado"})

@app.route("/limpiar_dispositivos", methods=["POST"])
def limpiar_dispositivos():
    """Endpoint para limpiar todos los dispositivos y reiniciar el estado"""
    global dispositivos_disponibles, dispositivos_conectados, solicitudes_pendientes
    
    dispositivos_disponibles.clear()
    dispositivos_conectados.clear()
    solicitudes_pendientes.clear()
    
    print("Todos los dispositivos han sido limpiados del servidor")
    return jsonify({"status": "ok", "message": "Dispositivos limpiados exitosamente"})

@app.route("/reiniciar_dispositivo", methods=["POST"])
def reiniciar_dispositivo():
    """Endpoint para que un dispositivo se reinicie y vuelva al estado inicial"""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request. JSON payload required."}), 400
    
    dispositivo_ip = data.get("ip")
    dispositivo_nombre = data.get("nombre")
    
    # Remover de todas las listas
    for device_id, device in list(dispositivos_conectados.items()):
        if device.get("ip") == dispositivo_ip or device.get("nombre") == dispositivo_nombre:
            del dispositivos_conectados[device_id]
            break
    
    for device_id, device in list(dispositivos_disponibles.items()):
        if device.get("ip") == dispositivo_ip or device.get("nombre") == dispositivo_nombre:
            del dispositivos_disponibles[device_id]
            break
    
    # Limpiar solicitudes pendientes relacionadas
    for solicitud_id, solicitud in list(solicitudes_pendientes.items()):
        if solicitud.get("ip_destino") == dispositivo_ip:
            del solicitudes_pendientes[solicitud_id]
    
    print(f"Dispositivo reiniciado: {dispositivo_nombre} ({dispositivo_ip})")
    return jsonify({"status": "ok", "message": "Dispositivo reiniciado exitosamente"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)