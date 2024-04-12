import asyncio
import threading
import websockets
import keyboard
import json
import os

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

IDvideo=0  # sirve para acceder a cada video en una carpeta dada
carpeta="" # sirve para acceder a la carpeta de videos de una vista, un modo y un movmiento especifico 
modo=""    # modo de la imagen 

superior=0

cantidad_videos=0
nombre_archivos=""
nombre_modos=""

lista_videos=[]

ruta=""
dato ={'dirVideo': ruta,'patologia': patologico,'status': prediccion,'Nombre_movimiento': nombre,'marcador': marcador,'IDvideo':IDvideo,'btn': f}

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

def on_key_press(e):
    global f, data,dato, prediccion, nombre,marcador,modo,IDvideo,carpeta, ruta, contador,key_pressed, key_pressed1
    global cantidad_videos, inferior, superior, bandera,patologico,tipo,superior,nombre_archivos,nombre_modos
    global diccionaro_videos,lista_videos
    contador=0    

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
    

    
    # data=dato
    
    # if dato['patologia'] == False:
    #     tipo="anatomia"
    # else:
    #     tipo="patologia"

    carpeta=marcador+"\\"+tipo+"\\"+nombre+"\\"+modo
    ruta=cargar_ML_plano(f"{IDvideo}"+f" {marcador}",carpeta)
    

    dato['dirVideo']=ruta
    dato['IDvideo']=IDvideo
    
    # if superior!=0 and nombre_archivos!="":
    #     print("Número total de elementos:", superior)
    #     print("Nombres de elementos:", nombre_archivos)
    
# Función de conversión para manejar listas
def convertir_a_lista(obj):
    if isinstance(obj, list):
        return {'__es_lista__': True, 'datos': obj}
    return obj

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
    
def cargar_ML_plano(clave,otracarpeta):
    global cantidad_videos,superior,nombre_archivos,nombre_modos, marcador,tipo,nombre
    global lista_videos
    directorio_base = os.path.expanduser("~")  # Obtenemos el directorio base del usuario
    escritorio = os.path.join(directorio_base, "Desktop\\simulador_edopi_backend"+"\\"+otracarpeta)
    
    # Verifica si la carpeta existe
    if not os.path.exists(escritorio):
        return None

    modoss=os.path.join(directorio_base,"Desktop\\simulador_edopi_backend"+"\\"+marcador+"\\"+tipo+"\\"+nombre)
    ele,car=contar_elementos_carpeta(modoss)
    nombre_modos=car
        
    # Recorre los archivos en el directorio
    for raiz, carpetas, archivos in os.walk(escritorio):
        superior=len(archivos)
        nombre_archivos=archivos
        for nombre_archivo in archivos:
            if clave in nombre_archivo:
                # Imprime el nombre completo del archivo que contiene la palabra buscada
                nombre_completo = os.path.join(raiz, nombre_archivo)
                return nombre_completo
                #print(nombre_completo)
        # Si no se encuentra el archivo, devuelve None
    #print(f"No se encontró ningún archivo con la clave '{clave}' en la carpeta '{escritorio}'.")
    return None


def contar_elementos_carpeta(ruta):
    # Obtener la lista de archivos y carpetas en la ruta especificada
    elementos = os.listdir(ruta)
    # Contar el número total de elementos
    total_elementos = len(elementos)
    return total_elementos,elementos


async def enviar_mensaje_a_clientes(mensaje, clientes):
    # Iterar sobre los clientes conectados y enviar el mensaje a cada uno
    for cliente in clientes:
        await cliente.send(mensaje)


async def handle_client(websocket,path):
    global frontend,transductor, mensaje_frontend, mensaje_transductor,llaves_a_incluir,modo
    global f,data,dato, ruta,carpeta,IDvideo, superior, bandera,new,IDvideo,f,marcador,patologico,nombre
    global nombre_archivos,nombre_modos,tipo
    global lista_videos, enviar_dataa, patologico_anterior

    try:
        async for message in websocket:            
            
            data=json.loads(message)

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

keyboard.hook(on_key_press)
start_server=websockets.serve(handle_client, "localhost", 8765) 
print("Servidor WebSocket iniciado en ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




