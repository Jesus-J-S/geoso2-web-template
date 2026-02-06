# GEOSO2 Web Template Editor

Aplicación de escritorio desarrollada en **Python + Tkinter** para gestionar y generar de forma visual el sitio web de GEOSO2.  
Permite editar contenido, gestionar imágenes y documentos, mantener un historial de cambios y generar automáticamente los archivos HTML finales mediante **plantillas Jinja2**.

Este proyecto está diseñado para facilitar la edición del sitio sin necesidad de modificar manualmente archivos HTML, CSS o JSON.

---

## Características principales

- **Interfaz gráfica completa** creada con Tkinter.
- **Edición visual del contenido** almacenado en `json/web.json`.
- **Gestión automática de imágenes y documentos**, copiándolos a la carpeta correcta.
- **Historial global de cambios** por sección.
- **Generación automática del sitio web** usando plantillas Jinja2.
- **Sistema de copias de seguridad** (exportar/importar JSON).
- **Plantillas HTML personalizables** en la carpeta `templates/`.
- **Salida final del sitio** en la carpeta `output/`.
- **CSS único** para todo el sitio (`css/style.css`).

---

# Estructura del proyecto


geoso2-web-template/
│
├── css/
│   └── style.css
│
├── json/
│   └── web.json
│
├── imput/
│   ├── img/
│   │   
│   ├── docs/
│   │   
│   └── logos/
│
├── templates/
│   ├── index_page.html
│   ├── carrusel.html
│   ├── noticias.html
│   ├── agenda.html
│   ├── proyectos.html
│   ├── publicaciones.html
│   ├── quienes_somos.html
│   ├── rafagas.html
│   ├── entidades.html
│   ├── participa.html
│   └── pagina.html
│
├── output/
│   └── (HTML generados automáticamente)
│
├── interfaz_ventana_principal.py
├── interfaz_carrusel.py
├── interfaz_noticias.py
├── interfaz_agenda.py
├── interfaz_entidades_colaboradoras.py
├── interfaz_quienessomos.py
├── interfaz_pagina_web.py
├── interfaz_publicaciones.py
├── interfaz_rafagas.py
├── interfaz_proyectos.py
└── interfaz_participa.py


# Cómo ejecutar el proyecto

1. Instalar dependencias:

"```bash"
pip install jinja2 pillow

# Ejecutar la aplicación principal

python interfaz_ventana_principal.py

# interfaz principal

La ventana principal ofrece acceso a todas las funciones del sistema:
Editar sitio web  
Abre un menú donde puedes seleccionar qué sección editar.
Historial de cambios  
Muestra todos los cambios registrados en cualquier sección.
Generar sitio web  
Renderiza todas las plantillas Jinja2 usando web.json y genera los HTML en output/.
Exportar copia de seguridad  
Guarda una copia del JSON actual.
Importar copia de seguridad  
Restaura un JSON previamente exportado.
Manual de ayuda PDF
Instrucciones.


# Cómo funciona el sistema de edición

Cada sección del sitio tiene su propio editor independiente, pero todos comparten la misma lógica:
Cargan el archivo json/web.json.
Editan únicamente la parte correspondiente a su sección.
Guardan los cambios en el JSON.
Registran un historial interno dentro de su sección.
Gestionan imágenes y documentos copiándolos a imput/.
Secciones disponibles
Carrusel
Noticias
Agenda
Entidades colaboradoras
Ráfagas
Proyectos
Quiénes somos
Publicaciones
Participa
Páginas web individuales
Cada editor está implementado en un archivo .py independiente.

# Gestión de imágenes y documentos

Todas las imágenes y documentos seleccionados por el usuario se copian automáticamente a la carpeta imput.
Los editores generan rutas relativas para que el sitio web funcione correctamente al exportarse.

# Estructura del archivo web.json

El archivo json/web.json contiene toda la información editable del sitio y Cada editor modifica únicamente su sección correspondiente.

# Historial de cambios

Cada sección mantiene un historial interno.
La ventana principal permite ver todo el historial global y limpiarlo.

# Generación del sitio web

Cuando el usuario pulsa Generar sitio web, ocurre lo siguiente:
Se carga json/web.json.
Se inicializa Jinja2 con las plantillas de templates/.
Se renderiza cada plantilla con los datos del JSON.
Se generan los archivos HTML en output/.
Se abre automáticamente output/index.html en el navegador.

Ejemplo de renderizado:

template = env.get_template("index_page.html")
html = template.render(index_page=web["index_page"])

# CSS

Todos los html usan el archivo css/style.css para el diseño de la página

# Copias de seguridad

Exportar copia:
Guarda el JSON actual en un archivo .json.

Importar copia:
Sobrescribe json/web.json con el archivo seleccionado.

# Plantillas HTML

Las plantillas están en la carpeta: templates/

Cada plantilla corresponde a una sección del sitio.
Puedes modificarlas libremente para cambiar el diseño del sitio web.

## Cómo añadir una nueva sección al editor

1. Crear un nuevo archivo `interfaz_nueva_seccion.py` siguiendo la estructura de los demás editores.
2. Añadir un botón en `interfaz_ventana_principal.py` dentro del menú de secciones.
3. Añadir la lógica de carga/guardado en `web.json` dentro de la clave correspondiente.
4. Crear una plantilla HTML en `templates/nueva_seccion.html`.
5. Añadir el renderizado en la función `generar_sitio_web()`.

Todas las secciones existentes pueden usarse como ejemplo.

## Cómo crear el ejecutable

Para crear el ejecutable necesitas tener installado pyinstaller, para descargarlo abre terminal o cmd y escribe:
pip install pyinstaller
y una vez instalado sigue el siguiente paso.

# En IOS:

1. una vez modificado eso nos diriguimos a "terminal" en nuestro dispositivo

2. Debemos diriguirnos a la carpeta raiz de nuestro proyecto, en este caso es new-geoso2 : "cd new-geoso2"

3. Escribimos lo siguiente:
pyinstaller --noconsole --onedir --add-data "geoso2-web-template:geoso2-web-template" geoso2-web-template/interfaz_ventana_principal.py

4. Se abrá creado en geoso2-web-template una carpeta llamada "dist" y dentro esta el ejecutable interfaz_ventana_principal que puedes ya mover a donde quieras

# En Windows:

1. Hacer doble clic en el archivo llamado Crear aplicación.bat que esta dentro del repositorio.

2. Se abrá creado en el escirtorio una carpeta llamada "GEOSO2" y dentro esta el ejecutable Editor GEOSO".exe y la carpeta Geoso2-web-template donde se encuentran todos los ficheros de la aplicación.

## Autor

Jesús Jaén Santana  
Versión del editor: 2.0 / 2026

