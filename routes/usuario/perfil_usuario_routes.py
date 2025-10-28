from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from werkzeug.utils import secure_filename
import os
import uuid
from utils.extensions import db
from models.usuario import Usuario

perfil_usuario_bp = Blueprint('perfil_usuario', __name__, template_folder='../templates')

# Configuración simple para subida de imágenes
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 👉 Ruta para mostrar perfil
@perfil_usuario_bp.route("/perfil_usuario")
def perfil():
    # Identificar usuario en sesión
    if not session.get('user'):
        flash('Debes iniciar sesión para ver el perfil.', 'warning')
        return redirect(url_for('registro.login'))

    uid = session['user'].get('id')
    user = Usuario.query.get(uid)
    if not user:
        flash('Usuario no encontrado en la base de datos.', 'danger')
        return redirect(url_for('registro.login'))

    usuario_dict = {
        'nombre': getattr(user, 'usuario', None),
        'email': getattr(user, 'correo', None),
        'telefono': getattr(user, 'telefono', None),
        'identificacion': getattr(user, 'identificacion', None),
        'direccion': getattr(user, 'direccion', None),
        'membresia': getattr(user, 'membresia', None) or '—',
        'foto': getattr(user, 'foto', None) or 'https://via.placeholder.com/150'
    }

    # Placeholder: si en el futuro se añade relación Reservas, remplazar por datos reales
    reservas_activas = []
    estancias_pasadas = []

    return render_template(
        "usuario/perfil_usuario.html",
        usuario=usuario_dict,
        reservas_activas=reservas_activas,
        estancias_pasadas=estancias_pasadas
    )

# 👉 Ruta para editar perfil
@perfil_usuario_bp.route("/editar_perfil", methods=["POST"])
def editar_perfil():
    if not session.get('user'):
        flash('Debes iniciar sesión para editar el perfil.', 'warning')
        return redirect(url_for('registro.login'))

    uid = session['user'].get('id')
    user = Usuario.query.get(uid)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('registro.login'))

    # Mapear campos del formulario a columnas del modelo
    if 'nombre' in request.form:
        user.usuario = request.form.get('nombre') or user.usuario
    if 'email' in request.form:
        user.correo = request.form.get('email') or user.correo
    if 'telefono' in request.form:
        user.telefono = request.form.get('telefono') or None
    if 'identificacion' in request.form:
        user.identificacion = request.form.get('identificacion') or None
    if 'direccion' in request.form:
        user.direccion = request.form.get('direccion') or None

    db.session.commit()
    # Actualizar valores en session
    session['user']['nombre'] = user.usuario

    flash('Perfil actualizado correctamente.', 'success')
    return redirect(url_for("perfil_usuario.perfil"))


@perfil_usuario_bp.route('/subir_foto', methods=['POST'])
def subir_foto():
    if 'foto' not in request.files:
        flash('No se seleccionó fichero.', 'warning')
        return redirect(url_for('perfil_usuario.perfil'))

    file = request.files['foto']
    if file.filename == '':
        flash('Nombre de fichero vacío.', 'warning')
        return redirect(url_for('perfil_usuario.perfil'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # añadir uuid para evitar colisiones
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{uuid.uuid4().hex}{ext}"
        profiles_dir = os.path.join(current_app.root_path, 'static', 'img', 'profiles')
        os.makedirs(profiles_dir, exist_ok=True)

        filepath = os.path.join(profiles_dir, filename)
        file.save(filepath)

        # si el usuario ya tenía una foto local, intentar eliminarla
        if not session.get('user'):
            flash('Debes iniciar sesión para cambiar la foto.', 'warning')
            return redirect(url_for('registro.login'))

        uid = session['user'].get('id')
        user = Usuario.query.get(uid)
        if not user:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('registro.login'))

        old = getattr(user, 'foto', None)
        try:
            if old and old.startswith(url_for('static', filename='')):
                # extraer ruta relativa después de /static/
                rel = old.split(url_for('static', filename=''))[1].lstrip('/')
                oldpath = os.path.join(current_app.root_path, 'static', rel)
                if os.path.exists(oldpath):
                    os.remove(oldpath)
        except Exception:
            pass

        # Guardar referencia en la BD
        user.foto = url_for('static', filename=f'img/profiles/{filename}')
        db.session.commit()

        flash('Foto de perfil actualizada.', 'success')
        return redirect(url_for('perfil_usuario.perfil'))
    else:
        flash('Formato de imagen no permitido.', 'danger')
        return redirect(url_for('perfil_usuario.perfil'))


@perfil_usuario_bp.route('/eliminar_foto', methods=['POST'])
def eliminar_foto():
    if not session.get('user'):
        flash('Debes iniciar sesión para eliminar la foto.', 'warning')
        return redirect(url_for('registro.login'))

    uid = session['user'].get('id')
    user = Usuario.query.get(uid)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('registro.login'))

    old = getattr(user, 'foto', None)
    try:
        if old and old.startswith(url_for('static', filename='')):
            rel = old.split(url_for('static', filename=''))[1].lstrip('/')
            oldpath = os.path.join(current_app.root_path, 'static', rel)
            if os.path.exists(oldpath):
                os.remove(oldpath)
    except Exception:
        pass

    user.foto = None
    db.session.commit()
    flash('Foto eliminada.', 'info')
    return redirect(url_for('perfil_usuario.perfil'))


@perfil_usuario_bp.route('/eliminar_campo', methods=['POST'])
def eliminar_campo():
    if not session.get('user'):
        flash('Debes iniciar sesión para modificar el perfil.', 'warning')
        return redirect(url_for('registro.login'))

    uid = session['user'].get('id')
    user = Usuario.query.get(uid)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('registro.login'))

    campo = request.form.get('campo')
    # Permitir solo campos seguros
    allowed = {'telefono', 'direccion', 'identificacion', 'foto'}
    if campo and campo in allowed:
        setattr(user, campo, None)
        db.session.commit()
        flash(f'Campo {campo} eliminado.', 'info')
    else:
        flash('Campo no permitido o no encontrado.', 'warning')
    return redirect(url_for('perfil_usuario.perfil'))


@perfil_usuario_bp.route('/eliminar_perfil', methods=['POST'])
def eliminar_perfil():
    # Elimina usuario de la base de datos y su foto local, cierra sesión
    if not session.get('user'):
        flash('Debes iniciar sesión para eliminar el perfil.', 'warning')
        return redirect(url_for('registro.login'))

    uid = session['user'].get('id')
    user = Usuario.query.get(uid)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('registro.login'))

    # intentar borrar foto local si existe
    old = getattr(user, 'foto', None)
    try:
        if old and old.startswith(url_for('static', filename='')):
            rel = old.split(url_for('static', filename=''))[1].lstrip('/')
            oldpath = os.path.join(current_app.root_path, 'static', rel)
            if os.path.exists(oldpath):
                os.remove(oldpath)
    except Exception:
        pass

    # eliminar usuario
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error al eliminar usuario: %s', e)
        flash('Ocurrió un error al eliminar el perfil.', 'danger')
        return redirect(url_for('perfil_usuario.perfil'))

    # cerrar sesión
    session.pop('user', None)
    flash('Tu perfil ha sido eliminado.', 'info')
    return redirect(url_for('registro.login'))