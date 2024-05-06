# entregable 2
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
import random
import time
from datetime import datetime
from functools import reduce
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
            self._sensor = Sensor("Sensor de temperatura")
            self._subs = None
    
    def info_entorno(self):
        print(f"ENTORNO IoT:\n\tNombre: {self.nombreSistema}\n\tFecha_funcionamiento: {self.fecha_funcionamiento}\n")
    
    def _generar_datos(self):
        t = round(random.uniform(5,40),2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._sensor.nuevos_datos((timestamp,t))
        time.sleep(5)
        return 
    
    def _obtener_datos(self):
        nueva_temp = self._subs.get_datos()[1]
        if len(self._ultimos_datos) > 12:
            self._ultimos_datos.append(nueva_temp)
            self._ultimos_datos.pop(0)
        else:
            self._ultimos_datos.append(nueva_temp)
        return 
    
    def _realizar_calculos(self):
        L = self._ultimos_datos
        T = manejadorAumentoTemperatura(L)
        U = manejadorSuperaUmbral(L, T)
        C = manejadorEstadisticos_EstrategiaC(L, U)
        B = manejadorEstadisticos_EstrategiaB(L, C)
        A = manejadorEstadisticos_EstrategiaA(L, B)
        
        A.manejar_posicion()
        
    def _registrar_subscriptor(self, nombre_subs):
        subs = MiSubscriptor(nombre_subs)
        self._sensor.registrar_subscriptor(subs)
        self._subs = subs      
    
    def iniciar_funcionamiento(self):
        self._registrar_subscriptor("Subscriptor 1")
        self._detener_bucle = False
        print("Registrando temperaturas ....")
        # Iniciar hilo para leer la entrada del usuario
        hilo_entrada = threading.Thread(target=self.leer_entrada)
        hilo_entrada.start()
        
        # Bucle principal para registrar temperaturas
        while not self._detener_bucle:
            self._generar_datos()
            self._obtener_datos()
            self._realizar_calculos()
    
    def leer_entrada(self):
        # Función para leer la entrada del usuario en segundo plano
        input("Presiona Enter para detener el registro de temperaturas...\n")
        self._detener_bucle = True

############# OBSERVER ###########################

# El publicador de datos de sensor es el EntornoIoT

class PublicadorDatosSensor:
    def __init__(self):
        self._subscriptores = []

    def registrar_subscriptor(self, subscriptor):
        self._subscriptores.append(subscriptor)

    def eliminar_subscriptor(self, subscriptor):
        self._subscriptores.remove(subscriptor)

    def notificar_subscriptores(self, datos):
        for subscriptor in self._subscriptores:
            subscriptor.actualizar(datos)

class Subscriptor(ABC):
    @abstractmethod
    def actualizar(self, data):
        pass
    
class Sensor(PublicadorDatosSensor):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.datos = None

    def nuevos_datos(self, datos):
        self.datos = datos
        self.notificar_subscriptores(self.datos)
        
class MiSubscriptor(Subscriptor):
    def __init__(self, nombre):
        self.nombre = nombre
        self._datos = None
        
    def get_datos(self):
        return self._datos
              
    def actualizar(self, datos):
        self._datos = datos
        print(f"El usuario {self.nombre} ha obtenido los siguientes datos: {self.get_datos()}\n")
        self.datos = datos

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
        media, sd = self._estrategia.hacer_algo(self._ultimos_datos)
        print(f"Media: {media}, Desviación típica: {sd}")
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorEstadisticos_EstrategiaB(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaB)
    def manejar_posicion(self):
        self.establecer_estrategia()
        cuantil_25, cuantil_50, cuantil_75 = self._estrategia.hacer_algo(self._ultimos_datos)
        print("Cuantil 25 (primer cuartil):", cuantil_25)
        print("Cuantil 50 (mediana):", cuantil_50)
        print("Cuantil 75 (tercer cuartil):", cuantil_75)
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorEstadisticos_EstrategiaC(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC)
    def manejar_posicion(self):
        self.establecer_estrategia()
        maximo, minimo = self._estrategia.hacer_algo(self._ultimos_datos)
        print(f"Temperatura máxima en los ultimos 60 segundos: {maximo}")
        print(f"Temperatura mínima en los ultimos 60 segundos: {minimo}")
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorSuperaUmbral(manejadorcalculos):
     def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC)
     
     def manejar_posicion(self):
        self.establecer_estrategia()
        L = self._ultimos_datos
        temp_umbral = 36
        maximo, _ = self._estrategia.hacer_algo(L)
        supera = maximo > temp_umbral
        print(f"¿Se ha sobrepasado la temperatura {temp_umbral}ºC?")
        print("- Sí" if supera else "- No")
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return

class manejadorAumentoTemperatura(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC)
     
    def manejar_posicion(self):
        L = self._ultimos_datos
        t = 30
        temp_dif = 10
        print(f"¿Ha habido una diferencia de temperatura de {temp_dif}ºC en un intervalo de {t} segundos?")
        
        if len(L) < 7:
            print("- No\n")
        else:
            self.establecer_estrategia()
            L = self._ultimos_datos
            t = 30
            ultimos_30 = L[-7:] #Nótese que obtenemos datos cada 5 segundos
            temp_dif = 10
            maximo, minimo = self._estrategia.hacer_algo(ultimos_30)
            dif = maximo-minimo
            supera = dif > temp_dif
            print("- Sí" if supera else "- No\n")
        if self.succesor is not None:
            self.succesor.manejar_posicion()
        return


#########################################################
# STRATEGY
class Contexto: 
    def establecer_estrategia(self, estrategia):
        self._estrategia = estrategia
        
    def hacer_algo(self, L):
        return self._estrategia.aplicar_estrategia(self, L)

class Estrategia(ABC):
    @abstractmethod
    def aplicar_estrategia(self):
        pass

class EstrategiaA(Estrategia):
    def aplicar_estrategia(self, L):
        
        calc_media = lambda lista: round(reduce(lambda x,y: (x+y) ,lista)/len(lista),3)
        calc_sd = lambda lista: round((reduce(lambda x,y: x+y, map(lambda x: (x[0] - x[1])**2, zip(lista, [calc_media(lista)]*len(lista))))/len(lista))**(1/2),3)

        return calc_media(L), calc_sd(L)

class EstrategiaB(Estrategia):
    def aplicar_estrategia(self, L):
        from math import ceil
        
        calc_cuantil = lambda lista, cuantil: sorted(lista)[ceil(len(lista)*cuantil)-1] if len(lista)%(1/cuantil) != 0 else (sorted(lista)[int(len(lista)*cuantil)-1] + sorted(lista)[int(len(lista)*cuantil)])/2
        
        return (calc_cuantil(L, 1/4), calc_cuantil(L, 1/2), calc_cuantil(L, 3/4))

class EstrategiaC(Estrategia):
    def aplicar_estrategia(self, L):
        
        calc_max = lambda lista: reduce(lambda x, y: x if x > y else y, lista)
        calc_min = lambda lista: reduce(lambda x, y: x if x < y else y, lista)
        
        return (calc_max(L), calc_min(L))

############### cliente ####################

entorno = entornoIoT('Invernadero', 'Hoy')
entorno.iniciar_funcionamiento()

