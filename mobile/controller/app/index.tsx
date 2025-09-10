import React, { useEffect, useState, useCallback } from 'react';
import { StyleSheet, Text, View, Image, TouchableOpacity, Alert } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import * as Network from 'expo-network';

export default function HomeScreen() {
  const [username, setUsername] = useState('');
  const [userNumber, setUserNumber] = useState('');
  const [deviceIp, setDeviceIp] = useState<string>(''); // IP dinámica del dispositivo
  const [serverIp, setServerIp] = useState<string | null>(null);
  const [isPublished, setIsPublished] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Buscando servidor...');
  const router = useRouter();

  // Función para reiniciar el estado del dispositivo
  const resetDeviceState = useCallback(async () => {
    setIsPublished(false);
    setIsConnected(false);
    setServerIp(null);
    setDeviceIp('');
    setStatusMessage('Buscando servidor...');
  }, []); // Sin dependencias para evitar bucles infinitos

  // Efecto para generar el nombre de usuario al cargar
  useEffect(() => {
    const names = ["Usuario", "Player", "Gamer", "Controller"];
    const number = Math.floor(Math.random() * (9999 - 1000 + 1)) + 1000;
    const randomName = names[Math.floor(Math.random() * names.length)];
    
    setUsername(randomName);
    setUserNumber(`#${number}`);
    
    // Reiniciar estado al cargar la aplicación (solo una vez)
    resetDeviceState();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Solo ejecutar una vez al montar el componente (intencional para evitar bucles)

  // Función para obtener la IP del dispositivo dinámicamente
  const getDeviceIp = useCallback(async (): Promise<string> => {
    try {
      const ip = await Network.getIpAddressAsync();
      return ip || '';
    } catch (error) {
      console.log('No se pudo obtener la IP del dispositivo', error);
      return '';
    }
  }, []); // Sin dependencias para evitar re-renders constantes

  // Función para verificar si una IP tiene el servidor
  const checkServer = useCallback(async (ip: string): Promise<string | null> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000);

      const response = await fetch(`http://${ip}:5000/health`, {
        method: 'GET',
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        return ip;
      }
    } catch {
      // Silenciar errores de conexión
    }
    return null;
  }, []);

  // Función para escanear IPs en la red local
  const scanForServer = useCallback(async () => {
    setStatusMessage('Escaneando red local...');
    // Intento especial para emulador Android (host PC)
    let foundIp = await checkServer('10.0.2.2');
    if (foundIp) return foundIp;

    // Obtener IP del dispositivo para inferir subred
    const myIp = await getDeviceIp();
    if (myIp) setDeviceIp(myIp);
    const parts = myIp?.split('.') || [];
    if (parts.length === 4) {
      const base = `${parts[0]}.${parts[1]}.${parts[2]}`;
      const chunkSize = 25;
      // Escanear /24 en bloques para evitar bloquear UI
      for (let start = 1; start <= 254; start += chunkSize) {
        const batch: Promise<string | null>[] = [];
        for (let i = start; i < Math.min(start + chunkSize, 255); i++) {
          batch.push(checkServer(`${base}.${i}`));
        }
        const results = await Promise.all(batch);
        const ok = results.find(Boolean);
        if (ok) return ok as string;
      }
    }
    return null;
  }, [checkServer, getDeviceIp]);

  // Función para publicar disponibilidad en el servidor
  const publishDevice = useCallback(async (targetIp: string) => {
    try {
      // Obtener la IP dinámica del dispositivo
      const currentDeviceIp = await getDeviceIp();
      
      // Actualizar el estado con la IP obtenida
      setDeviceIp(currentDeviceIp);
      
      const response = await fetch(`http://${targetIp}:5000/publicar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre: `${username} ${userNumber}`,
          ip: currentDeviceIp, // Usar IP dinámica
        }),
      });

      if (response.ok) {
        setIsPublished(true);
        setStatusMessage('Disponible para conexión');
        return true;
      }
    } catch (error) {
      console.log('Error publicando dispositivo:', error);
    }
    return false;
  }, [username, userNumber, getDeviceIp]);

  // Función para responder a solicitud de conexión
  const respondToRequest = useCallback(async (targetIp: string, solicitudId: string, accept: boolean) => {
    try {
      const response = await fetch(`http://${targetIp}:5000/responder_solicitud`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          solicitud_id: solicitudId,
          aceptar: accept,
        }),
      });

      if (response.ok && accept) {
        setIsConnected(true);
        setStatusMessage('¡Conectado!');
        Alert.alert(
          "Conexión Autorizada",
          "Dispositivo conectado exitosamente",
          [
            {
              text: "Ir al Controlador",
              onPress: () => router.push(`/controller?serverIp=${targetIp}`)
            },
            {
              text: "OK",
              style: "cancel"
            }
          ]
        );
      } else if (response.ok && !accept) {
        setStatusMessage('Conexión rechazada');
      }
    } catch (error) {
      console.log('Error respondiendo solicitud:', error);
    }
  }, [router]); // Agregar router como dependencia

  // Función para verificar solicitudes de conexión
  const checkConnectionRequests = useCallback(async (targetIp: string) => {
    try {
      const response = await fetch(`http://${targetIp}:5000/verificar_solicitudes`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.solicitudes && data.solicitudes.length > 0) {
          // Mostrar prompt de autorización
          const solicitud = data.solicitudes[0]; // Tomar la primera solicitud
          Alert.alert(
            "Solicitud de Conexión",
            "Una PC quiere conectarse a este dispositivo. ¿Autorizar conexión?",
            [
              {
                text: "Rechazar",
                onPress: () => respondToRequest(targetIp, solicitud.solicitud_id, false),
                style: "cancel"
              },
              {
                text: "Autorizar",
                onPress: () => respondToRequest(targetIp, solicitud.solicitud_id, true)
              }
            ]
          );
        }
      }
    } catch (error) {
      console.log('Error verificando solicitudes:', error);
    }
  }, [respondToRequest]); // Ahora incluir respondToRequest como dependencia

  // Efecto para detectar cuando regresamos desde el controlador (posible desconexión)
  useFocusEffect(
    useCallback(() => {
      // Si estábamos conectados y regresamos a esta pantalla, resetear completamente
      if (isConnected) {
        // Resetear directamente sin usar la función para evitar dependencias
        setIsConnected(false);
        setIsPublished(false);
        setServerIp(null);
        setDeviceIp('');
        setStatusMessage('Buscando servidor...');
      }
    }, [isConnected])
  );

  // Efecto principal para manejar el flujo de conexión
  useEffect(() => {
    const initializeConnection = async () => {
      if (!serverIp) {
        const foundIp = await scanForServer();
        if (foundIp) {
          setServerIp(foundIp);
          setStatusMessage(`Servidor encontrado: ${foundIp}`);
        } else {
          setStatusMessage('Servidor no encontrado');
          return;
        }
      }
    };

    initializeConnection();
  }, [serverIp, scanForServer]);

  // Efecto para publicar y verificar solicitudes
  useEffect(() => {
    if (!serverIp || !username) return;

    const interval = setInterval(async () => {
      if (!isPublished) {
        await publishDevice(serverIp);
      } else if (!isConnected) {
        await checkConnectionRequests(serverIp);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [serverIp, username, isPublished, isConnected, publishDevice, checkConnectionRequests]);

  const handleOpenController = () => {
    if (isConnected && serverIp) {
      router.push(`/controller?serverIp=${serverIp}`);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.userContainer}>
        <Text style={styles.usernameText}>{username}</Text>
        <Text style={styles.userNumberText}>{userNumber}</Text>
      </View>
      
      <Image
        source={require('../assets/images/Idle.png')}
        style={styles.image}
      />
      
      <Text style={[
        styles.statusText, 
        isConnected && styles.connectedText,
        isPublished && !isConnected && styles.publishedText
      ]}>
        {statusMessage}
      </Text>

  {!!deviceIp && (
        <Text style={styles.deviceIpText}>
          IP del dispositivo: {deviceIp}
        </Text>
      )}

      {isConnected && (
        <TouchableOpacity style={styles.controllerButton} onPress={handleOpenController}>
          <Text style={styles.buttonText}>Abrir Controlador</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1c3036',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  userContainer: {
    flexDirection: 'row',
    marginBottom: 30,
  },
  usernameText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  userNumberText: {
    fontSize: 24,
    color: 'rgba(255, 255, 255, 0.5)',
    fontWeight: 'bold',
  },
  image: {
    width: 200,
    height: 200,
    resizeMode: 'contain',
  },
  statusText: {
    marginTop: 30,
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.7)',
    fontStyle: 'italic',
  },
  connectedText: {
    color: '#4CAF50',
    fontStyle: 'normal',
    fontWeight: 'bold',
  },
  publishedText: {
    color: '#FF9800',
    fontStyle: 'normal',
    fontWeight: 'bold',
  },
  deviceIpText: {
    marginTop: 10,
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.5)',
    fontStyle: 'italic',
  },
  controllerButton: {
    marginTop: 30,
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});
