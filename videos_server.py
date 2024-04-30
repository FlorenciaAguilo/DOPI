import http.server
import socketserver

# Definir el directorio donde están almacenados los archivos multimedia
# Asegúrate de proporcionar la ruta correcta a tu carpeta de videos
DIRECTORIO_MULTIMEDIA = "Desktop\\simulador_edopi_backend"

# Definir el puerto en el que deseas que el servidor HTTP escuche las solicitudes
PUERTO_HTTP = 3000

# Crear una clase para manejar las solicitudes HTTP
class ManejadorHTTPRequest(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORIO_MULTIMEDIA, **kwargs)

# Configurar el servidor para escuchar en el puerto especificado
with socketserver.TCPServer(("", PUERTO_HTTP), ManejadorHTTPRequest) as httpd:
    print(f"Servidor HTTP iniciado en el puerto {PUERTO_HTTP}")
    # Mantener el servidor en funcionamiento hasta que se presione Ctrl+C
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

