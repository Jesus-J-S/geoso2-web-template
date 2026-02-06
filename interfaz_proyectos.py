import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import webbrowser
from PIL import Image
import sys

def resource_path(relative_path):
    """Devuelve la ruta absoluta tanto en script como en ejecutable .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class EditorProyectosWindow(tk.Toplevel):
    def __init__(self, filepath=None):
        super().__init__()
        self.title("Editor de Proyectos")
        self.geometry("1100x700")

        self.filepath = filepath

        self.state = {
            "proyectos": {
                "encurso": [],
                "anteriores": [],
                "trabajosacademicos": []
            }
        }

        if filepath and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                datos = json.load(f)

            self.state["proyectos"] = datos.get("web", {}).get(
                "proyectos",
                {
                    "encurso": [],
                    "anteriores": [],
                    "trabajosacademicos": []
                }
            )

            self.contenido_original = json.loads(json.dumps(self.state["proyectos"]))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = {}

        for categoria, nombre in [
            ("encurso", "En curso"),
            ("anteriores", "Anteriores"),
            ("trabajosacademicos", "Trabajos académicos")
        ]:
            tab = DatosTab(self.notebook, self, categoria)
            self.notebook.add(tab, text=nombre)
            self.tabs[categoria] = tab

        footer = ttk.Frame(self)
        footer.pack(fill="x", pady=10)

        ttk.Button(
            footer,
            text="Instrucciones",
            command=self.mostrar_instrucciones
        ).pack(side="left", padx=10)

        ttk.Button(
            footer,
            text="Guardar cambios",
            command=self.save_json
        ).pack(side="top", pady=5)

        for tab in self.tabs.values():
            tab.refresh_table()


    def mostrar_instrucciones(self):
        instrucciones = (
            "Editor de Proyectos:\n\n"
            "• Cada pestaña representa una categoría: En curso, Anteriores y Trabajos académicos.\n"
            "• Puedes añadir, editar, eliminar, mover y reordenar proyectos.\n"
            "• El botón 'Mover a…' permite enviar un proyecto a otra categoría.\n"
            "• Las imágenes se redimensionan automáticamente a 300×300.\n"
            "• Los documentos se copian a la carpeta correspondiente.\n"
            "• Usa 'Guardar cambios' para actualizar el archivo JSON."
        )
        messagebox.showinfo("Instrucciones", instrucciones)


    def detectar_cambios(self, antes, despues):
        cambios = []

        for key in ["encurso", "anteriores", "trabajosacademicos"]:
            if antes.get(key) != despues.get(key):
                cambios.append(key)

        return cambios

    def save_json(self):
        ruta = resource_path("geoso2-web-template/json/web.json")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            datos_completos.setdefault("web", {})
            datos_completos["web"].setdefault("proyectos", {})

            cambios = self.detectar_cambios(self.contenido_original, self.state["proyectos"])

            if cambios:
                datos_completos["web"]["proyectos"].setdefault("history", [])
                datos_completos["web"]["proyectos"]["history"].append({
                    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "sections_changed": cambios,
                    "summary": "Actualización en proyectos"
                })

            datos_completos["web"]["proyectos"] = self.state["proyectos"]

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", "Proyectos actualizados correctamente.")

            self.contenido_original = json.loads(json.dumps(self.state["proyectos"]))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


class DatosTab(ttk.Frame):
    def __init__(self, parent, controller, categoria):
        super().__init__(parent)
        self.controller = controller
        self.categoria = categoria
        self.editing_index = None

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew")
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=6)

        ttk.Label(frm, text="Título:").grid(row=1, column=0, sticky="nw")
        self.text_titulo = tk.Text(frm, height=3)
        self.text_titulo.grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw")
        self.text_descripcion = tk.Text(frm, height=6)
        self.text_descripcion.grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Link:").grid(row=3, column=0, sticky="w")
        self.entry_link = ttk.Entry(frm)
        self.entry_link.grid(row=3, column=1, sticky="ew")

        ttk.Button(frm, text="Probar", command=self.probar_link).grid(row=3, column=2, padx=6)
        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=3, column=3, padx=6)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Mover a…", command=self.mover_a).pack(side="left", padx=5)

        self.tree = ttk.Treeview(frm, columns=("Imagen", "Título", "Link"), show="headings", height=12)
        self.tree.grid(row=5, column=0, columnspan=4, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Link", text="Link")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(5, weight=1)

    def select_file(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Documentos", "*.pdf *.html *.htm"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        try:
            destino_dir = resource_path("geoso2-web-template/imput/docs/proyectos")
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            shutil.copy(ruta, destino)

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, f"../imput/docs/proyectos/{nombre}")

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
            destino_dir = resource_path("geoso2-web-template/imput/img/proyectos")
            os.makedirs(destino_dir, exist_ok=True)

            destino = os.path.join(destino_dir, nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((300, 300), Image.LANCZOS)

                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, f"../imput/img/proyectos/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def add_item(self):
        data = {
            "imagen": self.entry_imagen.get().strip(),
            "titulo": self.text_titulo.get("1.0", tk.END).strip(),
            "descripcion": self.text_descripcion.get("1.0", tk.END).strip(),
            "link": self.entry_link.get().strip()
        }

        if not data["imagen"] or not data["titulo"] or not data["descripcion"]:
            messagebox.showwarning("Aviso", "Imagen, título y descripción son obligatorios.")
            return

        self.controller.state["proyectos"][self.categoria].append(data)

        self.refresh_table()
        self.clear_fields()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        self.editing_index = index

        data = self.controller.state["proyectos"][self.categoria][index]

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, data["imagen"])

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", data["titulo"])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", data["descripcion"])

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, data["link"])

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.controller.state["proyectos"][self.categoria][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        arr = self.controller.state["proyectos"][self.categoria]

        if index == 0:
            return

        arr[index - 1], arr[index] = arr[index], arr[index - 1]
        self.refresh_table()

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        arr = self.controller.state["proyectos"][self.categoria]

        if index == len(arr) - 1:
            return

        arr[index + 1], arr[index] = arr[index], arr[index + 1]
        self.refresh_table()

    def mover_a(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        proyecto = self.controller.state["proyectos"][self.categoria][index]

        popup = tk.Toplevel(self)
        popup.title("Mover a…")
        popup.geometry("300x150")

        ttk.Label(popup, text="Selecciona categoría destino:").pack(pady=10)

        destino_var = tk.StringVar()
        combo = ttk.Combobox(
            popup,
            textvariable=destino_var,
            values=["encurso", "anteriores", "trabajosacademicos"],
            state="readonly"
        )
        combo.pack(pady=5)

        def confirmar():
            destino = destino_var.get()
            if not destino:
                return

            del self.controller.state["proyectos"][self.categoria][index]

            self.controller.state["proyectos"][destino].insert(0, proyecto)

            for tab in self.controller.tabs.values():
                tab.refresh_table()

            popup.destroy()

        ttk.Button(popup, text="Mover", command=confirmar).pack(pady=10)

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for elem in self.controller.state["proyectos"][self.categoria]:
            self.tree.insert("", tk.END, values=(elem["imagen"], elem["titulo"], elem["link"]))

    def clear_fields(self):
        self.entry_imagen.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_link.delete(0, tk.END)
        self.editing_index = None

    def probar_link(self):
        url = self.entry_link.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "No hay ningún enlace para probar.")
            return

        try:
            if url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                ruta = os.path.abspath(resource_path(url))
                if os.path.exists(ruta):
                    webbrowser.open_new_tab(f"file:///{ruta}")
                else:
                    messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")
