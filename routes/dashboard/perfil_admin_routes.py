from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from werkzeug.utils import secure_filename
import os, uuid
from utils.extensions import db
from models.usuario import Usuario

perfil_admin_bp = Blueprint('perfil_admin', __name__, template_folder='../../templates')

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required():
    # Per user request: remove admin-only restriction for these routes.
    # This function now always returns True so the perfil_admin routes are accessible
    # regardless of role. NOTE: This is insecure for production; consider restricting
    # individual actions if needed.
    return True


@perfil_admin_bp.route('/perfil_admin')
def perfil_admin():
    # Render the admin profile. If there's a logged session user, use it; otherwise
    # show placeholder data so the page still renders.
    user = None
    sess = session.get('user') or {}
    # Require that the current session is an admin so we show the correct admin data
    if not sess or sess.get('rol') != 'admin':
        flash('Acceso restringido: inicia sesión como administrador para ver este perfil.', 'warning')
        return redirect(url_for('registro.login'))

    uid = sess.get('id')
    if uid:
        user = Usuario.query.get(uid)

    # If we couldn't find a user by id, try to recover by correo from session
    if not user:
        correo = sess.get('correo')
        if correo:
            user = Usuario.query.filter_by(correo=correo).first()

    # If session indicates admin role but we still don't have a user, try to find any admin account as fallback
    if not user and sess.get('rol') == 'admin':
        user = Usuario.query.filter_by(rol='admin').first()
    if not user:
        usuario_dict = {
            'nombre': None,
            'email': None,
            'telefono': None,
            'identificacion': None,
            'direccion': None,
            'membresia': 'Admin',
            'foto': 'https://via.placeholder.com/150'
        }
    else:
        usuario_dict = {
            'nombre': getattr(user, 'usuario', None),
            'email': getattr(user, 'correo', None),
            'telefono': getattr(user, 'telefono', None),
            'identificacion': getattr(user, 'identificacion', None),
            'direccion': getattr(user, 'direccion', None),
            'membresia': getattr(user, 'membresia', None) or 'Admin',
            'foto': getattr(user, 'foto', None) or 'https://via.placeholder.com/150'
        }

    reservas_activas = []
    estancias_pasadas = []

    # pass authentication flags so template can show logout button and adjust UI
    is_authenticated = bool(sess)
    is_admin = (sess.get('rol') == 'admin')
    return render_template('dashboard/perfil_admin.html', usuario=usuario_dict, reservas_activas=reservas_activas, estancias_pasadas=estancias_pasadas, is_authenticated=is_authenticated, is_admin=is_admin)


@perfil_admin_bp.route('/editar_perfil_admin', methods=['POST'])
def editar_perfil_admin():
    # admin_required() intentionally returns True per user request
    uid = session.get('user', {}).get('id')
    user = Usuario.query.get(uid) if uid else None
    if not user:
        flash('Administrador no encontrado.', 'danger')
        return redirect(url_for('perfil_admin.perfil_admin'))

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
    # update session display name if present
    if session.get('user'):
        session['user']['nombre'] = user.usuario
    flash('Perfil de administrador actualizado.', 'success')
    return redirect(url_for('perfil_admin.perfil_admin'))


@perfil_admin_bp.route('/subir_foto_admin', methods=['POST'])
def subir_foto_admin():
    uid = session.get('user', {}).get('id')
    user = Usuario.query.get(uid) if uid else None
    if 'foto' not in request.files:
        flash('No se seleccionó fichero.', 'warning')
        return redirect(url_for('perfil_admin.perfil_admin'))

    file = request.files['foto']
    if file.filename == '':
        flash('Nombre de fichero vacío.', 'warning')
        return redirect(url_for('perfil_admin.perfil_admin'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{uuid.uuid4().hex}{ext}"

        profiles_dir = os.path.join(current_app.root_path, 'static', 'img', 'profiles')
        os.makedirs(profiles_dir, exist_ok=True)

        filepath = os.path.join(profiles_dir, filename)
        file.save(filepath)

        if user:
            old = getattr(user, 'foto', None)
            try:
                if old and old.startswith(url_for('static', filename='')):
                    rel = old.split(url_for('static', filename=''))[1].lstrip('/')
                    oldpath = os.path.join(current_app.root_path, 'static', rel)
                    if os.path.exists(oldpath):
                        os.remove(oldpath)
            except Exception:
                pass

            user.foto = url_for('static', filename=f'img/profiles/{filename}')
            db.session.commit()
            flash('Foto de administrador actualizada.', 'success')
        else:
            flash('Usuario no identificado para asociar la foto.', 'warning')

        return redirect(url_for('perfil_admin.perfil_admin'))
    else:
        flash('Formato de imagen no permitido.', 'danger')
        return redirect(url_for('perfil_admin.perfil_admin'))


@perfil_admin_bp.route('/eliminar_foto_admin', methods=['POST'])
def eliminar_foto_admin():
    uid = session.get('user', {}).get('id')
    user = Usuario.query.get(uid) if uid else None
    if user:
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
    else:
        flash('Usuario no identificado.', 'warning')

    return redirect(url_for('perfil_admin.perfil_admin'))


@perfil_admin_bp.route('/eliminar_perfil_admin', methods=['POST'])
def eliminar_perfil_admin():
    uid = session.get('user', {}).get('id')
    user = Usuario.query.get(uid) if uid else None
    if not user:
        flash('Administrador no encontrado.', 'danger')
        return redirect(url_for('perfil_admin.perfil_admin'))

    old = getattr(user, 'foto', None)
    try:
        if old and old.startswith(url_for('static', filename='')):
            rel = old.split(url_for('static', filename=''))[1].lstrip('/')
            oldpath = os.path.join(current_app.root_path, 'static', rel)
            if os.path.exists(oldpath):
                os.remove(oldpath)
    except Exception:
        pass

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error al eliminar admin: %s', e)
        flash('Ocurrió un error al eliminar el perfil.', 'danger')
        return redirect(url_for('perfil_admin.perfil_admin'))

    session.pop('user', None)
    session.pop('rol', None)
    flash('Perfil de administrador eliminado.', 'info')
    return redirect(url_for('registro.login'))
    
