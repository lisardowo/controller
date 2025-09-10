import React, { useEffect } from 'react';
import { View, StyleSheet, Dimensions, TouchableOpacity, Text, Alert } from 'react-native';
import * as ScreenOrientation from 'expo-screen-orientation';
import { useLocalSearchParams, useRouter } from 'expo-router';

const { width, height } = Dimensions.get('window');

export default function ControllerScreen() {
  const params = useLocalSearchParams();
  const serverIp = params.serverIp as string;
  const router = useRouter();

  useEffect(() => {
    // Forzar orientación horizontal al montar
    ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE);
  }, []);

  // Función para enviar comandos al servidor
  const sendCommand = async (comando: string) => {
    try {
      await fetch(`http://${serverIp || '172.17.17.207'}:5000/comando`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comando }),
      });
    } catch (error) {
      console.log('Error enviando comando:', error);
    }
  };

  // Función para desconectar y volver a la pantalla principal
  const disconnect = async () => {
    Alert.alert(
      "Desconectar",
      "¿Estás seguro que quieres desconectarte?",
      [
        {
          text: "Cancelar",
          style: "cancel"
        },
        {
          text: "Desconectar",
          onPress: async () => {
            try {
              // Enviar comando de desconexión al servidor
              await fetch(`http://${serverIp || '172.17.54.174'}:5000/desconectar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  ip: 'mobile_device', // Identificador del dispositivo móvil
                  nombre: 'Mobile Controller'
                }),
              });
              
              // También enviar comando de reinicio para limpiar completamente
              await fetch(`http://${serverIp || '172.17.54.174'}:5000/reiniciar_dispositivo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  ip: 'mobile_device',
                  nombre: 'Mobile Controller'
                }),
              });
            } catch (error) {
              console.log('Error al desconectar:', error);
            } finally {
              // Volver a la pantalla principal independientemente del resultado
              router.push('/');
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Botón de desconexión en la esquina superior derecha */}
      <TouchableOpacity
        style={styles.disconnectButton}
        onPress={disconnect}
      >
        <Text style={styles.disconnectText}>×</Text>
      </TouchableOpacity>

      {/* Rectángulo izquierdo - Click izquierdo */}
      <TouchableOpacity
        style={styles.sideButtonLeft}
        onPress={() => sendCommand('click_izquierdo')}
      >
        <Text style={styles.buttonText}>L</Text>
      </TouchableOpacity>

      {/* Área central */}
      <View style={styles.centerArea}>
        {/* Área gris larga arriba - Touchpad */}
        <TouchableOpacity
          style={styles.touchpad}
          onPress={() => sendCommand('touchpad')}
        >
          <Text style={styles.buttonText}>Touchpad</Text>
        </TouchableOpacity>

        {/* Cuatro cuadrados pequeños abajo - Flechas */}
        <View style={styles.arrowsContainer}>
          <TouchableOpacity
            style={styles.arrowButton}
            onPress={() => sendCommand('flecha_arriba')}
          >
            <Text style={styles.buttonText}>↑</Text>
          </TouchableOpacity>
          
          <View style={styles.middleArrows}>
            <TouchableOpacity
              style={styles.arrowButton}
              onPress={() => sendCommand('flecha_izquierda')}
            >
              <Text style={styles.buttonText}>←</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.arrowButton}
              onPress={() => sendCommand('flecha_derecha')}
            >
              <Text style={styles.buttonText}>→</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            style={styles.arrowButton}
            onPress={() => sendCommand('flecha_abajo')}
          >
            <Text style={styles.buttonText}>↓</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Rectángulo derecho - Click derecho */}
      <TouchableOpacity
        style={styles.sideButtonRight}
        onPress={() => sendCommand('click_derecho')}
      >
        <Text style={styles.buttonText}>R</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#1c3036',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    position: 'relative',
  },
  disconnectButton: {
    position: 'absolute',
    top: 20,
    right: 20,
    width: 40,
    height: 40,
    backgroundColor: '#FF4444',
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10,
  },
  disconnectText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  sideButtonLeft: {
    width: Math.min(width * 0.15, 80),
    height: height * 0.7,
    backgroundColor: '#444',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sideButtonRight: {
    width: Math.min(width * 0.15, 80),
    height: height * 0.7,
    backgroundColor: '#444',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  centerArea: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'space-between',
    height: height * 0.8,
    marginHorizontal: 20,
  },
  touchpad: {
    width: width * 0.5,
    height: Math.max(height * 0.3, 120),
    backgroundColor: '#666',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  arrowsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  middleArrows: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: width * 0.25,
    marginVertical: 10,
  },
  arrowButton: {
    width: Math.min(width * 0.08, 60),
    height: Math.min(width * 0.08, 60),
    backgroundColor: '#888',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
