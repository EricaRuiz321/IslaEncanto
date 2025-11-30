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

# --------------------------------------------------------
# LISTAR PLATOS
# --------------------------------------------------------
@nuevoplato_bp.route('/', methods=['GET'])
def nuevo_plato():
    platos = NuevoPlato.query.order_by(NuevoPlato.nombre).all()
    return render_template('dashboard/restaurante_admin.html', platos=platos)

# --------------------------------------------------------
# EDITAR PLATO
# --------------------------------------------------------
@nuevoplato_bp.route('/editar/<int:plato_id>', methods=['GET', 'POST'])
def editar_plato(plato_id):
    plato = NuevoPlato.query.get_or_404(plato_id)

    if request.method == 'POST':

        if hasattr(plato, 'nombre'):
            plato.nombre = request.form.get('nombre')

        if hasattr(plato, 'descripcion'):
            plato.descripcion = request.form.get('descripcion')

        if hasattr(plato, 'precio'):
            try:
                plato.precio = float(request.form.get('precio') or 0)
            except:
                plato.precio = 0

        # IMAGEN
        img = request.files.get('imagen')
        if img and img.filename and hasattr(plato, 'imagen'):
            filename = secure_filename(f"{plato_id}_{img.filename}")
            path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(path)
            plato.imagen = path.replace('static/', '').replace('\\', '/')

        db.session.commit()
        flash('Plato actualizado', 'success')
        return redirect(url_for('nuevoplato.nuevo_plato') + '?v=' + str(int(time.time())))

    return render_template('dashboard/plato_edit.html', plato=plato)

# --------------------------------------------------------
# ELIMINAR PLATO
# --------------------------------------------------------
@nuevoplato_bp.route('/eliminar/<int:plato_id>', methods=['POST'])
def eliminar_plato(plato_id):
    plato = NuevoPlato.query.get_or_404(plato_id)

    try:
        db.session.delete(plato)
        db.session.commit()
        flash('Plato eliminado', 'success')

    except Exception:
        db.session.rollback()
        try:
            sql = text('DELETE FROM plato WHERE idPlato = :id')
            db.session.execute(sql, {'id': plato_id})
            db.session.commit()
            flash('Plato eliminado (método directo)', 'success')
        except Exception as e2:
            db.session.rollback()
            flash(f'Error eliminando plato: {e2}', 'danger')

    return redirect(request.referrer or url_for('nuevoplato.nuevo_plato'))

# --------------------------------------------------------
# IR AL FORMULARIO
# --------------------------------------------------------
@nuevoplato_bp.route('/ir_formulario', methods=['GET'])
def ir_formulario():
    return redirect(url_for('nuevoplato.nuevo_plato', open='plato'))

# --------------------------------------------------------
# CREAR PLATO
# --------------------------------------------------------
@nuevoplato_bp.route('/crear', methods=['POST'])
def crear_plato():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    img = request.files.get('imagen')

    # Imagen
    img_path = None
    if img and img.filename:
        filename = secure_filename(f"{int(time.time())}_{img.filename}")
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(saved_path)
        img_path = os.path.join('uploads', filename).replace('\\', '/')

    plato = NuevoPlato()

    if hasattr(plato, 'nombre'):
        plato.nombre = nombre

    if hasattr(plato, 'descripcion'):
        plato.descripcion = descripcion

    if hasattr(plato, 'precio'):
        try:
            plato.precio = float(precio) if precio else 0
        except:
            plato.precio = 0

    if img_path and hasattr(plato, 'imagen'):
        plato.imagen = img_path

    # Validación: nombre duplicado
    existe = NuevoPlato.query.filter_by(nombre=nombre).first()
    if existe:
        flash(f"Ya existe un plato llamado '{nombre}'.", "warning")
        return redirect(url_for('nuevoplato.nuevo_plato'))

    try:
        db.session.add(plato)
        db.session.commit()
        flash("Plato creado con éxito", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error creando plato: " + str(e), "danger")

    return redirect(url_for('nuevoplato.nuevo_plato') + '?v=' + str(int(time.time())))
