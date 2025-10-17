from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models.nuevoplato import NuevoPlato
from utils.extensions import db
import os

nuevoplato_bp = Blueprint('nuevoplato', __name__)
UPLOAD_FOLDER = 'static/uploads'

# Asegurar que la carpeta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@nuevoplato_bp.route('/admin/plato/nuevo', methods=['POST'])
def nuevo_plato():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    categoria = request.form['categoria']

    imagen_file = request.files.get('imagen')
    if imagen_file and imagen_file.filename != '':
        filename = secure_filename(imagen_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        imagen_file.save(image_path)
        imagen_url = '/' + image_path  # Ruta pública
    else:
        imagen_url = '/static/img/default.png'

    nuevo = NuevoPlato(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria=categoria,
        imagen=imagen_url
    )

    db.session.add(nuevo)
    db.session.commit()

    flash('Plato añadido correctamente', 'success')
    return redirect(url_for('main.restaurante_admin'))
