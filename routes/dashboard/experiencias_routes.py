import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from utils.extensions import db
from models.comentario import Comentario
from flask_login import current_user

# intentar importar modelos existentes (si fallan, usamos listas vacías en templates)
try:
    from models.nuevoplato import NuevoPlato
except ImportError:
    NuevoPlato = None

try:
    # asegúrate de que el fichero sea models/habitacion.py y la clase Habitacion esté definida allí
    from models.habitacion import Habitacion
except ImportError:
    Habitacion = None

# Blueprint público
experiencias_bp = Blueprint('experiencias', __name__, url_prefix='/experiencias')

@experiencias_bp.route('/', methods=['GET'])
def index():
    platos = NuevoPlato.query.all() if NuevoPlato is not None else []
    habitaciones = Habitacion.query.all() if Habitacion is not None else []
    comentarios = Comentario.query.order_by(Comentario.created_at.desc()).all()

    # detect authentication: prefer flask-login, fallback to session
    try:
        from flask_login import current_user
        is_auth = getattr(current_user, 'is_authenticated', False)
    except Exception:
        is_auth = False
    from flask import session
    if not is_auth:
        is_auth = bool(session.get('rol') or session.get('user'))

    return render_template('home/Experiencias.html', platos=platos, habitaciones=habitaciones, comentarios=comentarios, is_authenticated=is_auth)

@experiencias_bp.route('/comentario', methods=['POST'])
def add_comment():
    contenido = request.form.get('contenido')
    rating = request.form.get('rating')
    tipo = request.form.get('tipo')  # 'plato' / 'habitacion' / 'general'
    item_id = request.form.get('item_id')

    # Intentar obtener current_user (flask-login). Si no existe, admitir login por session (registro/login)
    try:
        from flask_login import current_user
        is_auth = getattr(current_user, 'is_authenticated', False)
    except Exception:
        current_user = None
        is_auth = False

    # Fallback: si no usamos flask-login, permitir usuarios autenticados via session (registro.py / auth.py guardan session['user'])
    from flask import session
    if not is_auth:
        if session.get('user'):
            is_auth = True

    if not is_auth:
        flash('Para añadir un comentario, inicia sesión.', 'warning')
        return redirect(url_for('auth.login') if 'auth' in current_app.blueprints else url_for('login'))

    if not contenido or contenido.strip() == '':
        flash('Comentario vacío', 'warning')
        return redirect(request.referrer or url_for('experiencias.index'))

    # Construir el objeto Comentario usando current_user o session['user']
    user_id = getattr(current_user, 'idUsuario', getattr(current_user, 'id', None)) if current_user else None
    if not user_id:
        # intentar obtener id desde session (registro/login almacena session['user']['id'])
        try:
            user_id = int(session.get('user', {}).get('id')) if session.get('user') else None
        except Exception:
            user_id = None

    comentario = Comentario(
        user_id=user_id,
        contenido=contenido.strip(),
        rating=int(rating) if rating else None,
        created_at=datetime.utcnow()
    )

    if tipo == 'plato' and item_id:
        try:
            comentario.plato_id = int(item_id)
        except Exception:
            pass
    if tipo == 'habitacion' and item_id:
        try:
            comentario.habitacion_id = int(item_id)
        except Exception:
            pass

    db.session.add(comentario)
    db.session.commit()
    flash('Comentario añadido', 'success')
    return redirect(request.referrer or url_for('experiencias.index'))

# ----------------- Admin CRUD para comentarios (mismo archivo) -----------------
admin_bp = Blueprint('experiencias_admin', __name__, url_prefix='/admin/experiencias')

@admin_bp.route('/', methods=['GET'])
def admin_list():
    comentarios = Comentario.query.order_by(Comentario.created_at.desc()).all()
    return render_template('dashboard/experiencias_admin.html', comentarios=comentarios)

# Edición desde modal: recibir POST con contenido y rating
@admin_bp.route('/editar/<int:comentario_id>', methods=['POST'])
def admin_edit(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    contenido = request.form.get('contenido')
    rating = request.form.get('rating')

    comentario.contenido = contenido or comentario.contenido
    comentario.rating = int(rating) if rating else comentario.rating

    db.session.commit()
    flash('Comentario actualizado', 'success')
    return redirect(url_for('experiencias_admin.admin_list'))

@admin_bp.route('/eliminar/<int:comentario_id>', methods=['POST'])
def admin_delete(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    db.session.delete(comentario)
    db.session.commit()
    flash('Comentario eliminado', 'success')
    return redirect(url_for('experiencias_admin.admin_list'))


# ----------------- Rutas para que el usuario edite / elimine sus propios comentarios ---------------
@experiencias_bp.route('/editar/<int:comentario_id>', methods=['POST'])
def user_edit(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    # sólo el autor o admin puede editar
    user_id = getattr(current_user, 'idUsuario', getattr(current_user, 'id', None))
    if not current_user or not getattr(current_user, 'is_authenticated', False):
        flash('Debes iniciar sesión para editar comentarios.', 'warning')
        return redirect(request.referrer or url_for('experiencias.index'))
    if comentario.user_id != user_id and getattr(current_user, 'rol', '') != 'admin':
        flash('No tienes permiso para editar este comentario.', 'danger')
        return redirect(request.referrer or url_for('experiencias.index'))

    contenido = request.form.get('contenido')
    rating = request.form.get('rating')
    comentario.contenido = contenido or comentario.contenido
    comentario.rating = int(rating) if rating else comentario.rating
    db.session.commit()
    flash('Comentario actualizado', 'success')
    return redirect(request.referrer or url_for('experiencias.index'))


@experiencias_bp.route('/eliminar/<int:comentario_id>', methods=['POST'])
def user_delete(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    user_id = getattr(current_user, 'idUsuario', getattr(current_user, 'id', None))
    if not current_user or not getattr(current_user, 'is_authenticated', False):
        flash('Debes iniciar sesión para eliminar comentarios.', 'warning')
        return redirect(request.referrer or url_for('experiencias.index'))
    if comentario.user_id != user_id and getattr(current_user, 'rol', '') != 'admin':
        flash('No tienes permiso para eliminar este comentario.', 'danger')
        return redirect(request.referrer or url_for('experiencias.index'))

    db.session.delete(comentario)
    db.session.commit()
    flash('Comentario eliminado', 'success')
    return redirect(request.referrer or url_for('experiencias.index'))