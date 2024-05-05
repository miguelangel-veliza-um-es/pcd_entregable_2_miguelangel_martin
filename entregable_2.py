# entregable 2
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
import random
import time
from datetime import datetime
import functools
import math
import numpy as np
import threading

########## SINGLETON ###################
# R1 -> Singleton

class entornoIoT:
    _unicaInstancia = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._unicaInstancia:
            cls._unicaInstancia = super().__new__(cls)
        return cls._unicaInstancia

    def __init__(self, nombreSistema, fecha_funcionamiento):
        # Solo inicializa si no se ha inicializado anteriormente
        if not hasattr(self, '_inicializado'):
            self._temp_actual = 0
            self._ultimos_datos = list() # esta lista contendrá todas las temperaturas del último minuto
            self.nombreSistema = nombreSistema
            self.fecha_funcionamiento = fecha_funcionamiento
            self._inicializado = True  # Marca como inicializado
            self._detener_bucle = False
    
    def info_entorno(self):
        print(f"ENTORNO IoT:\n\tNombre: {self.nombreSistema}\n\tFecha_funcionamiento: {self.fecha_funcionamiento}\n")
    
    def _generador_temp(self):
        nueva_temp = round(random.uniform(5,40),2)
        self._temp_actual = nueva_temp
        if len(self._ultimos_datos) > 12:
            self._ultimos_datos.append(nueva_temp)
            self._ultimos_datos.pop(0)
        else:
            self._ultimos_datos.append(nueva_temp)
        self._notificar_sistema()
        time.sleep(5)
        return 
    
    def _notificar_sistema(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t = self._temp_actual
        print((timestamp, t))
        subs = subscriptor(self._ultimos_datos)
        subs.actualizar()
        print("\n---------------------------------------------------------------\n")
    
    def iniciar_funcionamiento(self):
        self._detener_bucle = False
        print("Registrando temperaturas ....")
        # Iniciar hilo para leer la entrada del usuario
        hilo_entrada = threading.Thread(target=self.leer_entrada)
        hilo_entrada.start()
        
        # Bucle principal para registrar temperaturas
        while not self._detener_bucle:
            self._generador_temp()
    
    def leer_entrada(self):
        # Función para leer la entrada del usuario en segundo plano
        input("Presiona Enter para detener el registro de temperaturas...")
        self._detener_bucle = True

############# OBSERVER ###########################

# El publicador de datos de sensor es el EntornoIoT

class subscriptor(ABC):
    def __init__(self, ultimos_datos):
        self._ultimos_datos = ultimos_datos
        
    def actualizar(self):
        L = self._ultimos_datos
        T = manejadorAumentoTemperatura(L)
        U = manejadorSuperaUmbral(L, T)
        C = manejadorEstadisticos_EstrategiaC(L, U)
        B = manejadorEstadisticos_EstrategiaB(L, C)
        A = manejadorEstadisticos_EstrategiaA(L, B)
        
        A.manejar_posicion()

############### CHAIN OF RESPONSABILITY ##################

class manejadorcalculos(ABC):
    def __init__(self, ultimos_datos, successor=None):
        self.succesor = successor
        self._ultimos_datos = ultimos_datos
        self._estrategia = None
    
    @abstractmethod  
    def manejar_posicion(self):
        pass

class manejadorEstadisticos_EstrategiaA(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaA)
    def manejar_posicion(self):
        self.establecer_estrategia()
        self._estrategia.hacer_algo(self._ultimos_datos)
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorEstadisticos_EstrategiaB(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaB)
    def manejar_posicion(self):
        self.establecer_estrategia()
        self._estrategia.hacer_algo(self._ultimos_datos)
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorEstadisticos_EstrategiaC(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC)
    def manejar_posicion(self):
        self.establecer_estrategia()
        self._estrategia.hacer_algo(self._ultimos_datos)
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorSuperaUmbral(manejadorcalculos):
     def __init__(self, ultimos_datos, successor=None):
         super().__init__(ultimos_datos, successor)
     
     def manejar_posicion(self):
        L = self._ultimos_datos
        temp = 36
        if len(list(filter(lambda x: x > temp, L))) > 0 :
            print(f"Se han recogido temperaturas superiores a {temp} ºC.")
        else:
            print(f"No se ha superado los {temp}ºC.")
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorAumentoTemperatura(manejadorcalculos):
    def __init__(self, ultimos_datos, successor=None):
        super().__init__(ultimos_datos, successor)
    def manejar_posicion(self):
        print('Aumento Temperatura')
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return


#########################################################
# STRATEGY
class Contexto: 
    def establecer_estrategia(self, estrategia):
        self._estrategia = estrategia
        
    def hacer_algo(self, L):
        self._estrategia.aplicar_estrategia(self, L)

class Estrategia(ABC):
    @abstractmethod
    def aplicar_estrategia(self):
        pass

class EstrategiaA(Estrategia):
    def aplicar_estrategia(self, L):
        lon = len(L)
        media = round(functools.reduce(lambda x,y: x+y, L) / lon, 3)
        desviacion_tipica = round(math.sqrt(functools.reduce(lambda x,y: x + y ,map(lambda x: (x - media)**2, L))) / lon ,3)
        print(media, desviacion_tipica)
        return

class EstrategiaB(Estrategia):
    def aplicar_estrategia(self, L):
        cuantil_25 = np.quantile(L, 0.25)
        cuantil_50 = np.quantile(L, 0.5)  
        cuantil_75 = np.quantile(L, 0.75)

        print("Cuantil 25 (primer cuartil):", cuantil_25)
        print("Cuantil 50 (mediana):", cuantil_50)
        print("Cuantil 75 (tercer cuartil):", cuantil_75)
        return 

class EstrategiaC(Estrategia):
    def aplicar_estrategia(self, L):
        maximo = max(L)
        minimo = min(L)
        print(f"Temperatura maxima en los ultimos 60 segundos: {maximo}")
        print(f"Temperatura minima en los ultimos 60 segundos: {minimo}")
        return 



############### cliente ####################

entorno = entornoIoT('Invernadero', 'Hoy')
entorno.iniciar_funcionamiento()

