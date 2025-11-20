#!/usr/bin/env python3
"""
Script para modificar un template HTML usando Jinja2
"""

import json
from jinja2 import Template
from datetime import datetime

def main():
    # Leer el template
    with open('template.html', 'r', encoding='utf-8') as file:
        template_content = file.read()

    # Crear el objeto Template de Jinja2
    template = Template(template_content)

    # Leer datos desde el archivo JSON
    with open('datos.json', 'r', encoding='utf-8') as file:
        datos = json.load(file)

    # Agregar la fecha actual (se genera dinámicamente)
    datos['fecha'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    # Renderizar el template con los datos
    html_generado = template.render(datos)

    # Guardar el resultado en output.html
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(html_generado)

    print('✓ Template procesado exitosamente')
    print('✓ Archivo generado: output.html')

if __name__ == '__main__':
    main()
