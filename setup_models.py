import urllib.request
import bz2
import os
import sys

# Configuración
MODEL_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
MODELS_DIR = os.path.join("app", "static", "models")
MODEL_FILENAME = "shape_predictor_68_face_landmarks.dat"
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)

def download_and_extract():
    # 1. Crear directorio si no existe
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"[INFO] Carpeta creada: {MODELS_DIR}")

    # 2. Verificar si ya existe el modelo
    if os.path.exists(MODEL_PATH):
        print(f"[INFO] El modelo ya existe en: {MODEL_PATH}")
        return

    print("[INFO] Iniciando descarga del Modelo de Predicción de Forma (99 MB)...")
    print("       Esto puede tardar unos minutos dependiendo de tu internet.")
    
    try:
        # Descargar el archivo comprimido (.bz2)
        bz2_filename = MODEL_FILENAME + ".bz2"
        bz2_path = os.path.join(MODELS_DIR, bz2_filename)
        
        urllib.request.urlretrieve(MODEL_URL, bz2_path)
        print("[INFO] Descarga completada.")

        # Descomprimir
        print("[INFO] Descomprimiendo archivo...")
        with bz2.BZ2File(bz2_path) as fr, open(MODEL_PATH, "wb") as fw:
            data = fr.read()
            fw.write(data)
        
        # Limpiar archivo comprimido
        os.remove(bz2_path)
        print(f"[EXITO] Modelo instalado correctamente en: {MODEL_PATH}")

    except Exception as e:
        print(f"[ERROR] Falló la descarga/instalación: {str(e)}")

if __name__ == "__main__":
    download_and_extract()