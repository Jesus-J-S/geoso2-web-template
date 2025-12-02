import shutil
import os

origen = ""
destino = "../imagenes/carousel"

os.makedirs(destino, exist_ok=True)

for archivo in os.listdir(origen):
    if archivo.lower().endswith((".jpg", ".png", ".jpeg")):
        ruta_origen = os.path.join(origen, archivo)
        ruta_destino = os.path.join(destino, archivo)
        shutil.copy(ruta_origen, ruta_destino)