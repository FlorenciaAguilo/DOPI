import asyncio
import threading
import websockets
import keyboard
import json
import os
from evento_tecla import on_key_press
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
client={}

# Variable para almacenar el cliente frontend
frontend = None
transductor= None
directory_path=None
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
relative_directory=None

lista_videos={}


dato ={'dirVideo': ruta,'patologia': patologico,'status': prediccion,'Nombre_movimiento': nombre,'marcador': marcador,'IDvideo':IDvideo,'btn': f}


# Función de conversión para manejar listas
def convertir_a_lista(obj):
    if isinstance(obj, list):
        return {'__es_lista__': True, 'datos': obj}
    return obj

# Definir la función que se llamará después de handle_client
def continuar_despues_de_actualizar():
    global relative_directory
    global f,data,dato,ruta,modo,carpeta,IDvideo, IDvideo,marcador,patologico,nombre,tipo
    
    relative_directory = os.path.join(marcador, tipo, nombre, modo)
    
# Define una bandera para verificar si el mensaje ya se envió
enviar_dataa=True
patologico_anterior = None  # Variable para almacenar el valor anterior de patologico

def find_folder(folder_name, search_path=None):
    if search_path is None:
        search_path = os.path.join(os.path.expanduser("~"), "Desktop")  # Ruta al escritorio del usuario

    for root, dirs, files in os.walk(search_path):
        if folder_name in dirs:
            return os.path.abspath(os.path.join(root, folder_name))
    return None

def codigo_modo(codigo):
    global modo
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
    global modo, marcador, tipo, nombre, modo, lista_videos
    global relative_directory
    directorio_base = os.path.expanduser("~")  # Obtenemos el directorio base del usuario
    lista_carpetas = {}

    # Ruta base donde se encuentran las carpetas PEL
    ruta_base_pel = os.path.join(directorio_base, "Desktop", "simulador_edopi_backend", marcador)

    # Contador para asignar un número único a cada video
    video_count = 1

    # Recorremos las carpetas principales (anatomico, patologico) dentro de PEL
    for categoria in os.listdir(ruta_base_pel):
        ruta_categoria = os.path.join(ruta_base_pel, categoria)
        if os.path.isdir(ruta_categoria) and categoria == tipo:  # Solo para por el 'tipo' que es la pestaña activa. Por defecto es anatomia
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
                                    # Construir la URL del video con el número único en lugar del nombre del video
                                    subcarpeta = subcarpeta.replace(" ", "_")
                                    subcarpeta.replace("\\", "/")
                                    subcategoria = subcategoria.replace(" ", "_")
                                    categoria = categoria.replace(" ", "_")
                                    

                                    video_url = f"http://localhost:3000/{marcador}/{categoria}/{subcategoria}/{subcarpeta}/absolute_path/{video_count}"
                                    
                                    videos.append({
                                        "videoTitulo": video,
                                        #"dirVideo": os.path.join(ruta_subcarpeta, video),
                                        "video_url": video_url
                                    })
                                    video_count += 1  # Incrementar el contador para el próximo video
                            video_count = 1
                            lista_videos[subcarpeta] = videos
                    lista_carpetas[categoria][subcategoria] = lista_videos
                
    # Imprimimos la estructura de carpetas y videos
    # print(lista_carpetas)
    return lista_carpetas


    
def custom_on_key_press():
    global f, data, dato, ruta, modo, carpeta, IDvideo, marcador, patologico, nombre, tipo, prediccion
    prediccion, marcador, nombre, dato, patologico, f, tipo, carpeta, modo, IDvideo, ruta = on_key_press(
     prediccion, marcador, nombre, dato, patologico, f, tipo, carpeta, modo, IDvideo, ruta
    )


async def handle_client(websocket,path):
    global frontend, mensaje_frontend
    global f,data,dato,ruta,modo,carpeta,IDvideo, IDvideo,marcador,patologico,nombre,tipo
    global lista_videos, enviar_dataa, patologico_anterior,relative_directory
        # Define una función que pasa las variables globales a on_key_press

    try:
        async for message in websocket:            
            
            data=json.loads(message)
            #identifica al frontend
            if "frontClient" in message:
                message=json.loads(message)

                if message.get("frontClient") == True:
                    print("se conectó el frontend")
                    id_cliente = id(websocket)
                    client[id_cliente] = websocket
                    frontend = client[id_cliente]
                    await websocket.send("Solicitud recibida. Esperando mensajes:...")
                    
                    
            # Espera hasta recibir la información del marcador

            if 'marcador' in data:
                marcador = data['marcador']
                patologico= data['patologia']

                #if nombre is None and data['Nombre_movimiento']!="":
                nombre=data['Nombre_movimiento']
                
                if data['btn']=="" and data['IDvideo']==0:
                    f=0
                    IDvideo=1
                else:
                    f=data['btn']
                
                codigo_modo(f)
                continuar_despues_de_actualizar()
            
                # Si es la primera vez que se recibe el marcador o el valor de patologico ha cambiado
                if enviar_dataa or patologico != patologico_anterior:
                    if patologico == False:
                        tipo = "anatomia"
                    else:
                        tipo = "patologia"

                    lista_videos = listar_videos()
                    continuar_despues_de_actualizar()
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
                    lista_videos = listar_videos()
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

                        #lista_videos=listar_videos()
                        if mensaje_frontend['Nombre_movimiento']!="":
                            nombre=mensaje_frontend['Nombre_movimiento']
                        
                        custom_on_key_press()
                        continuar_despues_de_actualizar()

                        mensaje=dato
                        m=json.dumps(mensaje)
                        await frontend.send(m)

                        await asyncio.sleep(1)
    finally:
        # Remover cliente de la lista de clientes conectados cuando se desconecta
        frontend=None

# # Iniciar el servidor WebSocket

# keyboard.hook(custom_on_key_press)

# Definición del manejador de solicitudes HTTP para servir archivos estáticos
class MediaHTTPRequestHandler(SimpleHTTPRequestHandler):
    global f,data,dato,ruta,modo,carpeta, IDvideo,marcador,patologico,nombre,tipo
    global relative_directory
    continuar_despues_de_actualizar()
    def list_files_with_urls(self):
    # Especifica manualmente la ruta base que deseas utilizars
        # Utiliza la ruta base especificada en lugar del directorio actual
        files = os.listdir(self.directory)
        base_url = "http://localhost:3000/"
        files_with_urls = []
        file_id = 1
        for file in files:
            if os.path.isfile(os.path.join(self.directory, file)):
                file_name = file.replace(" ", "_")  # Reemplazar espacios por guiones bajos
                file_path = os.path.abspath(os.path.join(self.directory, file))  # Ruta absoluta del archivo
                # file_url = os.path.join(base_url, "absolute_path", str(file_id)).replace("\\", "/")
                            # Remover la parte de la ruta base del servidor HTTP de la ruta completa del archivo
                file_url = os.path.relpath(file_path, os.path.join(os.path.expanduser("~"), "Desktop", "simulador_edopi_backend"))
                file_url = os.path.dirname(file_url)
                file_url = os.path.join(base_url,file_url,"absolute_path", str(file_id))  # Construir la URL completa
                
                file_url = file_url.replace("\\", "/")  # Reemplazar las barras invertidas por barras inclinadas
                file_url = file_url.replace(" ", "_")
                files_with_urls.append({"id": file_id, "name": file_name, "url": file_url, "absolute_path": file_path})
                file_id += 1
        return files_with_urls

    def do_GET(self):
        global directory_path
        # Directorio base donde se encuentran los archivos multimedia
        folder_name = "simulador_edopi_backend"
        absolute_path = find_folder(folder_name)
        
        # Actualizar directory_path antes de servir la solicitud GET
        if relative_directory is not None:
            directory_path = os.path.join(absolute_path, relative_directory)
        else:
            directory_path = absolute_path
        
        continuar_despues_de_actualizar()
        name=nombre.replace(" ", "_")
        mode=modo.replace(" ", "_")
        # Actualizar la ruta base antes de obtener la lista de archivos
        self.directory = directory_path

        # Servir la solicitud GET para obtener la lista de archivos
        if self.path == f'/{marcador}/{tipo}/{name}/{mode}/':

            continuar_despues_de_actualizar()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files_with_urls = self.list_files_with_urls()
            response = json.dumps({"files": files_with_urls})
            self.wfile.write(response.encode('utf-8'))
        elif self.path.startswith(f'/{marcador}/{tipo}/{name}/{mode}/absolute_path/'):

            # Obtener el ID del archivo de la URL
            file_id = int(unquote(self.path.split('/')[-1]))  # Decodificar la URL y obtener el ID del archivo
            # Buscar el archivo por su ID en la lista de archivos con rutas absolutas
            for file_info in self.list_files_with_urls():
                if file_info['id'] == file_id:
                    # Devolver la ruta absoluta del archivo si se encuentra
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = json.dumps({"id": file_info['id'], "name": file_info['name'], "absolute_path": file_info['absolute_path']})
                    self.wfile.write(response.encode('utf-8'))
                    return
            # Devolver un mensaje de error si el archivo no se encuentra
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("File not found".encode('utf-8'))
        
        else:
            super().do_GET()

# Iniciar el servidor WebSocket
start_server = websockets.serve(handle_client, "localhost", 8765)
print("Servidor WebSocket iniciado en ws://localhost:8765")

# Iniciar el servidor HTTP en un hilo separado
def start_http_server():
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.shutdown()
        http_server.server_close()

http_server_port = 3000
http_server = HTTPServer(('localhost', http_server_port), lambda *args, **kwargs: MediaHTTPRequestHandler(*args, directory=directory_path, **kwargs))
print(f"Servidor HTTP iniciado en http://localhost:{http_server_port}")

http_thread = threading.Thread(target=start_http_server)
http_thread.start()

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    # Detener el servidor WebSocket y,
    # Detener el servidor HTTP
    http_server.shutdown()
    http_server.server_close()
    http_thread.join()
    start_server.ws_server.close()



