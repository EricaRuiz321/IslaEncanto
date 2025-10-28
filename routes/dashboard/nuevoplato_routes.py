from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models.nuevoplato import NuevoPlato
from utils.extensions import db
from sqlalchemy import text
import os
import time

nuevoplato_bp = Blueprint('nuevoplato', __name__, url_prefix='/admin/nuevoplato')
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Listar / crear (GET muestra lista)
@nuevoplato_bp.route('/', methods=['GET'])
def nuevo_plato():
    platos = NuevoPlato.query.all()
    return render_template('dashboard/restaurante_admin.html', platos=platos)

# Editar plato (GET muestra formulario, POST guarda cambios)
@nuevoplato_bp.route('/editar/<int:plato_id>', methods=['GET', 'POST'])
def editar_plato(plato_id):
    plato = NuevoPlato.query.get_or_404(plato_id)
    if request.method == 'POST':
        # Campos seguros: asignar solo si existen en el modelo
        if 'nombre' in request.form and hasattr(plato, 'nombre'):
            plato.nombre = request.form.get('nombre')
        if 'descripcion' in request.form and hasattr(plato, 'descripcion'):
            plato.descripcion = request.form.get('descripcion')
        if 'precio' in request.form and hasattr(plato, 'precio'):
            try:
                plato.precio = float(request.form.get('precio') or 0)
            except Exception:
                pass
        # mapear 'seccion' del formulario al atributo que tenga el modelo
        seccion = request.form.get('seccion') or request.form.get('categoria')
        if seccion:
            # Normalize category to Title case so templates matching 'Desayuno/Almuerzo/Cena' work
            seccion_norm = seccion.strip().title()
            if hasattr(plato, 'categoria'):
                plato.categoria = seccion_norm
            elif hasattr(plato, 'seccion'):
                plato.seccion = seccion_norm
        # imagen
        img = request.files.get('imagen')
        if img and img.filename and hasattr(plato, 'imagen'):
            filename = secure_filename(f"{plato_id}_{img.filename}")
            path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(path)
            # guardar ruta relativa para url_for('static', filename=...)
            plato.imagen = path.replace('static/', '').replace('\\','/')
    db.session.commit()
    flash('Plato actualizado', 'success')
    # Añadimos un parámetro de caché para forzar recarga de la imagen en el cliente
    return redirect(url_for('nuevoplato.nuevo_plato') + '?v=' + str(int(time.time())))
    # GET
    return render_template('dashboard/plato_edit.html', plato=plato)

# Eliminar plato
@nuevoplato_bp.route('/eliminar/<int:plato_id>', methods=['POST'])
def eliminar_plato(plato_id):
    plato = NuevoPlato.query.get_or_404(plato_id)
    try:
        # Intentamos eliminar de la forma ORM habitual
        db.session.delete(plato)
        db.session.commit()
        flash('Plato eliminado', 'success')
    except Exception as e:
        # Si falla (p. ej. tabla comentario no existe y SQLAlchemy intenta consultarla),
        # intentamos una eliminación directa por SQL para evitar dependencias ORM.
        db.session.rollback()
        try:
            sql = text('DELETE FROM plato WHERE idPlato = :id')
            db.session.execute(sql, {'id': plato_id})
            db.session.commit()
            flash('Plato eliminado (borrado directo)', 'success')
        except Exception as e2:
            db.session.rollback()
            flash(f'Error eliminando plato: {e2}', 'danger')
    return redirect(request.referrer or (url_for('nuevoplato.nuevo_plato') + '?v=' + str(int(time.time()))))

@nuevoplato_bp.route('/ir_formulario', methods=['GET'])
def ir_formulario():
    return redirect(url_for('nuevoplato.nuevo_plato', open='plato'))

# Crear plato (POST)
@nuevoplato_bp.route('/crear', methods=['POST'])
def crear_plato():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    categoria = (request.form.get('categoria') or '').strip()  # usar 'categoria' que existe en la BD
    img = request.files.get('imagen')

    img_path = None
    if img and img.filename:
        filename = secure_filename(f"{int(time.time())}_{img.filename}")
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(saved_path)
        img_path = os.path.join('uploads', filename).replace('\\','/')

    plato = NuevoPlato()
    if hasattr(plato, 'nombre'): plato.nombre = nombre
    if hasattr(plato, 'descripcion'): plato.descripcion = descripcion
    if hasattr(plato, 'precio'):
        try:
            plato.precio = float(precio) if precio else 0
        except Exception:
            plato.precio = 0

    # asignar la columna que realmente existe en la tabla (categoria)
    if categoria:
        # Normalize stored category to Title case for consistency with templates
        categoria_norm = categoria.title()
        if hasattr(plato, 'categoria'):
            plato.categoria = categoria_norm
        if hasattr(plato, 'seccion'):
            plato.seccion = categoria_norm
    else:
        # valor por defecto para evitar NOT NULL
        if hasattr(plato, 'categoria'):
            plato.categoria = 'General'
        if hasattr(plato, 'seccion'):
            plato.seccion = 'General'

    if img_path and hasattr(plato, 'imagen'):
        plato.imagen = img_path

    # Verificar duplicado: mismo nombre y categoría
    try:
        exists = None
        if nombre:
            qname = nombre.strip()
            if hasattr(NuevoPlato, 'categoria') and getattr(plato, 'categoria', None):
                exists = NuevoPlato.query.filter_by(nombre=qname, categoria=plato.categoria).first()
            else:
                exists = NuevoPlato.query.filter_by(nombre=qname).first()
        if exists:
            flash(f"Ya existe un plato llamado '{nombre}' en la categoría '{getattr(plato,'categoria', 'General')}'. Elige otro nombre.", 'warning')
            return redirect(url_for('nuevoplato.nuevo_plato'))

        db.session.add(plato)
        db.session.commit()
        flash('Plato creado', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creando plato: ' + str(e), 'danger')
    return redirect(url_for('nuevoplato.nuevo_plato') + '?v=' + str(int(time.time())))
