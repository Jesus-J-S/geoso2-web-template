import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
import shutil
from PIL import Image
import sys

def resource_path(relative_path):
    """Devuelve la ruta absoluta tanto en script como en ejecutable .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class NoticiasWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Noticias")
        self.geometry("980x640")

        self.state = {
            "noticias": []
        }

        os.makedirs(resource_path("geoso2-web-template/imput/img/noticias"), exist_ok=True)
        os.makedirs(resource_path("geoso2-web-template/imput/docs/noticias"), exist_ok=True)

        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                self.state["noticias"] = datos.get("web", {}) \
                                              .get("index_page", {}) \
                                              .get("noticias", [])

                self.contenido_original = json.loads(json.dumps(self.state["noticias"]))

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        self.tab_datos = DatosTab(self, self)
        self.tab_datos.pack(fill="both", expand=True)

        footer = ttk.Frame(self)
        footer.pack(fill="x", pady=10)

        ttk.Button(footer, text="Instrucciones",
                   command=self.tab_datos.instrucciones).pack(side="left", padx=10)

        ttk.Button(footer, text="Guardar cambios",
                   command=self.save_json).pack(side="top", pady=5)

        if mode == "edit":
            self.tab_datos.refresh_table()


    def detectar_cambios(self, antes, despues):
        cambios = []
        if antes != despues:
            cambios.append("noticias")
        return cambios


    def save_json(self):
        ruta = resource_path("geoso2-web-template/json/web.json")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            datos_completos.setdefault("web", {})
            datos_completos["web"].setdefault("index_page", {})

            cambios = self.detectar_cambios(self.contenido_original, self.state["noticias"])

            if cambios:
                datos_completos["web"]["index_page"].setdefault("history", [])
                datos_completos["web"]["index_page"]["history"].append({
                    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "sections_changed": cambios,
                    "summary": "Actualización en noticias"
                })

            datos_completos["web"]["index_page"]["noticias"] = self.state["noticias"]

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


class DatosTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.editing_index = None

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=6)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="w")
        self.entry_titulo = ttk.Entry(frm)
        self.entry_titulo.grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw")
        self.text_descripcion = tk.Text(frm, height=5)
        self.text_descripcion.grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Texto del enlace:").grid(row=3, column=0, sticky="w")
        self.entry_enlace_texto = ttk.Entry(frm)
        self.entry_enlace_texto.grid(row=3, column=1, sticky="ew")

        ttk.Label(frm, text="URL del enlace:").grid(row=4, column=0, sticky="w")
        self.entry_enlace_url = ttk.Entry(frm)
        self.entry_enlace_url.grid(row=4, column=1, sticky="ew")

        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=4, column=2, padx=6)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(frm, columns=("Imagen", "Título"), show="headings", height=12)
        self.tree.grid(row=6, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

    def select_file(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Documentos", "*.pdf *.html *.htm"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        try:
            destino_dir = resource_path("geoso2-web-template/imput/docs/noticias")
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            shutil.copy(ruta, destino)

            self.entry_enlace_url.delete(0, tk.END)
            self.entry_enlace_url.insert(0, f"../imput/docs/noticias/{nombre}")

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
            destino_dir = resource_path("geoso2-web-template/imput/img/noticias")
            os.makedirs(destino_dir, exist_ok=True)

            destino = os.path.join(destino_dir, nombre)

            # Miniatura 300x300
            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((300, 300), Image.LANCZOS)

                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, f"../imput/img/noticias/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def add_item(self):
        noticia = {
            "imagen": self.entry_imagen.get().strip(),
            "titulo": self.entry_titulo.get().strip(),
            "descripcion": self.text_descripcion.get("1.0", tk.END).strip(),
            "enlace": {
                "texto": self.entry_enlace_texto.get().strip(),
                "url": self.entry_enlace_url.get().strip()
            }
        }

        if not noticia["imagen"] or not noticia["titulo"] or not noticia["descripcion"]:
            messagebox.showwarning("Aviso", "Imagen, título y descripción son obligatorios.")
            return

        if self.editing_index is not None:
            self.controller.state["noticias"][self.editing_index] = noticia
            self.editing_index = None
        else:
            self.controller.state["noticias"].append(noticia)

        self.refresh_table()
        self.clear_fields()


    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        noticia = self.controller.state["noticias"][index]
        self.editing_index = index

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, noticia["imagen"])

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, noticia["titulo"])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", noticia["descripcion"])

        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_texto.insert(0, noticia["enlace"].get("texto", ""))

        self.entry_enlace_url.delete(0, tk.END)
        self.entry_enlace_url.insert(0, noticia["enlace"].get("url", ""))


    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.controller.state["noticias"][index]
        self.refresh_table()


    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state["noticias"]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])


    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["noticias"]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])


    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for elem in self.controller.state["noticias"]:
            self.tree.insert("", tk.END, values=(elem["imagen"], elem["titulo"]))


    def clear_fields(self):
        self.entry_imagen.delete(0, tk.END)
        self.entry_titulo.delete(0, tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_enlace_texto.delete(0, tk.END)
        self.entry_enlace_url.delete(0, tk.END)
        self.editing_index = None


    def instrucciones(self):
        instrucciones = (
            "Instrucciones para la sección de Noticias:\n\n"
            "1. Añadir Noticia:\n"
            "   - Rellena los campos de Imagen, Título, Descripción, Texto del enlace y URL del enlace.\n"
            "   - Haz clic en 'Añadir' para agregar la noticia a la lista.\n\n"
            "2. Editar Noticia:\n"
            "   - Selecciona una noticia de la tabla.\n"
            "   - Haz clic en 'Editar' para cargar sus datos en los campos.\n"
            "   - Modifica los campos según sea necesario y haz clic en 'Añadir' para guardar los cambios.\n\n"
            "3. Eliminar Noticia:\n"
            "   - Selecciona una noticia de la tabla y haz clic en 'Eliminar' para borrarla.\n\n"
            "4. Guardar Cambios:\n"
            "   - Una vez que hayas terminado de editar las noticias, haz clic en 'Guardar cambios' para actualizar el archivo JSON."
        )
        messagebox.showinfo("Instrucciones", instrucciones)
