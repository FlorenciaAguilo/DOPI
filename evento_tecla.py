import asyncio
import threading
import websockets
import keyboard
import json
import os

def on_key_press(e,prediccion,marcador,nombre,dato,patologico,f,tipo,carpeta,modo,IDvideo,ruta):
    if e is not None and hasattr(e, 'name'):
    
    # mPrediccion de vista. Permite identificar si el movimiento es valido o no
        if e.name=="f":
            prediccion=False
        if e.name=="g":
            prediccion=True
    
    # Permite simular los distintos movimientos de las distintas vistas 

        if e.name == "6":
            if marcador=="PEL":
                nombre="PEL clasico"
                #IDvideo=0

            if marcador=="PEC":
                nombre="PEC A nivel de los grandes vasos"
                #IDvideo=0

            if marcador=="APICAL":
                nombre="Ap4C"
                #IDvideo=0

            if marcador=="SUBCOSTAL":
                nombre="SUBCOSTAL Ap4C" 
                #IDvideo=0

            if marcador=="SET":
                nombre="SET eje largo"             
                #IDvideo=0

        if e.name == "7":
            if marcador=="PEL":
                nombre="PEL modificado nro 1_TEVD"
                #IDvideo=0

            if marcador=="PEC":
                nombre="PEC A nivel de la valvula mitral"
                #IDvideo=0

            if marcador=="APICAL":
                nombre="Ap5C"
                #IDvideo=0

            if marcador=="SUBCOSTAL":
                nombre="SUBCOSTAL vena cava inferior"
                #IDvideo=0

            if marcador=="SET":
                nombre="SET eje corto"  
                #IDvideo=0      

        if e.name == "8":
            if marcador=="PEL":
                nombre="PEL modificado nro 2_TSVD"
                #IDvideo=0

            if marcador=="PEC":
                nombre="PEC A nivel de los musculos papilares"
                #IDvideo=0

            if marcador=="APICAL":
                nombre="Ap2C"
                #IDvideo=0

        if e.name == "9":
            if marcador=="PEC":
                nombre="PEC A nivel de la punto del VI"
                #IDvideo=0

            if marcador=="APICAL":
                nombre="Ap3C"
                #IDvideo=0

        dato['patologia']=patologico

        if patologico==False:
            tipo="anatomia"
        else:
            tipo="patologia"
        
        dato['btn']=f
        dato['status']=prediccion
        dato['marcador']=marcador
        dato['Nombre_movimiento']=nombre

        # carpeta=marcador+"\\"+tipo+"\\"+nombre+"\\"+modo
        # ruta=cargar_ML_plano(f"{IDvideo}"+f" {marcador}",carpeta)
        
        if nombre is not None:
            # Construir la carpeta utilizando los valores de marcador, tipo y nombre
            carpeta = os.path.join(marcador, tipo, nombre, modo)
            # Obtener el nombre del archivo de la carpeta utilizando cargar_ML_plano
            nombre_archivo = cargar_ML_plano(f"{IDvideo} {marcador}", carpeta)
            
            if nombre_archivo is not None:
                # Construir la URL completa del video
                dato['dirVideo'] = f"http://localhost:3000/{marcador}/{tipo}/{nombre}/{modo}/{nombre_archivo}"
            else:
                dato['dirVideo'] = None
        # #dato['dirVideo']=ruta
        # ruta2=marcador+"\\"+tipo+"\\"+nombre+"\\"+modo+"\\"+ f"{IDvideo}"+f" {marcador}"
        # dato['dirVideo']=f"http://localhost:3000/{ruta2}" if ruta2 else None
        
        
        dato['IDvideo']=IDvideo

        return prediccion,marcador,nombre,dato,patologico,f,tipo,carpeta,modo,IDvideo,ruta


def cargar_ML_plano(clave,otracarpeta):
    global marcador,tipo,nombre
    directorio_base = os.path.expanduser("~")  # Obtenemos el directorio base del usuario
    escritorio = os.path.join(directorio_base, "Desktop\\simulador_edopi_backend"+"\\"+otracarpeta)
    
    # Verifica si la carpeta existe
    if not os.path.exists(escritorio):
        return None
        
    # # Recorre los archivos en el directorio
    # for raiz, carpetas, archivos in os.walk(escritorio):
    #     for nombre_archivo in archivos:
    #         if clave in nombre_archivo:
    #             # Imprime el nombre completo del archivo que contiene la palabra buscada
    #             nombre_completo = os.path.join(raiz, nombre_archivo)
    #             return nombre_completo
    #             #print(nombre_completo)
    #     # Si no se encuentra el archivo, devuelve None
    # #print(f"No se encontró ningún archivo con la clave '{clave}' en la carpeta '{escritorio}'.")
    # return None

    # Recorre los archivos en el directorio
    for raiz, carpetas, archivos in os.walk(escritorio):
        for nombre_archivo in archivos:
            if clave in nombre_archivo:
                # Solo devuelve el nombre del archivo, sin la ruta completa
                return nombre_archivo
    
    # Si no se encuentra el archivo, devuelve None
    return None