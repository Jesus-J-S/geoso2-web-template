# Template HTML con Jinja2

Prueba de concepto para modificar templates HTML usando Python y Jinja2.

cambio hecho por jesus

## Estructura del proyecto

```
.
├── venv/                  # Entorno virtual de Python
├── template.html          # Template HTML con sintaxis Jinja2
├── datos.json            # Archivo JSON con los datos del template
├── modify_template.py     # Script Python para procesar el template
├── output.html           # HTML generado (se crea al ejecutar el script)
└── README.md             # Este archivo
```

## Requisitos

- Python 3.x
- Jinja2 (instalado en el entorno virtual)

## Instalación

El entorno virtual ya está configurado con Jinja2 instalado. Si necesitas recrearlo:

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows

# Instalar Jinja2
pip install jinja2
```

### Gestión de dependencias con pip freeze

Para exportar las dependencias instaladas a un archivo `requirements.txt`:

```bash
# Activar el entorno virtual
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows

# Exportar dependencias
pip freeze > requirements.txt
```

Para instalar las dependencias desde `requirements.txt` en otro entorno:

```bash
# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias desde el archivo
pip install -r requirements.txt
```

Esto es útil para compartir el proyecto con otros desarrolladores o desplegar en diferentes entornos.

## Cómo usar

### Ejecución básica

```bash
./venv/bin/python modify_template.py
```

O si tienes el entorno virtual activado:

```bash
python modify_template.py
```

### Visualizar el resultado

Abre el archivo `output.html` generado en tu navegador web.

## Características implementadas

### Variables simples

El template soporta variables que se reemplazan con valores reales:

- `{{ titulo }}` - Título de la página
- `{{ nombre }}` - Nombre del usuario
- `{{ email }}` - Email del usuario
- `{{ fecha }}` - Fecha de generación (automática)
- `{{ mensaje }}` - Mensaje personalizado

### Bucles (iteración)

Puedes generar listas dinámicamente usando bucles:

```html
{% for item in items %}
<li>{{ item }}</li>
{% endfor %}
```

### Estilos CSS incluidos

El template incluye estilos CSS básicos con:
- Diseño responsivo
- Tarjetas con sombras
- Colores y espaciado profesional

## Personalización

Los datos del template se encuentran en el archivo `datos.json`. Para personalizarlos, edita este archivo:

```json
{
    "titulo": "Tu título aquí",
    "nombre": "Tu nombre",
    "email": "tu@email.com",
    "mensaje": "Tu mensaje personalizado",
    "items": [
        "Item 1",
        "Item 2",
        "Item 3"
    ]
}
```

**Nota:** El campo `fecha` se genera automáticamente al ejecutar el script, no es necesario incluirlo en el JSON.

Después de modificar `datos.json`, ejecuta nuevamente el script para regenerar `output.html`:

```bash
./venv/bin/python modify_template.py
```

## Extender el template

Puedes añadir más variables o estructuras Jinja2 al template:

- **Condicionales**: `{% if condicion %}...{% endif %}`
- **Filtros**: `{{ variable|upper }}`, `{{ variable|length }}`
- **Comentarios**: `{# Este es un comentario #}`

Para más información sobre Jinja2: https://jinja.palletsprojects.com/
