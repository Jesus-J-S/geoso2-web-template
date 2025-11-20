import tkinter as tk
from tkinter import filedialog, messagebox
import json
import subprocess
import webbrowser
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import sys

# Configurar Jinja2 para cargar la plantilla desde el directorio actual
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')


class WizardNoticias(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Publicador de Noticias")
        self.geometry("800x500")

        # Estado: datos de la noticia
        self.state = {
            "nombre": "",
            "email": "",
            "titulo": "",
            "mensaje": "",
            "items": [],
            "imagen": "",
            "fecha": ""  # se setea al previsualizar/subir
        }

        # Contenedor principal para cambiar pantallas
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Construir pantallas
        self.frames = {}
        for F in (PasoDatos, PasoTitulo, PasoMensaje, PasoImagen, PasoPreview):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Mostrar primer paso
        self.show_frame("PasoDatos")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def render_html(self):
        # Preparar fecha
        self.state["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Renderizar HTML con Jinja2
        html = template.render(
            titulo=self.state["titulo"],
            nombre=self.state["nombre"],
            email=self.state["email"],
            mensaje=self.state["mensaje"],
            items=self.state["items"],
            imagen=self.state["imagen"],
            fecha=self.state["fecha"]
        )
        return html

    def preview_in_app(self):
        # Generar HTML y mostrar en el paso de previsualización
        html = self.render_html()
        preview_frame = self.frames["PasoPreview"]
        preview_frame.set_preview(html)

    def save_json_and_generate(self):
        # Guardar datos en datos.json
        datos = {
            "titulo": self.state["titulo"],
            "nombre": self.state["nombre"],
            "email": self.state["email"],
            "mensaje": self.state["mensaje"],
            "items": self.state["items"],
            "imagen": self.state["imagen"],
            "fecha": self.state["fecha"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            with open("datos.json", "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo escribir datos.json:\n{e}")
            return

        # Ejecutar modify_template.py
        try:
            subprocess.run([sys.executable, "modify_template.py"], check=True)
            messagebox.showinfo("Listo", "Noticia subida y output.html generado.")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al generar output.html:\n{e}")

    def open_preview_in_browser(self):
        # Guardar preview temporal y abrir en navegador con ruta absoluta
        html = self.render_html()
        try:
            with open("preview.html", "w", encoding="utf-8") as f:
                f.write(html)
            ruta = os.path.abspath("preview.html")
            webbrowser.open(f"file:///{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el navegador:\n{e}")


class BaseStep(tk.Frame):
    """Base para cada paso, define barra de navegación común."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.content = tk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.nav = tk.Frame(self)
        self.nav.pack(fill=tk.X, padx=20, pady=10)

        self.btn_back = tk.Button(self.nav, text="Atrás", command=self.on_back)
        self.btn_back.pack(side=tk.LEFT)

        self.btn_next = tk.Button(self.nav, text="Siguiente", command=self.on_next)
        self.btn_next.pack(side=tk.RIGHT)

    def on_back(self):
        pass

    def on_next(self):
        pass


class PasoDatos(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self.content, text="Datos del autor", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(self.content)
        form.pack(anchor="w", fill=tk.X)

        tk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nombre = tk.Entry(form, width=40)
        self.entry_nombre.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_email = tk.Entry(form, width=40)
        self.entry_email.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Inicializar si vuelve atrás
        self.entry_nombre.insert(0, controller.state["nombre"])
        self.entry_email.insert(0, controller.state["email"])

    def on_next(self):
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()

        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
        elif not email:
            messagebox.showwarning("Falta información", "El email es obligatorio.")
        else:
            self.controller.state["nombre"] = nombre
            self.controller.state["email"] = email
            self.controller.show_frame("PasoTitulo")


class PasoTitulo(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self.content, text="Título de la noticia", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(self.content)
        form.pack(anchor="w", fill=tk.X)

        tk.Label(form, text="Título:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_titulo = tk.Entry(form, width=60)
        self.entry_titulo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.entry_titulo.insert(0, controller.state["titulo"])

    def on_back(self):
        self.controller.show_frame("PasoDatos")

    def on_next(self):
        titulo = self.entry_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Falta información", "El título es obligatorio.")
        else:
            self.controller.state["titulo"] = titulo
            self.controller.show_frame("PasoMensaje")


class PasoMensaje(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self.content, text="Contenido de la noticia", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(self.content)
        form.pack(anchor="w", fill=tk.BOTH, expand=True)

        tk.Label(form, text="Mensaje:").grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.text_mensaje = tk.Text(form, width=70, height=12)
        self.text_mensaje.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        tk.Label(form, text="Items (separados por coma):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_items = tk.Entry(form, width=60)
        self.entry_items.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Inicializar si vuelve atrás
        self.text_mensaje.insert("1.0", controller.state["mensaje"])
        self.entry_items.insert(0, ",".join(controller.state["items"]))

        form.grid_rowconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

    def on_back(self):
        self.controller.show_frame("PasoTitulo")

    def on_next(self):
        mensaje = self.text_mensaje.get("1.0", tk.END).strip()
        items_raw = self.entry_items.get().strip()
        items = [i.strip() for i in items_raw.split(",") if i.strip()] if items_raw else []

        if not mensaje:
            messagebox.showwarning("Falta información", "El mensaje es obligatorio.")
        else:
            self.controller.state["mensaje"] = mensaje
            self.controller.state["items"] = items
            self.controller.show_frame("PasoImagen")


class PasoImagen(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self.content, text="Imagen de la noticia", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(self.content)
        form.pack(anchor="w", fill=tk.X)

        tk.Label(form, text="Ruta de imagen:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_imagen = tk.Entry(form, width=50)
        self.entry_imagen.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.btn_sel = tk.Button(form, text="Seleccionar...", command=self.select_image)
        self.btn_sel.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Inicializar si vuelve atrás
        self.entry_imagen.insert(0, controller.state["imagen"])

        note = tk.Label(self.content, text="Sugerencia: usa imágenes .png/.jpg/.jpeg/.gif; deja el campo vacío si no quieres incluir imagen.")
        note.pack(anchor="w", pady=(10, 0))

    def select_image(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if ruta:
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, ruta)

    def on_back(self):
        self.controller.show_frame("PasoMensaje")

    def on_next(self):
        self.controller.state["imagen"] = self.entry_imagen.get().strip()
        # Preparar previsualización
        self.controller.preview_in_app()
        self.controller.show_frame("PasoPreview")


class PasoPreview(BaseStep):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self.content, text="Previsualización", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # Área de previsualización: muestra el HTML renderizado como texto
        self.preview_text = tk.Text(self.content, wrap="word")
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Acciones extra
        actions = tk.Frame(self.content)
        actions.pack(fill=tk.X, pady=8)
        tk.Button(actions, text="Abrir en navegador", command=self.controller.open_preview_in_browser).pack(side=tk.LEFT)

        # Cambiar el botón principal a "Subir"
        self.btn_next.config(text="Subir")

    def set_preview(self, html):
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, html)

    def on_back(self):
        self.controller.show_frame("PasoImagen")

    def on_next(self):
        # Subir: guardar JSON y generar output.html
        self.controller.save_json_and_generate()


if __name__ == "__main__":
    app = WizardNoticias()
    app.mainloop()
