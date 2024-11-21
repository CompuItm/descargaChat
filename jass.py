from flask import Flask, render_template, request, send_file
import os
from datetime import datetime
from chat_downloader import ChatDownloader
import json

app = Flask(__name__)

def obtener_nombre_archivo():
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"chat_{fecha_actual}.txt"
    version = 1
    directorio = "chats_descargados"

    # Crear el directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    nombre_completo = os.path.join(directorio, nombre_archivo)
    while os.path.isfile(nombre_completo):
        nombre_archivo = f"chat_{fecha_actual}_v{version}.txt"
        nombre_completo = os.path.join(directorio, nombre_archivo)
        version += 1

    return nombre_completo

def descargar_chat(url):
    downloader = ChatDownloader()
    chat = downloader.get_chat(url)
    chat_data = []
    
    for mensaje in chat:
        texto = mensaje.get("message", "")
        tiempo = mensaje.get("time_text", "0:00")
        chat_data.append({"tiempo": tiempo, "texto": texto})
    
    return chat_data

def guardar_chat_en_txt(chat_data):
    nombre_archivo = obtener_nombre_archivo()
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for mensaje in chat_data:
            archivo.write(f"[{mensaje['tiempo']}] {mensaje['texto']}\n")
    return nombre_archivo

@app.route("/", methods=["GET", "POST"])
def index():
    chat_data = []
    if request.method == "POST":
        url = request.form["url"]
        chat_data = descargar_chat(url)
    return render_template("index.html", chat_data=chat_data)

@app.route("/descargar_txt", methods=["POST"])
def descargar_txt():
    try:
        chat_data_json = request.form.get("chat_data")
        if not chat_data_json:
            return "No se recibió ningún dato para procesar", 400

        chat_data = json.loads(chat_data_json)

        nombre_archivo = guardar_chat_en_txt(chat_data)
        if not nombre_archivo or not os.path.isfile(nombre_archivo):
            return "Error: No se pudo generar el archivo", 500

        return send_file(
            os.path.abspath(nombre_archivo),
            as_attachment=True,
            download_name=os.path.basename(nombre_archivo),
            mimetype="text/plain"
        )

    except Exception as e:
        import traceback
        print("Error al procesar la descarga del archivo:")
        print(traceback.format_exc())
        return "Ocurrió un error al descargar el archivo", 500

if __name__ == "__main__":
    app.run(debug=True)
