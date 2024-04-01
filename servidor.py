import asyncio
import threading
import websockets
import keyboard
import json
import os

clientes = set()
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

IDvideo=0 # sirve para acceder a cada video en una carpeta dada
carpeta="" # sirve para acceder a la carpeta de videos de una vista en especifico
modo=""    #modo de la imagen 

contador=0

ruta=""
dato ={'dirVideo': ruta,'patologia': patologico,'status': prediccion,'Nombre_movimiento': nombre,'marcador': marcador,'IDvideo':IDvideo,'btn': f}
llaves_a_incluir = ['dirVideo', 'status', 'Nombre_movimiento','marcador']

def on_key_press(e):
    global f, data,dato, prediccion, nombre,marcador,modo,IDvideo,carpeta, ruta, contador,key_pressed, key_pressed1
    global cantidad_videos, inferior, superior, bandera,patologico,tipo
    contador=0    

# mPrediccion de vista. Permite identificar si el movimiento es valido o no
    if e.name=="f":
        prediccion=0
    if e.name=="g":
        prediccion=1

# Vistas

    if e.name=="1":
        marcador="PEL"
        nombre=""
        
    if e.name=="2":
        marcador="PEC"
        nombre=""
        
    if e.name=="3":
        marcador="APICAL"
        nombre=""
        
    if e.name=="4":
        marcador="SUBCOSTAL"
        nombre=""
        
    if e.name=="5":
        marcador="SET"
        nombre="SET"
        

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

    if patologico==False:
        tipo="anatomia"
    else:
        tipo="patologia"

    dato['btn']=f
    dato['status']=prediccion
    dato['marcador']=marcador
    dato['Nombre_movimiento']=nombre
    
    # data=dato
    
    if dato['patologia'] == False:
        tipo="anatomia"
    else:
        tipo="patologia"

    carpeta=marcador+"\\"+tipo+"\\"+nombre+"\\"+modo
    
    ruta=cargar_ML_plano(f"{IDvideo}"+f" {marcador}",carpeta)

    dato['dirVideo']=ruta
    dato['IDvideo']=IDvideo

# Función de conversión para manejar listas
def convertir_a_lista(obj):
    if isinstance(obj, list):
        return {'__es_lista__': True, 'datos': obj}
    return obj

#holaaaaaaaaaaa

# def cargar_ML_plano(clave,otracarpeta):
#     global cantidad_videos,superior
#     directorio_base = os.path.expanduser("~")  # Obtenemos el directorio base del usuario

#     escritorio = os.path.join(directorio_base, "Desktop\\simulador_edopi_backend"+"\\"+otracarpeta)
#     #"Desktop\BLE_imu_TaitBryan\Machine Learning + GIU"
#     cantidad_videos=contar_elementos_carpeta(escritorio)

#     superior=cantidad_videos
#     # Recorre los archivos en el directorio
#     for raiz, carpetas, archivos in os.walk(escritorio):
#         for nombre_archivo in archivos:
#             if clave in nombre_archivo:
#                 # Imprime el nombre completo del archivo que contiene la palabra buscada
#                 nombre_completo = os.path.join(raiz, nombre_archivo)
#                 return nombre_completo
#                 #print(nombre_completo)

def cargar_ML_plano(clave,otracarpeta):
    global cantidad_videos,superior
    directorio_base = os.path.expanduser("~")  # Obtenemos el directorio base del usuario

    escritorio = os.path.join(directorio_base, "Desktop\\simulador_edopi_backend"+"\\"+otracarpeta)
    #"Desktop\BLE_imu_TaitBryan\Machine Learning + GIU"
        # Verifica si la carpeta existe
    if not os.path.exists(escritorio):
        print(f"La carpeta '{escritorio}' no existe.")
        return None
    
    cantidad_videos=contar_elementos_carpeta(escritorio)
    
    superior=cantidad_videos
    # Recorre los archivos en el directorio
    for raiz, carpetas, archivos in os.walk(escritorio):
        for nombre_archivo in archivos:
            if clave in nombre_archivo:
                # Imprime el nombre completo del archivo que contiene la palabra buscada
                nombre_completo = os.path.join(raiz, nombre_archivo)
                return nombre_completo
                #print(nombre_completo)
        # Si no se encuentra el archivo, devuelve None
    print(f"No se encontró ningún archivo con la clave '{clave}' en la carpeta '{escritorio}'.")
    return None


def contar_elementos_carpeta(ruta):
    # Obtener la lista de archivos y carpetas en la ruta especificada
    elementos = os.listdir(ruta)
    # Contar el número total de elementos
    total_elementos = len(elementos)
    return total_elementos


async def enviar_mensaje_a_clientes(mensaje, clientes):
    # Iterar sobre los clientes conectados y enviar el mensaje a cada uno
    for cliente in clientes:
        await cliente.send(mensaje)


async def handle_client(websocket,path):
    global frontend,transductor, mensaje_frontend, mensaje_transductor,llaves_a_incluir,modo
    global f,data,dato, ruta,carpeta,IDvideo, superior, bandera,new,IDvideo,f,marcador,patologico
    clientes.add(websocket)



    # Modo 
    if f==0:
         #modo Bidimensional
        modo="Bidimensional"
    if f==1:
         #modo doppler color
        modo="Modo Doppler Color"
    if f==2:
         #modo doppler pulsado
        modo="Modo Doppler Pulsado"
    if f==3:
         #modo doppler continuo
        modo="Modo Doppler Continuo"
    if f==4:
         #modo doppler tisular
        modo="Modo Doppler Tisular"
    if f==5:
         #modo M
        modo="Modo M"


    #cliente_id=str()
    try:
        async for message in websocket:
            #message = json.loads(message)
            
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

                # else:
                #     if frontend!=websocket:
                #         print("Frontend aun no conectado")
                #         id_transductor=id(websocket)
                #         client[id_transductor]=websocket
                #         transductor= client[id_transductor]
                #         mensaje_transductor=data
                           
            if frontend is not None:
                if websocket == frontend:
                    mensaje_frontend=data                

            if mensaje_frontend is not None:
                if frontend is not None:                    
                    
                    #comparar mensajes
                    
                        # ruta=mensaje_transductor["dirVideo"]    
                        # mensaje_frontend["dirVideo"]=ruta
                        # mensaje_frontend['status']=mensaje_transductor['status']
                        # mensaje_frontend['Nombre_movimiento']=mensaje_transductor['Nombre_movimiento']
                    if 'patologia' in mensaje_frontend:
                        patologico=mensaje_frontend['patologia']                   
                        marcador=mensaje_frontend['marcador']              
                        IDvideo=mensaje_frontend['IDvideo']
                        f=mensaje_frontend['btn']

                        mensaje=dato
                        m=json.dumps(mensaje)
                        await frontend.send(m)

                        await asyncio.sleep(1)
    finally:
        # Remover cliente de la lista de clientes conectados cuando se desconecta
        #clientes.remove(websocket)
        frontend=None


# Iniciar el servidor WebSocket


keyboard.hook(on_key_press)
start_server=websockets.serve(handle_client, "localhost", 8765) 
print("Servidor WebSocket iniciado en ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()








    
