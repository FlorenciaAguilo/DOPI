from flask import Flask, send_from_directory, request, Response
from flask_ngrok import run_with_ngrok
import os
from werkzeug.utils import secure_filename  # Agrega esta línea
import shutil

app = Flask(__name__)
run_with_ngrok(app)  # Crea un túnel con ngrok
marcador = 'APICAL'

# Ruta de la carpeta "Desktop" del usuario
desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop")

def cargar_archivos(marcador):
    
    base_folder = os.path.join(desktop_folder, f'simulador_edopi_backend\\{marcador}')
    # Recorre recursivamente la carpeta PEL
    for root, dirs, files in os.walk(base_folder):
        # Filtra solo las carpetas que contienen videos
        if any(file.endswith('.mp4') for file in files):
            # Recorre los archivos en la carpeta actual
            for file in files:
                # Si es un archivo de video, copia el archivo a la carpeta de carga
                if file.endswith('.mp4'):
                    video_path = os.path.join(root, file)
                    # Define la ruta de destino en la carpeta de carga
                    destination_path = os.path.join(UPLOAD_FOLDER, file)
                    print(destination_path)


# Ruta de la carpeta que contiene los archivos a subir
UPLOAD_FOLDER = os.path.join(desktop_folder, f'simulador_edopi_backend\\{marcador}')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route(f'/upload/{marcador}', methods=['POST'])
def upload_file():
    global marcador
    if 'file' not in request.files:
        return 'No se encontró ningún archivo en la solicitud', 400  # Bad Request
    file = request.files['file']
    if file.filename == '':
        return 'No se seleccionó ningún archivo', 400  # Bad Request
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'Archivo subido exitosamente', 200  # OK

@app.route('/videos/<path:filename>')
def download_file(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_video(video_path)

@app.route(f'/get_all_urls', methods=['GET'])
def get_all_urls():
    global marcador
    video_urls = []
    # Ruta base de la carpeta PEL
    base_folder = rf'C:\\Users\\AGUILÓ\\Desktop\\simulador_edopi_backend\\{marcador}'
    # Recorre recursivamente la carpeta PEL
    for root, dirs, files in os.walk(base_folder):
        # Filtra solo las carpetas que contienen videos
        if any(file.endswith('.mp4') for file in files):
            # Recorre los archivos en la carpeta actual
            for file in files:
                # Si es un archivo de video, agrega su URL a la lista
                if file.endswith('.mp4'):
                    video_path = os.path.join(root, file)
                    video_url = request.url_root + 'videos/' + os.path.relpath(video_path, base_folder)
                    video = video_url.replace("\\","/")
                    video = video.replace(" ","_")

                    video_urls.append(video)

    # Devuelve las URLs de los videos encontrados
    return '\n'.join(video_urls), 200

def send_video(video_path):
    video1 = video_path.replace("/","\\")
    # Obtén la parte del nombre de archivo después de "simulador_edopi_backend"
    nombre_archivo = video1.split("simulador_edopi_backend")[1]
    

    # Reemplaza los guiones bajos por espacios en el nombre del archivo
    nombre_archivo_con_espacios = nombre_archivo.replace("_", " ")
    parte_izquierda = video1.split("simulador_edopi_backend")[0]

    # Reconstruye la ruta completa con el nombre de archivo modificado
    ruta_con_espacios = parte_izquierda +"simulador_edopi_backend" + nombre_archivo_con_espacios
    def generate():
        with open(ruta_con_espacios, 'rb') as f:
            # Lee el video en bloques de 1024 bytes
            while True:
                video_chunk = f.read(1024)
                if not video_chunk:
                    break
                yield video_chunk

    # Devuelve el archivo de video con el tipo de contenido adecuado para que el navegador lo reproduzca
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    cargar_archivos(marcador)
    app.run()
