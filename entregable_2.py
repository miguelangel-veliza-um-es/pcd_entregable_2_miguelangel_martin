# entregable 2
from abc import ABC, abstractmethod
import random
import time
from datetime import datetime
from functools import reduce
import numpy as np
import threading

##### SINGLETON #####

class entornoIoT:
    _unicaInstancia = None

    def __init__(self, nombreSistema):
            if not isinstance(nombreSistema, str):
                raise TypeError("La variable 'nombreSistema' debe ser de tipo 'str'")
            self._nombreSistema = nombreSistema
            self._temp_actual = 0
            self._ultimos_datos = list() # esta lista contendrá todas las temperaturas del último minuto
            self._inicio_funcionamiento = None
            self._fin_funcionamiento = None
            self._detener_bucle = False # Booleano para detener el funcionamiento del sistema
            self._sensor = Sensor("Sensor de temperatura")
            self._subs = None

    @classmethod
    def obtener_instancia(cls, nombreSistema):
        if cls._unicaInstancia is None:
            cls._unicaInstancia = cls(nombreSistema)
        return cls._unicaInstancia
    
    def info_entorno(self):
        print(f"ENTORNO IoT:\n\tNombre: {self._nombreSistema}\n\tInicio del funcionamiento: {self._inicio_funcionamiento}\n\tFin del funcionamiento: {self._fin_funcionamiento}\n")

    # Función para generar el valor de la temperatura cada 5 segundos
    def _generar_datos(self):
        time.sleep(5)
        t = round(random.uniform(5,40),2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._sensor.registrar_datos((timestamp,t))
        # cuando registro un nuevo valor de temperatura salta la notificación
        return 

    # Función para pasar los valores registrados al entornoIoT
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
        if not isinstance(nombre_subs, str):
            raise TypeError("La variable 'nombreSistema' debe ser de tipo 'str'")
        subs = Alerta_Nuevo_Registro(nombre_subs)
        self._sensor.alta_subscriptor(subs)
        self._subs = subs      

    def iniciar_funcionamiento(self):
        self._inicio_funcionamiento = datetime.now()
        self._registrar_subscriptor("Alerta Registro Temperatura")
        self._detener_bucle = False
        print("Registrando temperaturas ....")
        # Creamos un hilo con el objetivo de que el entornoIoT continúe registrando temperaturas mientras espera
        # que el usuario presione Enter. Esta espera se va a realizar en segundo plano para no bloquear el programa
        # principal.
        # Creamos el hilo. Este inicia la ejecución de la función _parar_funcionamiento
        hilo_entrada = threading.Thread(target=self._parar_funcionamiento)
        hilo_entrada.start()

        # Mientras no se presione Enter, self._detener_bucle = False
        while not self._detener_bucle:
            self._generar_datos()
            self._obtener_datos()
            self._realizar_calculos()

    def _parar_funcionamiento(self):
        input("Presiona Enter para detener el registro de temperaturas...\n")
        self._detener_bucle = True
        self._fin_funcionamiento = datetime.now()
        # Con esta función, cuando se presione Enter se detiene el entornoIoT deja de registrar temperaturas

##### OBSERVER #####

class Sensor:
    def __init__(self, name):
        self._subscriptores = []
        if not isinstance(name, str):
                raise TypeError("La variable 'nombreSistema' debe ser de tipo 'str'")
        self.name = name

    def alta_subscriptor(self, subscriptor):
        if not isinstance(subscriptor, Subscriptor):
                raise TypeError("La variable 'subscriptor' debe ser de tipo 'Subscriptor'")
        self._subscriptores.append(subscriptor)

    def eliminar_subscriptor(self, subscriptor):
        if not isinstance(subscriptor, Subscriptor):
            raise TypeError("La variable 'subscriptor' debe ser de tipo 'Subscriptor'")
        self._subscriptores.remove(subscriptor)

    def notificar_subscriptores(self, datos):
        for subscriptor in self._subscriptores:
            subscriptor.actualizar(datos)
    
    def registrar_datos(self, datos):
        self.datos = datos
        self.notificar_subscriptores(self.datos)

class Subscriptor(ABC):
    @abstractmethod
    def actualizar(self, data):
        pass

class Alerta_Nuevo_Registro(Subscriptor):
    def __init__(self, nombre):
        self.nombre = nombre
        self._datos = None

    def get_datos(self):
        return self._datos

    def actualizar(self, datos):
        self._datos = datos
        print(f"Nuevo registro de temperatura: {self.get_datos()}\n")

##### CHAIN OF RESPONSABILITY ######

class manejadorcalculos(ABC):
    def __init__(self, ultimos_datos, successor=None): 
        if not isinstance(successor, manejadorcalculos) and successor != None:
            raise TypeError("La variable 'successor' debe ser de tipo 'manejadorcaculos'")
        if not isinstance(ultimos_datos, list) or not all(isinstance(elem, float) for elem in ultimos_datos):
            raise TypeError("La variable 'ultimos_datos' debe ser de tipo 'lista' formada por elementos de tipo 'float")
        self._successor = successor
        self._ultimos_datos = ultimos_datos
        # Este atributo de la clase 'manejadorcalculos' se utilizará para instanciar el patrón de diseño
        # 'strategy' implementado para determinar una determina estrategia.
        self._estrategia = None

    @abstractmethod  
    def manejar_posicion(self):
        pass

class manejadorEstadisticos_EstrategiaA(manejadorcalculos):
    def establecer_estrategia_manejador(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaA())
    def manejar_posicion(self):
        self.establecer_estrategia_manejador()
        media, sd = self._estrategia.hacer_algo(self._ultimos_datos)
        print(f"Media: {media}\n\nDesviación típica: {sd}")
        if self._successor is not None:
            self._successor.manejar_posicion()
        return

class manejadorEstadisticos_EstrategiaB(manejadorcalculos):
    def establecer_estrategia_manejador(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaB())
    def manejar_posicion(self):
        self.establecer_estrategia_manejador()
        cuantil_25, cuantil_50, cuantil_75 = self._estrategia.hacer_algo(self._ultimos_datos)
        print(f"\n\nCuantil 25 (primer cuartil): {cuantil_25}")
        print(f"\nCuantil 50 (mediana): {cuantil_50}")
        print(f"\nCuantil 75 (tercer cuartil): {cuantil_75}")
        if self._successor is not None:
            self._successor.manejar_posicion()
        return

class manejadorEstadisticos_EstrategiaC(manejadorcalculos):
    def establecer_estrategia_manejador(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC())
    def manejar_posicion(self):
        self.establecer_estrategia_manejador()
        maximo, minimo = self._estrategia.hacer_algo(self._ultimos_datos)
        print(f"\n\nTemperatura máxima en los ultimos 60 segundos: {maximo}")
        print(f"\nTemperatura mínima en los ultimos 60 segundos: {minimo}")
        if self._successor is not None:
            self._successor.manejar_posicion()
        return

class manejadorSuperaUmbral(manejadorcalculos):
    # Utilizamos los resultados calculos por la EstrategiaC para obtener el valor máximo de temperatura
    # registrado durante el último minuto
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC())

    def manejar_posicion(self):
        self.establecer_estrategia()
        L = self._ultimos_datos
        temp_umbral = 36
        maximo, _ = self._estrategia.hacer_algo(L)
        supera = maximo > temp_umbral
        print(f"¿Se ha sobrepasado la temperatura {temp_umbral}ºC en los últimos 60 segundos?")
        print("- Sí\n" if supera else "- No\n")
        if self._successor is not None:
            self._successor.manejar_posicion()
        return

class manejadorAumentoTemperatura(manejadorcalculos):
    def establecer_estrategia(self):
        self._estrategia = Contexto()
        self._estrategia.establecer_estrategia(EstrategiaC())

    def manejar_posicion(self):
        L = self._ultimos_datos
        t = 30
        temp_dif = 10
        print(f"¿Ha habido una diferencia de temperatura de {temp_dif}ºC en un intervalo de {t} segundos?")

        if len(L) < 7:
            print("- No\n\n")
        else:
            self.establecer_estrategia()
            L = self._ultimos_datos
            t = 30
            ultimos_30 = L[-7:] #Nótese que obtenemos datos cada 5 segundos
            temp_dif = 10
            maximo, minimo = self._estrategia.hacer_algo(ultimos_30)
            dif = maximo-minimo
            supera = dif > temp_dif
            print("- Sí\n\n" if supera else "- No\n\n")
        if self._successor is not None:
            self._successor.manejar_posicion()
        return


##### STRATEGY #####
class Contexto: 
    _estrategia = None
    def establecer_estrategia(self, estrategia):
        if not isinstance(estrategia, Estrategia):
            raise TypeError("La estrategia elegida debe ser de tipo 'Estrategia'")
        self._estrategia = estrategia

    def hacer_algo(self, L):
        return self._estrategia.aplicar_estrategia(L)

class Estrategia(ABC):
    @abstractmethod
    def aplicar_estrategia(self,L):
        pass

class EstrategiaA(Estrategia):
    def aplicar_estrategia(self, L):
        
        if not isinstance(L, list):
            raise TypeError("El parametro proporcionado debe ser de tipo 'list'.")
        if not all(isinstance(elem, (float, int)) for elem in L):
            raise TypeError("La lista debe contener solo elementos de tipo 'float' o 'int'.")
        
        calc_media = lambda lista: round(reduce(lambda x,y: (x+y) ,lista)/len(lista),3)
        calc_sd = lambda lista: round((reduce(lambda x,y: x+y, map(lambda x: (x[0] - x[1])**2, zip(lista, [calc_media(lista)]*len(lista))))/len(lista))**(1/2),3)

        return calc_media(L), calc_sd(L)

class EstrategiaB(Estrategia):
    def aplicar_estrategia(self, L):
        
        if not isinstance(L, list):
            raise TypeError("El parametro proporcionado debe ser de tipo 'list'.")
        if not all(isinstance(elem, (float, int)) for elem in L):
            raise TypeError("La lista debe contener solo elementos de tipo 'float' o 'int'.")
        
        from math import ceil

        calc_cuantil = lambda lista, cuantil: sorted(lista)[ceil(len(lista)*cuantil)-1] if len(lista)%(1/cuantil) != 0 else (sorted(lista)[int(len(lista)*cuantil)-1] + sorted(lista)[int(len(lista)*cuantil)])/2

        return (calc_cuantil(L, 1/4), calc_cuantil(L, 1/2), calc_cuantil(L, 3/4))

class EstrategiaC(Estrategia):
    def aplicar_estrategia(self, L):
        
        if not isinstance(L, list):
            raise TypeError("El parametro proporcionado debe ser de tipo 'list'.")
        if not all(isinstance(elem, (float, int)) for elem in L):
            raise TypeError("La lista debe contener solo elementos de tipo 'float' o 'int'.")

        calc_max = lambda lista: reduce(lambda x, y: x if x > y else y, lista)
        calc_min = lambda lista: reduce(lambda x, y: x if x < y else y, lista)

        return (calc_max(L), calc_min(L))

##### CLIENTE #####
try:
    entorno = entornoIoT.obtener_instancia('SistemaIoT')
    entorno.obtener_instancia('SistemaIoT_2')
    entorno.info_entorno()
    entorno.iniciar_funcionamiento()
    entorno.info_entorno()

except(TypeError) as e:
    import sys
    exc_type, exc_obj, exc_tb = sys.exc_info()
    line_number = exc_tb.tb_lineno
    print(f"Error en la línea {line_number}: {e}")