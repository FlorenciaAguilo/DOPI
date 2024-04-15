import asyncio
import threading
import websockets
import keyboard
import json
import os
from evento_tecla import on_key_press

client={}

# Variable para almacenar el cliente frontend
frontend = None
transductor= None

mensaje_frontend=None
mensaje_transductor=None

f=""
data=""
prediccion=""
nombre=""
marcador=""
patologico=False
tipo=""
ruta=""
IDvideo=0  # sirve para acceder a cada video en una carpeta dada
carpeta="" # sirve para acceder a la carpeta de videos de una vista, un modo y un movmiento especifico 
modo=""    # modo de la imagen 


lista_videos=[]


dato ={'dirVideo': ruta,'patologia': patologico,'status': prediccion,'Nombre_movimiento': nombre,'marcador': marcador,'IDvideo':IDvideo,'btn': f}


# Función de conversión para manejar listas
def convertir_a_lista(obj):
    if isinstance(obj, list):
        return {'__es_lista__': True, 'datos': obj}
    return obj


# Define una bandera para verificar si el mensaje ya se envió
enviar_dataa=True
patologico_anterior = None  # Variable para almacenar el valor anterior de patologico

def codigo_modo(codigo):
    if codigo==0:
        modo="Bidimensional"

    if codigo==1:
        modo="Modo Doppler Color"

    if codigo==2:
        modo="Modo Doppler Pulsado"

    if codigo==3:
        modo="Modo Doppler Continuo"

    if codigo==4:
        modo="Modo Doppler Tisular"

    if codigo==5:
        modo="Modo M"

def listar_videos():
    global modo,marcador,tipo,nombre,modo,lista_videos
    directorio_base = os.path.expanduser("~")  # Obtenemos el directorio base del usuario
    lista_carpetas = {}

    # Ruta base donde se encuentran las carpetas PEL
    ruta_base_pel = os.path.join(directorio_base, "Desktop", "simulador_edopi_backend", marcador)

    # Recorremos las carpetas principales (anatomico, patologico) dentro de PEL
    for categoria in os.listdir(ruta_base_pel):
        ruta_categoria = os.path.join(ruta_base_pel, categoria)
        if os.path.isdir(ruta_categoria) and categoria == tipo:  # Solo para por el 'tipo' que e sla pestaña activa. Por defecto es anatomia
            lista_carpetas[categoria] = {}
            # Recorremos las subcarpetas de cada categoría (PEL clasico, PEL modificado nro 1_TEVD, etc.)
            for subcategoria in os.listdir(ruta_categoria):
                ruta_subcategoria = os.path.join(ruta_categoria, subcategoria)
                if os.path.isdir(ruta_subcategoria):
                    # Recorremos las subcarpetas de la subcategoría actual (Bidimensional, Modo Doppler Color, etc.)
                    lista_videos = {}
                    for subcarpeta in os.listdir(ruta_subcategoria):
                        ruta_subcarpeta = os.path.join(ruta_subcategoria, subcarpeta)
                        if os.path.isdir(ruta_subcarpeta):
                            # Ahora obtenemos los videos dentro de la subcarpeta actual y los agregamos a la lista de videos
                            videos = []
                            for video in os.listdir(ruta_subcarpeta):
                                if os.path.isfile(os.path.join(ruta_subcarpeta, video)):
                                    videos.append({
                                        "videoTitulo": video,
                                        "dirVideo": os.path.join(ruta_subcarpeta, video)
                                    })
                            lista_videos[subcarpeta] = videos
                    lista_carpetas[categoria][subcategoria] = lista_videos
    
    # Imprimimos la estructura de carpetas y videos
    #print(lista_carpetas)
    return lista_carpetas
    
def custom_on_key_press(e):
    global f, data, dato, ruta, modo, carpeta, IDvideo, marcador, patologico, nombre, tipo, prediccion
    prediccion, marcador, nombre, dato, patologico, f, tipo, carpeta, modo, IDvideo, ruta = on_key_press(
        e, prediccion, marcador, nombre, dato, patologico, f, tipo, carpeta, modo, IDvideo, ruta
    )


async def handle_client(websocket,path):
    global frontend, mensaje_frontend
    global f,data,dato,ruta,modo,carpeta,IDvideo, IDvideo,marcador,patologico,nombre,tipo
    global lista_videos, enviar_dataa, patologico_anterior
        # Define una función que pasa las variables globales a on_key_press

    try:
        async for message in websocket:            
            
            data=json.loads(message)
            print(nombre)
            print(prediccion)
            #identifica al frontend
            if "frontClient" in message:
                print("existe la llave")
                message=json.loads(message)

                if message.get("frontClient") == True:
                    print("se conectó el frontend")
                    id_cliente = id(websocket)
                    client[id_cliente] = websocket
                    frontend = client[id_cliente]
                    
                    
            # Espera hasta recibir la información del marcador

            if 'marcador' in data:
                marcador = data['marcador']
                patologico= data['patologia']
                # Si es la primera vez que se recibe el marcador o el valor de patologico ha cambiado
                
                if enviar_dataa or patologico != patologico_anterior:
                    if patologico == False:
                        tipo = "anatomia"
                    else:
                        tipo = "patologia"

                    lista_videos = listar_videos()
                    dataa = {"vista": marcador, "estructura": lista_videos}
                    msj = json.dumps(dataa)
                    await frontend.send(msj)

                    # Actualizamos la bandera y el valor de patologico anterior
                    enviar_dataa = False
                    patologico_anterior = patologico
                
            if frontend is not None:
                if websocket == frontend:
                    mensaje_frontend=data                

            if mensaje_frontend is not None:
                if frontend is not None:                    
                    
                    if 'patologia' in mensaje_frontend:

                        patologico=mensaje_frontend['patologia']
                        if patologico==False:
                            tipo="anatomia"
                        else:
                            tipo="patologia"

                        marcador=mensaje_frontend['marcador']

                        if mensaje_frontend['btn']=="" and mensaje_frontend['IDvideo']==0:
                            f=0
                            IDvideo=1
                        else:
                            f=mensaje_frontend['btn']
                            IDvideo=mensaje_frontend['IDvideo']
                        
                        
                        codigo_modo(f)
                        
                        lista_videos=listar_videos()
                        if mensaje_frontend['Nombre_movimiento']!="":
                            nombre=mensaje_frontend['Nombre_movimiento']

                        mensaje=dato
                        m=json.dumps(mensaje)
                        await frontend.send(m)

                        await asyncio.sleep(1)
    finally:
        # Remover cliente de la lista de clientes conectados cuando se desconecta
        frontend=None

# Iniciar el servidor WebSocket

keyboard.hook(custom_on_key_press)
start_server=websockets.serve(handle_client, "localhost", 8765) 
print("Servidor WebSocket iniciado en ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




