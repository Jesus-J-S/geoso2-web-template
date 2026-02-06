import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import webbrowser
import shutil
import sys

def resource_path(relative_path):
    """Devuelve la ruta absoluta tanto en script como en ejecutable .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class EditorWindow(tk.Toplevel):
    def __init__(self, mode="create", filepath=None):
        super().__init__()
        self.title("Editor de Publicaciones")
        self.geometry("980x800")

        self.state = {"publicaciones": {}}
        self.filepath = filepath

        if mode == "edit" and filepath and os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                self.state["publicaciones"] = datos.get("web", {}).get("publicaciones", {})
                self.contenido_original = json.loads(json.dumps(self.state["publicaciones"]))

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el JSON:\n{e}")

        notebook_frame = ttk.Frame(self)
        notebook_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        self.tab_datos = DatosTab(self.notebook, self)
        self.notebook.add(self.tab_datos, text="Datos")

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", pady=10)

        ttk.Button(bottom_frame, text="Instrucciones",
                   command=self.tab_datos.instrucciones).pack(side="left", padx=10)

        ttk.Button(bottom_frame, text="Guardar cambios",
                   command=self.save_json).pack(side="top", pady=5)

        self.tab_datos.set_data(self.state)


    def detectar_cambios(self, antes, despues):
        cambios = []

        if set(antes.keys()) != set(despues.keys()):
            cambios.append("años")

        for year in despues:
            if year not in antes:
                cambios.append(f"nuevo_{year}")
            elif antes[year] != despues[year]:
                cambios.append(year)

        return cambios


    def save_json(self):
        ruta = resource_path("geoso2-web-template/json/web.json")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos_completos = json.load(f)

            datos_completos.setdefault("web", {})
            datos_completos["web"].setdefault("publicaciones", {})

            cambios = self.detectar_cambios(self.contenido_original, self.state["publicaciones"])

            if cambios:
                datos_completos["web"]["publicaciones"].setdefault("history", [])
                datos_completos["web"]["publicaciones"]["history"].append({
                    "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    "sections_changed": cambios,
                    "summary": "Actualización en publicaciones"
                })

            datos_completos["web"]["publicaciones"] = self.state["publicaciones"]

            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Guardado", f"Archivo JSON actualizado:\n{ruta}")

            self.contenido_original = json.loads(json.dumps(self.state["publicaciones"]))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


class DatosTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frm, text="Año:").grid(row=0, column=0, sticky="w", pady=6)

        self.combo_year = ttk.Combobox(frm, state="readonly")
        self.combo_year.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Button(frm, text="Añadir año", command=self.add_year).grid(row=0, column=2, padx=6)
        ttk.Button(frm, text="Eliminar año", command=self.delete_year).grid(row=0, column=3, padx=6)
        ttk.Button(frm, text="Actualizar", command=self.refresh_table).grid(row=0, column=4, padx=6)

        frm.columnconfigure(1, weight=1)

        labels = [
            ("Autores:", 1),
            ("Título:", 2),
            ("Tipo:", 3),
            ("Revista:", 4),
            ("Volumen:", 5),
            ("Número:", 6),
            ("URL:", 7)
        ]

        self.entry_autores = ttk.Entry(frm)
        self.entry_titulo = ttk.Entry(frm)
        self.entry_tipo = ttk.Entry(frm)
        self.entry_revista = ttk.Entry(frm)
        self.entry_volumen = ttk.Entry(frm)
        self.entry_num = ttk.Entry(frm)
        self.entry_link = ttk.Entry(frm)

        entries = [
            self.entry_autores,
            self.entry_titulo,
            self.entry_tipo,
            self.entry_revista,
            self.entry_volumen,
            self.entry_num,
            self.entry_link
        ]

        for (text, row), entry in zip(labels, entries):
            ttk.Label(frm, text=text).grid(row=row, column=0, sticky="w", pady=6)
            entry.grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Button(frm, text="Probar enlace", command=self.probar_enlace).grid(row=7, column=2, padx=6)
        ttk.Button(frm, text="Buscar archivo", command=self.select_file).grid(row=7, column=3, padx=6)

        # -------------------------
        # Botones CRUD
        # -------------------------
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=8, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Añadir", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.move_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Bajar", command=self.move_down).pack(side="left", padx=5)

        self.tree = ttk.Treeview(
            frm,
            columns=("Autores", "Título", "Tipo", "Revista", "Volumen", "Num", "Link"),
            show="headings",
            height=10
        )
        self.tree.grid(row=9, column=0, columnspan=4, sticky="nsew")

        for col in ("Autores", "Título", "Tipo", "Revista", "Volumen", "Num", "Link"):
            self.tree.heading(col, text=col)

        frm.rowconfigure(9, weight=1)

    def select_file(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Documentos", "*.pdf;*.html;*.htm"),
                ("PDF", "*.pdf"),
                ("HTML", "*.html;*.htm"),
                ("Todos", "*.*")
            ]
        )

        if not ruta:
            return

        try:
            destino_dir = resource_path("geoso2-web-template/imput/docs/publicaciones")
            os.makedirs(destino_dir, exist_ok=True)

            nombre = os.path.basename(ruta)
            destino = os.path.join(destino_dir, nombre)

            with open(ruta, "rb") as f_src, open(destino, "wb") as f_dst:
                f_dst.write(f_src.read())

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, f"../imput/docs/publicaciones/{nombre}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")

    def add_year(self):
        year = tk.simpledialog.askstring("Nuevo año", "Introduce el año (ej: 2025):")
        if not year:
            return

        if year in self.controller.state["publicaciones"]:
            messagebox.showwarning("Aviso", "Ese año ya existe.")
            return

        self.controller.state["publicaciones"][year] = []
        self.refresh_years()
        self.combo_year.set(year)
        self.refresh_table()

    def delete_year(self):
        year = self.combo_year.get()
        if not year:
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el año {year}?"):
            return

        del self.controller.state["publicaciones"][year]
        self.refresh_years()
        self.refresh_table()

    def refresh_years(self):
        years = sorted(
            [y for y in self.controller.state["publicaciones"].keys() if y != "history"],
            reverse=True
        )
        self.combo_year["values"] = years
        if years:
            self.combo_year.set(years[0])


    def add_item(self):
        year = self.combo_year.get()
        if not year:
            messagebox.showwarning("Aviso", "Debes seleccionar un año.")
            return

        pub = {
            "autores": self.entry_autores.get().strip(),
            "titulo": self.entry_titulo.get().strip(),
            "tipo": self.entry_tipo.get().strip(),
            "revista": self.entry_revista.get().strip(),
            "volumen": self.entry_volumen.get().strip(),
            "num": self.entry_num.get().strip(),
            "link": self.entry_link.get().strip()
        }

        if not pub["titulo"]:
            messagebox.showwarning("Aviso", "Debes introducir un título.")
            return

        self.controller.state["publicaciones"][year].append(pub)
        self.refresh_table()
        self.clear_fields()


    def delete_item(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.controller.state["publicaciones"][year][index]
        self.refresh_table()


    def edit_item(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        item = self.controller.state["publicaciones"][year][index]

        self.entry_autores.delete(0, tk.END)
        self.entry_autores.insert(0, item["autores"])

        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, item["titulo"])

        self.entry_tipo.delete(0, tk.END)
        self.entry_tipo.insert(0, item["tipo"])

        self.entry_revista.delete(0, tk.END)
        self.entry_revista.insert(0, item["revista"])

        self.entry_volumen.delete(0, tk.END)
        self.entry_volumen.insert(0, item["volumen"])

        self.entry_num.delete(0, tk.END)
        self.entry_num.insert(0, item["num"])

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, item["link"])

        del self.controller.state["publicaciones"][year][index]
        self.refresh_table()


    def move_up(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        arr = self.controller.state["publicaciones"][year]

        if index > 0:
            arr[index - 1], arr[index] = arr[index], arr[index - 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])


    def move_down(self):
        year = self.combo_year.get()
        if not year:
            return

        selected = self.tree.selection()
        if not selected:
            return

        index = self.tree.index(selected[0])
        arr = self.controller.state["publicaciones"][year]

        if index < len(arr) - 1:
            arr[index + 1], arr[index] = arr[index], arr[index + 1]
            self.refresh_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def probar_enlace(self):
        url = self.entry_link.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "No hay URL para probar.")
            return

        try:
            if url.startswith(("http://", "https://")):
                webbrowser.open_new_tab(url)
            else:
                messagebox.showerror("Error", "El enlace debe ser una URL válida.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")


    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        year = self.combo_year.get()
        if not year:
            return

        for p in self.controller.state["publicaciones"].get(year, []):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    p["autores"],
                    p["titulo"],
                    p["tipo"],
                    p["revista"],
                    p["volumen"],
                    p["num"],
                    p["link"]
                )
            )


    def clear_fields(self):
        self.entry_autores.delete(0, tk.END)
        self.entry_titulo.delete(0, tk.END)
        self.entry_tipo.delete(0, tk.END)
        self.entry_revista.delete(0, tk.END)
        self.entry_volumen.delete(0, tk.END)
        self.entry_num.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)


    def set_data(self, datos):
        self.controller.state["publicaciones"] = datos.get("publicaciones", {})
        self.refresh_years()
        self.refresh_table()

    def instrucciones(self):
        instrucciones = (
            "Instrucciones para el editor de Publicaciones:\n\n"
            "1. Añadir un año:\n"
            "   - Haz clic en 'Añadir año' e introduce el año deseado.\n\n"
            "2. Eliminar un año:\n"
            "   - Selecciona el año en el desplegable y haz clic en 'Eliminar año'.\n\n"
            "3. Añadir una publicación:\n"
            "   - Rellena los campos correspondientes y haz clic en 'Añadir'.\n\n"
            "4. Editar una publicación:\n"
            "   - Selecciona una publicación en la tabla, haz clic en 'Editar', modifica los campos y vuelve a hacer clic en 'Añadir'.\n\n"
            "5. Eliminar una publicación:\n"
            "   - Selecciona una publicación en la tabla y haz clic en 'Eliminar'.\n\n"
            "6. Mover publicaciones:\n"
            "   - Selecciona una publicación y usa 'Subir' o 'Bajar' para cambiar su posición.\n\n"
            "7. Probar enlace:\n"
            "   - Introduce una URL en el campo correspondiente y haz clic en 'Probar enlace' para abrirla en el navegador.\n\n"
            "8. Guardar cambios:\n"
            "   - Haz clic en 'Guardar cambios' para actualizar el archivo JSON con las modificaciones realizadas."
        )
        messagebox.showinfo("Instrucciones", instrucciones)
