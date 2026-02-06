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


class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Agenda")
        self.geometry("1080x840")

        self.state = {
            "agenda": []
        }

        os.makedirs(resource_path("data/img"), exist_ok=True)

        if mode == "edit" and filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                self.state["agenda"] = datos.get("web", {}) \
                                            .get("index_page", {}) \
                                            .get("agenda", [])
                self.contenido_original = json.loads(json.dumps(self.state["agenda"]))

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_datos = DatosTab(self.notebook, self)
        self.notebook.add(self.tab_datos, text="Datos")

        footer = ttk.Frame(self)
        footer.pack(fill="x", side="bottom", pady=10)

        ttk.Button(
            footer,
            text="Instrucciones",
            command=self.tab_datos.instrucciones
        ).pack(side="left", padx=10)

        ttk.Button(
            footer,
            text="Guardar cambios",
            command=self.save_json
        ).pack(side="top", padx=10)

        if mode == "edit":
            self.tab_datos.set_data(self.state)

    def detectar_cambios(self, antes, despues):
        cambios = []
        if antes != despues:
            cambios.append("agenda")
        return cambios

    def save_json(self):
        ruta = resource_path("geoso2-web-template/json/web.json")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            datos_completos.setdefault("web", {})
            datos_completos["web"].setdefault("index_page", {})

            cambios = self.detectar_cambios(self.contenido_original, self.state["agenda"])

            if cambios:
                datos_completos["web"]["index_page"].setdefault("history", [])
                datos_completos["web"]["index_page"]["history"].append({
                    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "sections_changed": cambios,
                    "summary": "Actualización en agenda"
                })

            datos_completos["web"]["index_page"]["agenda"] = self.state["agenda"]

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frm, text="Imagen:").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_imagen = ttk.Entry(frm)
        self.entry_imagen.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Button(frm, text="Buscar", command=self.select_imagen).grid(row=0, column=2, padx=6)

        ttk.Label(frm, text="Título del evento:").grid(row=1, column=0, sticky="w", pady=4)
        self.text_titulo = tk.Text(frm, wrap="word", height=2)
        self.text_titulo.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="nw", pady=4)
        desc_frame = ttk.Frame(frm)
        desc_frame.grid(row=2, column=1, sticky="ew", pady=4)

        self.text_descripcion = tk.Text(desc_frame, wrap="word", height=4)
        self.text_descripcion.pack(side="left", fill="both", expand=True)

        scroll_desc = ttk.Scrollbar(desc_frame, orient="vertical", command=self.text_descripcion.yview)
        scroll_desc.pack(side="right", fill="y")
        self.text_descripcion.config(yscrollcommand=scroll_desc.set)

        ttk.Label(frm, text="Fecha:").grid(row=3, column=0, sticky="w", pady=4)
        self.entry_fecha = ttk.Entry(frm)
        self.entry_fecha.grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="Hora:").grid(row=4, column=0, sticky="w", pady=4)
        self.entry_hora = ttk.Entry(frm)
        self.entry_hora.grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="Lugar:").grid(row=5, column=0, sticky="w", pady=4)
        self.entry_lugar = ttk.Entry(frm)
        self.entry_lugar.grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="URL del enlace:").grid(row=6, column=0, sticky="w", pady=4)
        self.entry_link = ttk.Entry(frm)
        self.entry_link.grid(row=6, column=1, sticky="ew", pady=4)

        link_btns = ttk.Frame(frm)
        link_btns.grid(row=6, column=2, sticky="w")
        ttk.Button(link_btns, text="Probar", command=self.probar_enlace).pack(side="left", padx=3)
        ttk.Button(link_btns, text="Buscar archivo", command=self.select_file).pack(side="left", padx=3)

        ttk.Label(frm, text="Texto del enlace:").grid(row=7, column=0, sticky="w", pady=4)
        self.entry_texto_link = ttk.Entry(frm)
        self.entry_texto_link.grid(row=7, column=1, sticky="ew", pady=4)

        frm.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            frm,
            columns=("Imagen", "Título", "Fecha", "Lugar", "Link"),
            show="headings",
            height=10
        )
        self.tree.grid(row=10, column=0, columnspan=3, sticky="nsew")

        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Lugar", text="Lugar")
        self.tree.heading("Link", text="Link")

        frm.rowconfigure(10, weight=1)

    def select_file(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Documentos", "*.pdf;*.html;*.htm"), ("Todos", "*.*")]
        )
        if not ruta:
            return

        try:
            destino_dir = resource_path("geoso2-web-template/imput/docs/agenda")
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src, open(destino, "wb") as f_dst:
                f_dst.write(f_src.read())

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, f"../imput/docs/agenda/{nombre}")

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
            carpeta_destino = resource_path("geoso2-web-template/imput/img/agenda")
            os.makedirs(carpeta_destino, exist_ok=True)

            destino = os.path.join(carpeta_destino, nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((300, 300), Image.LANCZOS)

                canvas = Image.new("RGB", (300, 300), "white")
                x = (300 - img.width) // 2
                y = (300 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, f"../imput/img/agenda/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def probar_enlace(self):
        url = self.entry_link.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay URL para probar.")
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

    def add_item(self):
        evento = {
            "imagen": self.entry_imagen.get().strip(),
            "titulo": self.text_titulo.get("1.0", tk.END).strip(),
            "descripcion": self.text_descripcion.get("1.0", tk.END).strip(),
            "fecha": self.entry_fecha.get().strip(),
            "hora": self.entry_hora.get().strip(),
            "lugar": self.entry_lugar.get().strip(),
            "link": self.entry_link.get().strip(),
            "texto_link": self.entry_texto_link.get().strip()
        }

        if not evento["titulo"]:
            messagebox.showwarning("Aviso", "El título es obligatorio.")
            return

        self.controller.state["agenda"].append(evento)
        self.refresh_table()
        self.clear_fields()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.controller.state["agenda"][index]
        self.refresh_table()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["agenda"][index]

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, item["imagen"])

        self.text_titulo.delete("1.0", tk.END)
        self.text_titulo.insert("1.0", item["titulo"])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", item["descripcion"])

        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, item["fecha"])

        self.entry_hora.delete(0, tk.END)
        self.entry_hora.insert(0, item["hora"])

        self.entry_lugar.delete(0, tk.END)
        self.entry_lugar.insert(0, item["lugar"])

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, item["link"])

        self.entry_texto_link.delete(0, tk.END)
        self.entry_texto_link.insert(0, item["texto_link"])

        del self.controller.state["agenda"][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.controller.state["agenda"]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.controller.state["agenda"]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for e in self.controller.state["agenda"]:
            self.tree.insert(
                "",
                tk.END,
                values=(e["imagen"], e["titulo"], e["fecha"], e["lugar"], e["link"])
            )

    def clear_fields(self):
        self.entry_imagen.delete(0, tk.END)
        self.text_titulo.delete("1.0", tk.END)
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_hora.delete(0, tk.END)
        self.entry_lugar.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)
        self.entry_texto_link.delete(0, tk.END)

    def set_data(self, datos):
        self.controller.state["agenda"] = datos.get("agenda", [])
        self.refresh_table()

    def instrucciones(self):
        instrucciones = (
            "Instrucciones para la Agenda:\n\n"
            "1. Añadir eventos con imagen, título, descripción, fecha, hora, lugar y enlace.\n"
            "\n"
            "2. La imagen debe estar en formato PNG, JPG o GIF.\n"
            "\n"
            "3. El enlace puede ser un archivo PDF, HTML o una URL externa.\n"
            "\n"
            "4. Usa los botones para añadir, eliminar o mover eventos en la agenda.\n"
            "\n"
            "5. Pulsa en Guardar los cambios para guardar los cambios realizados."
        )
        messagebox.showinfo("Instrucciones", instrucciones)
