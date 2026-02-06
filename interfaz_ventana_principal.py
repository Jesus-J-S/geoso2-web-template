import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import interfaz_noticias
import interfaz_agenda
import interfaz_carrusel
import interfaz_entidades_colaboradoras
import interfaz_quienessomos
import interfaz_pagina_web
import interfaz_publicaciones
import interfaz_rafagas
import interfaz_proyectos
import interfaz_participa
import os
import json
import webbrowser
from jinja2 import Environment, FileSystemLoader
import sys


def resource_path(relative_path):
    """Devuelve la ruta absoluta tanto en script como en ejecutable .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class VentanaHistorialGlobal(tk.Toplevel):
    def __init__(self, historial):
        super().__init__()
        self.title("Historial de cambios (global)")
        self.geometry("750x500")

        ttk.Label(self, text="Historial global del sitio web",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("seccion", "timestamp", "cambios", "resumen")
        self.tree = ttk.Treeview(frame, columns=columnas, show="headings", height=20)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("seccion", text="Sección")
        self.tree.heading("timestamp", text="Fecha")
        self.tree.heading("cambios", text="Cambios")
        self.tree.heading("resumen", text="Resumen")

        self.tree.column("seccion", width=150)
        self.tree.column("timestamp", width=150)
        self.tree.column("cambios", width=200)
        self.tree.column("resumen", width=250)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        for reg in historial:
            self.tree.insert("", "end", values=(
                reg["seccion"],
                reg["timestamp"],
                ", ".join(reg["sections_changed"]),
                reg.get("summary", "")
            ))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(
            btn_frame,
            text="Limpiar historial",
            command=self.limpiar_historial
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_frame,
            text="Cerrar",
            command=self.destroy
        ).pack(side="right", padx=10)

    def limpiar_historial(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas limpiar todo el historial global?"):
            try:
                ruta_json = resource_path("geoso2-web-template/json/web.json")

                with open(ruta_json, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                web = datos.get("web", {})

                for seccion, contenido in web.items():
                    if isinstance(contenido, dict) and "history" in contenido:
                        contenido["history"] = []

                with open(ruta_json, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)

                messagebox.showinfo("Éxito", "Historial global limpiado correctamente.")
                self.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo limpiar el historial:\n{e}")

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gestor de Geoso2")
        self.geometry("400x500")

        ttk.Label(self, text="Selecciona una opción:", font=("Segoe UI", 14, "bold")).pack(pady=20)

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(btns, text="Editar sitio web", width=20,
                   command=lambda: self.open_section_menu("edit")).grid(row=0, column=0, padx=10)

        ttk.Button(btns, text="Historial de cambios", width=20,
                   command=self.abrir_historial_global).grid(row=1, column=0, padx=10, pady=10)

        ttk.Separator(btns).grid(row=2, column=0, pady=10, sticky="ew")

        ttk.Button(btns, text="Generar sitio web", width=16,
                   command=self.generar_sitio_web).grid(row=2, column=0, padx=10, pady=20)

        ttk.Button(btns, text="Exportar copia de seguridad", width=25,
                   command=self.exportar_copia).grid(row=3, column=0, padx=10)

        ttk.Button(btns, text="Importar copia de seguridad", width=25,
                   command=self.importar_copia).grid(row=4, column=0, padx=10, pady=10)

        ttk.Button(btns, text="Manual de ayuda Pdf", width=20,
                   command=self.abrir_manual_ayuda).grid(row=5, column=0, padx=20, pady=20)

        bottom_frame = ttk.Frame(btns)
        bottom_frame.grid(row=8, column=0, pady=(50, 0))

        ttk.Button(bottom_frame, text="Instrucciones", width=12,
                   command=self.abrir_instrucciones).grid(row=0, column=0, padx=10)

        ttk.Button(bottom_frame, text="Salir", width=8,
                   command=self.quit).grid(row=0, column=1, padx=10)

        ttk.Label(self, text="© Creado por Jesús Jaén Santana v.2.0/2026",
                  font=("Segoe UI", 10, "italic")).pack(side="bottom", pady=10)


    def abrir_historial_global(self):
        try:
            ruta_json = resource_path("geoso2-web-template/json/web.json")

            with open(ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)

            web = datos["web"]
            historial_global = []

            for nombre_seccion, contenido in web.items():
                if isinstance(contenido, dict) and "history" in contenido:
                    for registro in contenido["history"]:
                        historial_global.append({
                            "seccion": nombre_seccion,
                            **registro
                        })

            if not historial_global:
                messagebox.showinfo("Historial vacío", "No hay cambios registrados todavía.")
                return

            VentanaHistorialGlobal(historial_global)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{e}")

    def open_section_menu(self, mode):
        win = tk.Toplevel(self)
        win.title("Selecciona la sección")
        win.geometry("400x650")

        ttk.Label(win,
                  text="Selecciona el JSON a editar:",
                  font=("Segoe UI", 12, "bold")).pack(pady=15)

        frm = ttk.Frame(win)
        frm.pack(pady=10)

        ttk.Label(frm, text="Gestionar imágenes de:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Carrusel", width=20,
                   command=lambda: self.abrir_carrusel(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Entidades Colaboradoras", width=20,
                   command=lambda: self.abrir_entidades_colaboradoras(mode, win)).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Secciones de la página principal:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Noticias", width=20,
                   command=lambda: self.abrir_noticias(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Agenda", width=20,
                   command=lambda: self.abrir_agenda(mode, win)).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Otras secciones:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Ráfagas", width=20,
                   command=lambda: self.abrir_rafagas(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Proyectos", width=20,
                   command=lambda: self.abrir_proyectos(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Quienes Somos", width=20,
                   command=lambda: self.abrir_quienes_somos(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Publicaciones", width=20,
                   command=lambda: self.abrir_publicaciones(mode, win)).pack(pady=4)

        ttk.Button(frm, text="Participa", width=20,
                   command=lambda: self.abrir_participa(mode, win)).pack(pady=4)

        ttk.Separator(frm).pack(fill="x", pady=8)

        ttk.Label(frm, text="Gestión de otras Páginas:", font=("Segoe UI", 11)).pack(pady=8)

        ttk.Button(frm, text="Páginas Web", width=20,
                   command=lambda: self.abrir_pagina_web(mode, win)).pack(pady=4)


    def abrir_json_directo(self, mode, parent_win, filename):
        parent_win.destroy()

        ruta = resource_path(f"geoso2-web-template/json/{filename}.json")

        if mode == "edit" and not os.path.exists(ruta):
            messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta}")
            return None

        return ruta

    def abrir_noticias(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_noticias.NoticiasWindow(mode=mode, filepath=ruta)

    def abrir_agenda(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_agenda.EditorWindow(mode=mode, filepath=ruta)

    def abrir_rafagas(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_rafagas.EditorRafagasWindow(filepath=ruta)

    def abrir_proyectos(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_proyectos.EditorProyectosWindow(filepath=ruta)

    def abrir_quienes_somos(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_quienessomos.EditorWindow(mode=mode, filepath=ruta)

    def abrir_publicaciones(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_publicaciones.EditorWindow(mode=mode, filepath=ruta)

    def abrir_carrusel(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_carrusel.CarruselWindow(mode=mode, filepath=ruta)

    def abrir_entidades_colaboradoras(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_entidades_colaboradoras.EntidadesWindow(mode=mode, filepath=ruta)

    def abrir_pagina_web(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_pagina_web.paginaWindow(mode=mode, filepath=ruta)

    def abrir_participa(self, mode, parent_win):
        ruta = self.abrir_json_directo(mode, parent_win, "web")
        if ruta:
            interfaz_participa.EditorParticipaWindow(mode=mode, filepath=ruta)

    def generar_sitio_web(self):
        try:
            ruta_json = resource_path("geoso2-web-template/json/web.json")

            with open(ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)

            web = datos["web"]

            templates_dir = resource_path(os.path.join("geoso2-web-template", "templates"))
            env = Environment(loader=FileSystemLoader(templates_dir))

            output_dir = resource_path("geoso2-web-template/output")
            os.makedirs(output_dir, exist_ok=True)

            # INDEX
            template_index = env.get_template("index_page.html")
            html_index = template_index.render(
                index_page={
                    "carousel": web["index_page"].get("carrusel", []),
                    "noticias": web["index_page"].get("noticias", []),
                    "agenda": web["index_page"].get("agenda", []),
                    "colaboradores": web["index_page"].get("entidades", [])
                }
            )
            with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_index)

            # CARRUSEL
            if os.path.exists(resource_path("geoso2-web-template/templates/carrusel.html")):
                template_carrusel = env.get_template("carrusel.html")
                html_carrusel = template_carrusel.render(
                    carrusel=web["index_page"].get("carrusel", [])
                )
                with open(os.path.join(output_dir, "carrusel.html"), "w", encoding="utf-8") as f:
                    f.write(html_carrusel)

            # NOTICIAS
            if os.path.exists(resource_path("geoso2-web-template/templates/noticias.html")):
                template_noticias = env.get_template("noticias.html")
                html_noticias = template_noticias.render(
                    noticias=web["index_page"].get("noticias", [])
                )
                with open(os.path.join(output_dir, "noticias.html"), "w", encoding="utf-8") as f:
                    f.write(html_noticias)

            # AGENDA
            if os.path.exists(resource_path("geoso2-web-template/templates/agenda.html")):
                template_agenda = env.get_template("agenda.html")
                html_agenda = template_agenda.render(
                    agenda=web["index_page"].get("agenda", [])
                )
                with open(os.path.join(output_dir, "agenda.html"), "w", encoding="utf-8") as f:
                    f.write(html_agenda)

            # PROYECTOS
            if os.path.exists(resource_path("geoso2-web-template/templates/proyectos.html")):
                template_proyectos = env.get_template("proyectos.html")
                html_proyectos = template_proyectos.render(
                    proyectos=web.get("proyectos", {})
                )
                with open(os.path.join(output_dir, "proyectos.html"), "w", encoding="utf-8") as f:
                    f.write(html_proyectos)

            # PUBLICACIONES
            if os.path.exists(resource_path("geoso2-web-template/templates/publicaciones.html")):
                template_publicaciones = env.get_template("publicaciones.html")
                html_publicaciones = template_publicaciones.render(
                    publicaciones=web.get("publicaciones", {})
                )
                with open(os.path.join(output_dir, "publicaciones.html"), "w", encoding="utf-8") as f:
                    f.write(html_publicaciones)

            # QUIÉNES SOMOS
            if os.path.exists(resource_path("geoso2-web-template/templates/quienes_somos.html")):
                template_qs = env.get_template("quienes_somos.html")
                html_qs = template_qs.render(
                    quienes_somos=web.get("quienes_somos", {})
                )
                with open(os.path.join(output_dir, "quienes_somos.html"), "w", encoding="utf-8") as f:
                    f.write(html_qs)

            # RÁFAGAS
            if os.path.exists(resource_path("geoso2-web-template/templates/rafagas.html")):
                template_rafagas = env.get_template("rafagas.html")
                html_rafagas = template_rafagas.render(
                    rafagas=web.get("pagina1", {}).get("rafagas", [])
                )
                with open(os.path.join(output_dir, "rafagas.html"), "w", encoding="utf-8") as f:
                    f.write(html_rafagas)

            # ENTIDADES
            if os.path.exists(resource_path("geoso2-web-template/templates/entidades.html")):
                template_entidades = env.get_template("entidades.html")
                html_entidades = template_entidades.render(
                    entidades=web["index_page"].get("entidades", [])
                )
                with open(os.path.join(output_dir, "entidades.html"), "w", encoding="utf-8") as f:
                    f.write(html_entidades)

            # PARTICIPA
            if os.path.exists(resource_path("geoso2-web-template/templates/participa.html")):
                template_participa = env.get_template("participa.html")
                html_participa = template_participa.render(
                    participa=web.get("participa", [])
                )
                with open(os.path.join(output_dir, "participa.html"), "w", encoding="utf-8") as f:
                    f.write(html_participa)


            # PÁGINAS INDIVIDUALES
            if os.path.exists(resource_path("geoso2-web-template/templates/pagina.html")):
                template_pagina = env.get_template("pagina.html")
                paginas = web.get("paginas", [])

                for pagina in paginas:
                    html_pagina = template_pagina.render(pagina=pagina)
                    nombre_archivo = f"{pagina['id']}.html"

                    with open(os.path.join(output_dir, nombre_archivo), "w", encoding="utf-8") as f:
                        f.write(html_pagina)

            # LIMPIAR PÁGINAS ANTIGUAS
            paginas_json = {p["id"] + ".html" for p in web.get("paginas", [])}

            for archivo in os.listdir(output_dir):
                if archivo.startswith("pagina_") and archivo.endswith(".html"):
                    if archivo not in paginas_json:
                        os.remove(os.path.join(output_dir, archivo))

            messagebox.showinfo("Éxito", "Sitio web generado correctamente.")

            index_path = os.path.abspath(os.path.join(output_dir, "index.html"))
            webbrowser.open(f"file:///{index_path}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el sitio web:\n{e}")

    def exportar_copia(self):
        try:
            ruta_origen = resource_path("geoso2-web-template/json/web.json")

            if not os.path.exists(ruta_origen):
                messagebox.showerror("Error", "No se encontró web.json.")
                return

            ruta_destino = filedialog.asksaveasfilename(
                title="Exportar copia de seguridad",
                defaultextension=".json",
                filetypes=[("Archivo JSON", "*.json")]
            )

            if not ruta_destino:
                return

            with open(ruta_origen, "r", encoding="utf-8") as f_src, \
                 open(ruta_destino, "w", encoding="utf-8") as f_dst:
                f_dst.write(f_src.read())

            messagebox.showinfo("Exportado", "Copia exportada correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la copia:\n{e}")

    def importar_copia(self):
        try:
            ruta_origen = filedialog.askopenfilename(
                title="Seleccionar copia de seguridad",
                filetypes=[("Archivo JSON", "*.json")]
            )

            if not ruta_origen:
                return

            with open(ruta_origen, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if "web" not in datos:
                messagebox.showerror("Error", "El archivo seleccionado no es una copia válida.")
                return

            ruta_destino = resource_path("geoso2-web-template/json/web.json")

            with open(ruta_destino, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Importado", "Copia importada correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar la copia:\n{e}")

    def abrir_manual_ayuda(self):
        pdf_path = resource_path("geoso2-web-template/manual-de-ayuda/Manual-de-Ayuda.pdf")
        if not os.path.exists(pdf_path):
            print("No se encontró el archivo:", pdf_path)
            return
        webbrowser.open_new_tab(f"file:///{os.path.abspath(pdf_path)}")

    def abrir_instrucciones(self):
        instrucciones = (
            "Instrucciones para usar el Gestor de Geoso2:\n\n"
            "1. Usa 'Editar sitio web' para modificar las diferentes secciones del sitio.\n"
            "(Cada sección tiene su propio editor con instrucciones específicas)\n"
            "\n"
            "2. Usa 'Historial de cambios' para ver y limpiar el historial global de modificaciones.\n"
            "\n"
            "3. Usa 'Generar sitio web' para crear los archivos HTML en la carpeta de salida.\n"
            "\n"
            "4. Puedes exportar e importar copias de seguridad del archivo web.json.\n"
            "(Ten en cuenta que el nombre del archivo importado debe ser web.json para que funcione correctamente y que importar sobrescribirá el archivo actual)\n"
            "\n"
            "5. Consulta el 'Manual de ayuda Pdf' para más detalles sobre cada sección."
        )
        messagebox.showinfo("Instrucciones", instrucciones)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
