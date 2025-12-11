from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import date, datetime
from models.nuevahabitacion import NuevaHabitacion
from models.reservahuesped import ReservaHuesped
from models.nuevamesa import NuevaMesa
from models.nuevoplato import NuevoPlato

main_bp = Blueprint('main', __name__)

# ---------------------------------------------------------
# Rutas Home
# ---------------------------------------------------------
@main_bp.route('/')
def home():
    return render_template('home/home.html')


@main_bp.route('/hospedaje')
def hospedaje():
    habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    return render_template('home/hospedaje.html', habitaciones=habitaciones)


@main_bp.route('/restaurante')
def restaurantes():
    # Mostrar platos en el home por sección
    try:
        platos = NuevoPlato.query.order_by(NuevoPlato.nombre).all()
    except Exception:
        platos = []
    return render_template('home/restaurante.html', platos=platos)


@main_bp.route('/nosotros')
def nosotros():
    return render_template('home/nosotros.html')


@main_bp.route('/Experiencias', methods=['GET', 'POST'])
def experiencias():
    # Mostrar platos, habitaciones y comentarios reales desde la base de datos
    try:
        platos = NuevoPlato.query.order_by(NuevoPlato.nombre).all()
    except Exception:
        platos = []

    try:
        habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    except Exception:
        habitaciones = []

    try:
        from models.comentario import Comentario
        comentarios = Comentario.query.order_by(Comentario.created_at.desc()).all()
    except Exception:
        comentarios = []

    # Detectar si el usuario está logueado: preferir flask-login, fallback a session
    try:
        from flask_login import current_user
        is_auth = getattr(current_user, 'is_authenticated', False)
    except Exception:
        is_auth = False
    if not is_auth:
        is_auth = bool(session.get('rol') or session.get('user'))

    return render_template('home/experiencias.html', platos=platos, habitaciones=habitaciones, comentarios=comentarios, is_authenticated=is_auth)


# -----------------------------------------------------------
# Rutas Usuario
# -----------------------------------------------------------
@main_bp.route('/home_usuario')
def home_usuario():
    return render_template('usuario/home_usuario.html')


@main_bp.route('/hospedaje_usuario')
def hospedaje_usuario():
    habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    return render_template('usuario/hospedaje_usuario.html', habitaciones=habitaciones, current_date=date.today())


@main_bp.route('/nosotros_usuario')
def nosotros_usuario():
    return render_template('usuario/nosotros_usuario.html')


@main_bp.route('/restaurante_usuario')
def restaurante_usuario():
    # Mostrar platos también en la vista de usuario
    try:
        platos = NuevoPlato.query.order_by(NuevoPlato.nombre).all()
    except Exception:
        platos = []
    try:
        mesas = NuevaMesa.query.filter_by(disponible=True).all()
    except Exception:
        mesas = []
    return render_template('usuario/restaurante_usuario.html', platos=platos, mesas=mesas)


@main_bp.route('/experiencias_usuario')
def experiencias_usuario():
    # Asegurar que la plantilla recibe los mismos objetos que la vista pública
    try:
        platos = NuevoPlato.query.order_by(NuevoPlato.nombre).all()
    except Exception:
        platos = []
    try:
        habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    except Exception:
        habitaciones = []

    # Comentarios: usar el modelo Comentario si está disponible
    try:
        from models.comentario import Comentario
        comentarios = Comentario.query.order_by(Comentario.created_at.desc()).all()
    except Exception:
        comentarios = []

    # Detectar si el usuario está logueado: preferir flask-login, fallback a session
    try:
        from flask_login import current_user
        is_auth = getattr(current_user, 'is_authenticated', False)
    except Exception:
        is_auth = False
    # fallback: sesión usada por demo-login o implementaciones sin flask-login
    from flask import session
    if not is_auth:
        is_auth = bool(session.get('rol') or session.get('user'))

    return render_template('usuario/experiencias_usuario.html', platos=platos, habitaciones=habitaciones, comentarios=comentarios, is_authenticated=is_auth)


# ------------------------------------------------------------
# Rutas Admin
# ------------------------------------------------------------
@main_bp.route('/home_admin')
def home_admin():
    return render_template('dashboard/home_admin.html')


@main_bp.route('/hospedaje_admin')
def hospedaje_admin():
    # Mostrar reservas (modelo unificado)
    huespedes = ReservaHuesped.query.all()
    habitaciones = NuevaHabitacion.query.all()
    return render_template('dashboard/hospedaje_admin.html', huespedes=huespedes, habitaciones=habitaciones)


@main_bp.route('/habitaciones_admin')
def habitaciones_admin():
    habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    
    # Obtener objetos disponibles desde la tabla de inventario
    from models.objetoinventario import ObjetoInventario
    objetos_disponibles = ObjetoInventario.query.filter_by(activo=True).order_by(ObjetoInventario.nombre).all()
    
    return render_template('dashboard/habitaciones_admin.html', 
                         habitaciones=habitaciones, 
                         objetos_disponibles=objetos_disponibles)


@main_bp.route('/estadisticas_admin')
def estadisticas_admin():
    # Aquí puedes importar tus estadísticas reales o redirigir al blueprint
    return redirect(url_for('estadisticasgenerales.dashboard'))


@main_bp.route('/admin/restaurante')
def restaurante_admin():
    platos = NuevoPlato.query.all()
    mesas = NuevaMesa.query.all()
    # Mostrar por defecto la vista de Reservas para que aparezca primero
    return render_template('dashboard/restaurante_admin.html', platos=platos, mesas=mesas)


@main_bp.route('/experiencias_admin')
def experiencias_admin():
    # Asegúrate de importar los modelos necesarios si no lo están ya
    from models.comentario import Comentario 
    
    try:
        platos = NuevoPlato.query.order_by(NuevoPlato.nombre).all()
    except Exception:
        platos = []
    try:
        habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    except Exception:
        habitaciones = []
    try:
        # El administrador ve TODOS los comentarios, no solo los suyos
        comentarios = Comentario.query.order_by(Comentario.created_at.desc()).all()
    except Exception:
        comentarios = []
        
    # Asume que tienes un Blueprint llamado 'experiencias_admin' para las rutas de acción
    return render_template('dashboard/experiencias_admin.html', 
                           platos=platos, 
                           habitaciones=habitaciones, 
                           comentarios=comentarios)

@main_bp.route('/nosotros_admin')
def nosotros_admin():
    return render_template('dashboard/nosotros_admin.html')




# ------------------------------------------------------------
# Ruta de login demo para pruebas rápidas
# ------------------------------------------------------------
@main_bp.route('/demo-login', methods=['GET', 'POST'])
def demo_login():
    # Demo login kept for quick testing under /demo-login
    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('password')

        if username == "admin" and password == "1234":
            session['rol'] = 'admin'
            return redirect(url_for('main.home_admin'))
        else:
            session['rol'] = 'usuario'
            return redirect(url_for('main.home_usuario'))

    return render_template('home/Login.html')
