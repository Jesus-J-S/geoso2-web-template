import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import datetime
import webbrowser
from PIL import Image
from jinja2 import Environment, FileSystemLoader
import sys


def resource_path(relative_path):
    """Devuelve la ruta absoluta tanto en script como en ejecutable .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class paginaWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Página Web")
        self.geometry("1100x950")

        self.ruta_web_json = resource_path("geoso2-web-template/json/web.json")
        self.carpeta_imagenes = resource_path(os.path.join("geoso2-web-template", "imput", "img", "paginas"))
        os.makedirs(os.path.dirname(self.ruta_web_json), exist_ok=True)
        os.makedirs(self.carpeta_imagenes, exist_ok=True)

        self.state = {
            "id": None,
            "portada": "",
            "titulo": "",
            "cuerpo": [],
            "autor": "",
            "fecha": "",
        }

        self._build_ui()

        if mode == "edit" and filepath:
            self.load_page_from_file(filepath)
        self.contenido_original = json.loads(json.dumps(self.state))


    def _build_ui(self):
        frm_datos = ttk.LabelFrame(self, text="Datos")
        frm_datos.pack(fill="x", padx=12, pady=10)

        ttk.Label(frm_datos, text="Portada:").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_portada = ttk.Entry(frm_datos)
        self.entry_portada.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(frm_datos, text="Buscar", command=self.select_portada).grid(row=0, column=2, padx=8)

        ttk.Label(frm_datos, text="Título:").grid(row=1, column=0, sticky="nw", pady=6)
        self.texto_titulo = tk.Text(frm_datos, height=4, wrap="word")
        self.texto_titulo.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frm_datos, text="Autor:").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_autor = ttk.Entry(frm_datos)
        self.entry_autor.grid(row=2, column=1, sticky="ew", pady=6)

        frm_datos.columnconfigure(1, weight=1)

        frm_cuerpo = ttk.LabelFrame(self, text="Cuerpo de la página")
        frm_cuerpo.pack(fill="both", expand=True, padx=12, pady=10)

        ttk.Label(frm_cuerpo, text="Párrafo:").grid(row=0, column=0, sticky="nw")
        self.texto_parrafo = tk.Text(frm_cuerpo, height=10, wrap="word")
        self.texto_parrafo.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(frm_cuerpo, text="Enlace:").grid(row=1, column=0, sticky="w")
        self.entry_enlace = ttk.Entry(frm_cuerpo)
        self.entry_enlace.grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(frm_cuerpo, text="Probar", command=self.probar_enlace).grid(row=1, column=2, padx=8)

        ttk.Label(frm_cuerpo, text="Texto del enlace:").grid(row=2, column=0, sticky="w")
        self.entry_texto_enlace = ttk.Entry(frm_cuerpo)
        self.entry_texto_enlace.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(frm_cuerpo, text="Imagen:").grid(row=3, column=0, sticky="w")
        self.entry_imagen = ttk.Entry(frm_cuerpo)
        self.entry_imagen.grid(row=3, column=1, sticky="ew", pady=6)
        ttk.Button(frm_cuerpo, text="Buscar", command=self.select_imagen).grid(row=3, column=2, padx=8)

        ttk.Label(frm_cuerpo, text="Pie de imagen:").grid(row=4, column=0, sticky="nw")
        self.texto_pie = tk.Text(frm_cuerpo, height=3, wrap="word")
        self.texto_pie.grid(row=4, column=1, sticky="ew", pady=6)

        btns = ttk.Frame(frm_cuerpo)
        btns.grid(row=5, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text="Añadir", command=self.add_block).pack(side="left", padx=5)
        ttk.Button(btns, text="Editar", command=self.edit_block).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar", command=self.delete_block).pack(side="left", padx=5)
        ttk.Button(btns, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btns, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            frm_cuerpo,
            columns=("Párrafo", "Imagen", "Pie", "Enlace", "Texto enlace"),
            show="headings",
            height=6
        )
        self.tree.grid(row=6, column=0, columnspan=3, sticky="nsew")
        self.tree.heading("Párrafo", text="Párrafo")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.heading("Pie", text="Pie de imagen")
        self.tree.heading("Enlace", text="Enlace")
        self.tree.heading("Texto enlace", text="Texto del enlace")

        frm_cuerpo.columnconfigure(1, weight=1)
        frm_cuerpo.rowconfigure(6, weight=1)

        frm_opciones = ttk.LabelFrame(self, text="Opciones")
        frm_opciones.pack(fill="x", padx=12, pady=10)

        ttk.Button(frm_opciones, text="Guardar", command=self.save_json).pack(side="left", padx=5)
        ttk.Button(frm_opciones, text="Instrucciones", command=self.show_instructions).pack(side="left", padx=5)
        ttk.Button(frm_opciones, text="Ver páginas creadas", command=self.show_pages_window).pack(side="left", padx=5)
        ttk.Button(frm_opciones, text="Previsualizar en HTML", command=self.preview_web).pack(side="right", padx=5)

    def _load_web_data(self):
        if not os.path.exists(self.ruta_web_json):
            return {"web": {"paginas": []}}
        try:
            with open(self.ruta_web_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "web" not in data:
                data["web"] = {}
            if "paginas" not in data["web"]:
                data["web"]["paginas"] = []
            return data
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer web.json:\n{e}")
            return {"web": {"paginas": []}}

    def _save_web_data(self, data):
        try:
            with open(self.ruta_web_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar web.json:\n{e}")

    def _generate_new_id(self, paginas):
        max_num = 0
        for p in paginas:
            pid = p.get("id", "")
            if pid.startswith("pagina_"):
                try:
                    num = int(pid.split("_")[1])
                    if num > max_num:
                        max_num = num
                except Exception:
                    continue
        nuevo = max_num + 1
        return f"pagina_{nuevo:03d}"


    def load_page_from_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.state.update(datos)
            self.refresh_fields()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la página:\n{e}")

    def refresh_fields(self):
        self.entry_portada.delete(0, tk.END)
        self.entry_portada.insert(0, self.state.get("portada", ""))

        self.texto_titulo.delete("1.0", tk.END)
        self.texto_titulo.insert("1.0", self.state.get("titulo", ""))

        self.entry_autor.delete(0, tk.END)
        self.entry_autor.insert(0, self.state.get("autor", ""))

    def update_state(self):
        self.state["portada"] = self.entry_portada.get().strip()
        self.state["titulo"] = self.texto_titulo.get("1.0", tk.END).strip()
        self.state["autor"] = self.entry_autor.get().strip()

    def select_portada(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not ruta:
            return
        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join(self.carpeta_imagenes, nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((615, 350), Image.LANCZOS)
                canvas = Image.new("RGB", (615, 350), "white")
                x = (615 - img.width) // 2
                y = (350 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            ruta_rel = f"../imput/img/paginas/{nombre}"
            self.entry_portada.delete(0, tk.END)
            self.entry_portada.insert(0, ruta_rel)
            self.state["portada"] = ruta_rel

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def select_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not ruta:
            return
        try:
            nombre = os.path.basename(ruta)
            destino = os.path.join(self.carpeta_imagenes, nombre)

            with Image.open(ruta) as img:
                img = img.convert("RGB")
                img.thumbnail((615, 350), Image.LANCZOS)
                canvas = Image.new("RGB", (615, 350), "white")
                x = (615 - img.width) // 2
                y = (350 - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(destino, quality=90)

            ruta_rel = f"../imput/img/paginas/{nombre}"
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, ruta_rel)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{e}")

    def add_block(self):
        bloque = {
            "texto": self.texto_parrafo.get("1.0", tk.END).strip(),
            "imagen": self.entry_imagen.get().strip(),
            "pie_imagen": self.texto_pie.get("1.0", tk.END).strip(),
            "enlace": self.entry_enlace.get().strip(),
            "texto_enlace": self.entry_texto_enlace.get().strip()
        }
        if not bloque["texto"] and not bloque["imagen"]:
            messagebox.showwarning("Aviso", "Debes añadir al menos texto o imagen.")
            return

        self.state["cuerpo"].append(bloque)
        self.refresh_table()

        self.texto_parrafo.delete("1.0", tk.END)
        self.entry_imagen.delete(0, tk.END)
        self.entry_enlace.delete(0, tk.END)
        self.entry_texto_enlace.delete(0, tk.END)
        self.texto_pie.delete("1.0", tk.END)

    def delete_block(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.state["cuerpo"][index]
        self.refresh_table()

    def edit_block(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        bloque = self.state["cuerpo"][index]

        self.texto_parrafo.delete("1.0", tk.END)
        self.texto_parrafo.insert("1.0", bloque.get("texto", ""))

        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, bloque.get("imagen", ""))

        self.texto_pie.delete("1.0", tk.END)
        self.texto_pie.insert("1.0", bloque.get("pie_imagen", ""))

        self.entry_enlace.delete(0, tk.END)
        self.entry_enlace.insert(0, bloque.get("enlace", ""))

        self.entry_texto_enlace.delete(0, tk.END)
        self.entry_texto_enlace.insert(0, bloque.get("texto_enlace", ""))

        del self.state["cuerpo"][index]
        self.refresh_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        if index > 0:
            arr = self.state["cuerpo"]
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        arr = self.state["cuerpo"]
        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for bloque in self.state["cuerpo"]:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    bloque.get("texto", ""),
                    bloque.get("imagen", ""),
                    bloque.get("pie_imagen", ""),
                    bloque.get("enlace", ""),
                    bloque.get("texto_enlace", "")
                )
            )

    def probar_enlace(self):
        url = self.entry_enlace.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay ninguna URL para probar.")
            return
        try:
            if url.endswith(".html"):
                ruta_absoluta = os.path.abspath(url)
                if os.path.exists(ruta_absoluta):
                    webbrowser.open_new_tab(f"file:///{ruta_absoluta}")
                else:
                    messagebox.showerror("Error", f"No se encontró el archivo HTML:\n{ruta_absoluta}")
            elif url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                messagebox.showerror("Error", "El enlace debe ser una URL válida o un archivo .html del proyecto.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

    def detectar_cambios(self, antes, despues):
        cambios = []

        for campo in ["portada", "titulo", "autor"]:
            if antes.get(campo) != despues.get(campo):
                cambios.append(campo)

        if antes.get("cuerpo") != despues.get("cuerpo"):
            cambios.append("cuerpo")

        return cambios

    def save_json(self):
        self.update_state()
        datos = self.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")

        if not datos["titulo"].strip():
            messagebox.showerror("Error", "La página debe tener un título.")
            return

        data = self._load_web_data()
        paginas = data["web"]["paginas"]

        cambios = self.detectar_cambios(self.contenido_original, datos)

        if cambios:
            datos.setdefault("history", [])
            datos["history"].append({
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "sections_changed": cambios,
                "summary": "Actualización en página web"
            })

        if datos.get("id"):
            encontrado = False
            for i, p in enumerate(paginas):
                if p.get("id") == datos["id"]:
                    paginas[i] = datos
                    encontrado = True
                    break
            if not encontrado:
                paginas.append(datos)
        else:
            nuevo_id = self._generate_new_id(paginas)
            datos["id"] = nuevo_id
            self.state["id"] = nuevo_id
            paginas.append(datos)

        data["web"]["paginas"] = paginas
        self._save_web_data(data)

        self.contenido_original = json.loads(json.dumps(datos))

        messagebox.showinfo("Guardado", "Página guardada en web.json")


    def preview_web(self):
        self.update_state()
        datos = self.state.copy()
        datos["fecha"] = datetime.datetime.now().strftime("%d-%m-%Y")

        portada = datos.get("portada", "")
        if portada:
            datos["portada"] = portada.replace("\\", "/")
        else:
            datos["portada"] = ""

        cuerpo_ajustado = []
        for bloque in datos.get("cuerpo", []):
            nuevo = bloque.copy()
            if nuevo.get("imagen"):
                nuevo["imagen"] = nuevo["imagen"].replace("\\", "/")
            cuerpo_ajustado.append(nuevo)

        datos["cuerpo"] = cuerpo_ajustado

        try:
            env = Environment(loader=FileSystemLoader("geoso2-web-template/templates"))
            template = env.get_template("pagina.html")
            html = template.render(pagina=datos)

            ruta = resource_path("geoso2-web-template/data/preview_pagina.html")
            os.makedirs(resource_path("geoso2-web-template/data"), exist_ok=True)

            with open(ruta, "w", encoding="utf-8") as f:
                f.write(html)

            webbrowser.open_new_tab(f"file:///{os.path.abspath(ruta)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el preview HTML:\n{e}")

    def show_pages_window(self):
        data = self._load_web_data()
        paginas = data["web"]["paginas"]

        win = tk.Toplevel(self)
        win.title("Páginas creadas")
        win.geometry("700x400")

        tree = ttk.Treeview(
            win,
            columns=("ID", "Título", "Autor", "Fecha"),
            show="headings",
            height=12
        )
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        tree.heading("ID", text="ID")
        tree.heading("Título", text="Título")
        tree.heading("Autor", text="Autor")
        tree.heading("Fecha", text="Fecha")

        for p in paginas:
            tree.insert(
                "",
                tk.END,
                values=(
                    p.get("id", ""),
                    p.get("titulo", ""),
                    p.get("autor", ""),
                    p.get("fecha", "")
                )
            )

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", padx=10, pady=5)

        def editar():
            selected = tree.selection()
            if not selected:
                return
            index = tree.index(selected[0])
            pagina = paginas[index]
            self.state = pagina.copy()
            self.contenido_original = json.loads(json.dumps(self.state))
            self.refresh_fields()
            self.refresh_table()
            win.destroy()


        def borrar():
            selected = tree.selection()
            if not selected:
                return
            index = tree.index(selected[0])
            pagina = paginas[index]
            resp = messagebox.askyesno(
                "Confirmar borrado",
                f"¿Seguro que quieres borrar la página:\n{pagina.get('titulo', '')}?"
            )
            if not resp:
                return
            del paginas[index]
            data["web"]["paginas"] = paginas
            self._save_web_data(data)
            tree.delete(selected[0])

        ttk.Button(btn_frame, text="Editar", command=editar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Borrar", command=borrar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy).pack(side="right", padx=5)

    def show_instructions(self):
        messagebox.showinfo(
            "Instrucciones",
            "1. Rellena los datos generales (portada, título, autor).\n"
            "\n"
            "2. Añade bloques al cuerpo (texto, imagen, enlaces).\n"
            "\n"
            "3. Pulsa 'Guardar' para añadir o actualizar la página en web.json.\n"
            "\n"
            "4. Usa 'Ver páginas creadas' para editar o borrar páginas.\n"
            "\n"
            "5. Usa 'Previsualizar en HTML' para ver el resultado en el navegador.\n\n"
            "6. Si quieres usar una página ya creada como enlace en cualquier enlace de cualquier sección, usa el ID de la página creada seguido de .html en el campo enlace o link, ejemplo: \n Enlace: pagina_001.html"

        )
