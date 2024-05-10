# test_entorno_iot.py

import pytest
from entregable_2 import *

def test_singleton():
    # Nos aseguramos de que solamente hay una instancia del Singleton
    instance1 = EntornoIoT.obtener_instancia("Mi sistema IOT")
    instance2 = EntornoIoT.obtener_instancia("Otro sistema IOT")
    assert instance1 is instance2

def test_nombre_entornoIoT():
    EntornoIoT._unicaInstancia = None
    with pytest.raises(TypeError):
        EntornoIoT.obtener_instancia(33)

def test_registrar_subs():
    EntornoIoT._unicaInstancia = None
    with pytest.raises(TypeError):
        EntornoIoT.obtener_instancia("Sensor IoT")._registrar_subscriptor(Subscriptor())

def test_nombre_sensor():
    with pytest.raises(TypeError):
        Sensor(33)
        
def test_alta_subs():
    with pytest.raises(TypeError):
        Sensor("Cámara").alta_subscriptor("Manolo")

def test_eliminar_subs():
    with pytest.raises(TypeError):
        Sensor("Cámara").eliminar_subscriptor("Manolo")

def test_manejadorcalculos():
    with pytest.raises(TypeError):
        ManejadorEstadisticos_EstrategiaA([1,2,3], "manejador")
        
    with pytest.raises(TypeError):
        ManejadorEstadisticos_EstrategiaA([1,2,"Hola"])

def test_contexto():
    with pytest.raises(TypeError):
        Contexto().establecer_estrategia("Mi estrategia")

def test_estrategiaA():
    with pytest.raises(TypeError):
        EstrategiaA().aplicar_estrategia("Hola")


    with pytest.raises(TypeError):
        EstrategiaA().aplicar_estrategia([1,2,"Hola"])

if __name__ == "__main__":
    pytest.main()