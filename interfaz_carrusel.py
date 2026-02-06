import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import platform
import subprocess
import webbrowser
import shutil
from PIL import Image, ImageDraw
import sys


def resource_path(relative_path):
    """Devuelve la ruta absoluta tanto en script como en ejecutable .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class CarruselWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Carrusel JSON")
        self.geometry("980x640")

        # Estado
        self.state = {
            "carrusel": []
        }

        os.makedirs(resource_path("geoso2-web-template/imput/img/carrusel"), exist_ok=True)

        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                self.state["carrusel"] = datos.get("web", {}) \
                                              .get("index_page", {}) \
                                              .get("carrusel", [])

                self.contenido_original = json.loads(json.dumps(self.state["carrusel"]))

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_datos = DatosTab(self.notebook, self)
        self.notebook.add(self.tab_datos, text="Datos")

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", pady=10)

        ttk.Button(bottom_frame, text="Instrucciones",
                   command=self.tab_datos.instrucciones).pack(side="left", padx=10)

        ttk.Button(bottom_frame, text="Guardar cambios",
                   command=self.save_json).pack(side="top", pady=5)

        if mode == "edit":
            self.tab_datos.refresh_table()

    def detectar_cambios(self, antes, despues):
        cambios = []
        if antes != despues:
            cambios.append("carrusel")
        return cambios

    def save_json(self):
        ruta = resource_path("geoso2-web-template/json/web.json")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            datos_completos.setdefault("web", {})
            datos_completos["web"].setdefault("index_page", {})

            cambios = self.detectar_cambios(self.contenido_original, self.state["carrusel"])

            if cambios:
                datos_completos["web"]["index_page"].setdefault("history", [])
                datos_completos["web"]["index_page"]["history"].append({
                    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "sections_changed": cambios,
                    "summary": "Actualización en carrusel"
                })

            datos_completos["web"]["index_page"]["carrusel"] = self.state["carrusel"]

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

            self.contenido_original = json.loads(json.dumps(self.state["carrusel"]))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


class DatosTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=8)

        ttk.Label(frm, text="Enlace:").grid(row=1, column=0, sticky="w")
        self.entry_enlace = ttk.Entry(frm)
        self.entry_enlace.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=1, column=2, padx=8)

        frm.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Crear plantilla 2700x700",
                   command=self.crear_plantilla).pack(side="right", padx=5)

        self.tree = ttk.Treeview(frm, columns=("Imagen", "Enlace"), show="headings", height=12)
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Enlace", text="Enlace")

        frm.rowconfigure(3, weight=1)

    def select_file(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Documentos", "*.pdf;*.html;*.htm"),
                ("PDF", "*.pdf"),
                ("HTML", "*.html;*.htm"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        try:
            destino_dir = resource_path("geoso2-web-template/imput/docs/carrusel")
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src, open(destino, "wb") as f_dst:
                f_dst.write(f_src.read())

            self.entry_enlace.delete(0, tk.END)
            self.entry_enlace.insert(0, f"../imput/docs/carrusel/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")


    def select_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not ruta:
            return

        try:
            nombre = os.path.basename(ruta)
            carpeta_destino = resource_path("geoso2-web-template/imput/img/carrusel")
            os.makedirs(carpeta_destino, exist_ok=True)

            destino = os.path.join(carpeta_destino, nombre)
            shutil.copy(ruta, destino)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, f"../imput/img/carrusel/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")


    def add_item(self):
        imagen = self.entry_imagen.get().strip()
        enlace = self.entry_enlace.get().strip()

        if not imagen or not enlace:
            messagebox.showwarning("Aviso", "Debes seleccionar una imagen y escribir un enlace.")
            return

        self.controller.state["carrusel"].append({
            "imagen": imagen,
            "enlace": enlace
        })

        self.refresh_table()
        self.entry_imagen.delete(0, tk.END)
        self.entry_enlace.delete(0, tk.END)


    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["carrusel"][index]
        self.refresh_table()


    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["carrusel"]

        if index > 0:
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])


    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["carrusel"]

        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])


    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["carrusel"][index]

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, item["imagen"])

        self.entry_enlace.delete(0, tk.END)
        self.entry_enlace.insert(0, item["enlace"])

        del self.controller.state["carrusel"][index]
        self.refresh_table()


    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for elem in self.controller.state["carrusel"]:
            self.tree.insert("", tk.END, values=(elem["imagen"], elem["enlace"]))


    def set_data(self, datos):
        self.controller.state["carrusel"] = datos.get("carrusel", [])
        self.refresh_table()


    def crear_plantilla(self):
        try:
            carpeta_destino = filedialog.askdirectory(
                title="Selecciona donde guardar la plantilla"
            )

            ruta = os.path.join(carpeta_destino, "plantilla_carrusel.png")

            img = Image.new("RGB", (2700, 700), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), "Plantilla 2700x700", fill=(80, 80, 80))

            img.save(ruta)

            messagebox.showinfo("Plantilla creada", "Se ha generado una plantilla 2700x700.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la plantilla:\n{e}")


    def instrucciones(self):
        instrucciones = (
            "Instrucciones para el Carrusel:\n\n"
            "1. Añadir imágenes y enlaces para el carrusel de la página principal.\n"
            "\n"
            "2. Las imágenes deben estar en formato PNG, JPG o GIF.\n"
            "(Se recomienda una resolución de 2700x700 píxeles)\n"
            "\n"
            "3. Los enlaces pueden ser archivos PDF o HTML.\n"
            "\n"
            "4. Usa los botones para añadir, eliminar o mover elementos en el carrusel.\n"
            "\n"
            "5. Pulsa en Guardar los cambios para guardar los cambios realizados."
        )
        messagebox.showinfo("Instrucciones", instrucciones)
