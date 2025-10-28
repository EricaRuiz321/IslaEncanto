from flask import Flask, render_template, url_for
import logging
import os
from config import Config
from sqlalchemy import inspect, text
from authlib.integrations.flask_client import OAuth
from utils.extensions import db, bcrypt, serializer

# Registrar blueprints (añade estas importaciones/registro)
from routes.dashboard.experiencias_routes import experiencias_bp, admin_bp as experiencias_admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)

    # serializer puede ser None o no exponer init_app -> inicializar solo si es compatible
    if serializer and hasattr(serializer, 'init_app'):
        serializer.init_app(app)

    # Registrar blueprints
    app.register_blueprint(experiencias_bp)          # /experiencias
    app.register_blueprint(experiencias_admin_bp)    # /admin/experiencias

    from itsdangerous import URLSafeTimedSerializer
    import utils.extensions as extensions

    # Asignar un URLSafeTimedSerializer usable en utils.extensions
    extensions.serializer = URLSafeTimedSerializer(app.secret_key)

    # ------------------------------------------------------------
    # Inyectar variables globales para plantillas
    # ------------------------------------------------------------
    @app.context_processor
    def inject_current_user():
        try:
            from flask_login import current_user
            is_auth = getattr(current_user, 'is_authenticated', False)
        except Exception:
            class _Anonymous:
                is_authenticated = False

            current_user = _Anonymous()
            is_auth = False

        # Detectar endpoint de login disponible dentro del blueprint 'auth' (si existe)
        login_endpoint = None
        if 'auth' in app.blueprints:
            candidates = [ep for ep in app.view_functions.keys() if ep.startswith('auth.')]

            # Preferencias comunes
            if 'auth.login' in candidates:
                login_endpoint = 'auth.login'
            elif 'auth.google_login' in candidates:
                login_endpoint = 'auth.google_login'
            else:
                # Busca cualquier endpoint que contenga 'login' o toma el primero
                login_candidates = [c for c in candidates if 'login' in c]
                login_endpoint = (login_candidates[0] if login_candidates else (candidates[0] if candidates else None))

        # Fallback a 'login' si existe fuera del blueprint
        if not login_endpoint and 'login' in app.view_functions:
            login_endpoint = 'login'

        # Construir una URL absoluta segura para usar en plantillas
        try:
            login_url = url_for(login_endpoint) if login_endpoint else url_for('main.index') if 'main.index' in app.view_functions else '/'
        except Exception:
            login_url = '/'

        # fallback: si no está autentificado vía flask-login, considerar session (registro/login guarda session['user'])
        try:
            from flask import session
            if not is_auth and (session.get('rol') or session.get('user')):
                is_auth = True
        except Exception:
            pass

        return {
            'current_user': current_user,
            'is_authenticated': is_auth,
            'login_endpoint': login_endpoint,
            'login_url': login_url
        }

    # ------------------------------------------------------------
    # Verificar y crear columnas necesarias en la tabla usuario
    # ------------------------------------------------------------
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('usuario')] if 'usuario' in inspector.get_table_names() else []
            stmts = []

            if 'reset_code' not in cols:
                stmts.append("ALTER TABLE usuario ADD COLUMN reset_code VARCHAR(6) NULL")
            if 'reset_expire' not in cols:
                stmts.append("ALTER TABLE usuario ADD COLUMN reset_expire DATETIME NULL")
            # Columnas añadidas recientemente desde el modelo
            if 'telefono' not in cols:
                stmts.append("ALTER TABLE usuario ADD COLUMN telefono VARCHAR(50) NULL")
            if 'identificacion' not in cols:
                stmts.append("ALTER TABLE usuario ADD COLUMN identificacion VARCHAR(100) NULL")
            if 'foto' not in cols:
                stmts.append("ALTER TABLE usuario ADD COLUMN foto VARCHAR(255) NULL")
            if 'membresia' not in cols:
                stmts.append("ALTER TABLE usuario ADD COLUMN membresia VARCHAR(50) NULL")

            # Verificar y crear columnas necesarias en la tabla nuevaHabitacion
            habitacion_cols = [c['name'] for c in inspector.get_columns('nuevaHabitacion')] if 'nuevaHabitacion' in inspector.get_table_names() else []
            
            if 'objetos_incluidos' not in habitacion_cols:
                stmts.append("ALTER TABLE nuevaHabitacion ADD COLUMN objetos_incluidos TEXT NULL")

            # Crear tablas de inventario si no existen
            tables = inspector.get_table_names()
            
            if 'objeto_inventario' not in tables:
                stmts.append("""
                CREATE TABLE objeto_inventario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    descripcion TEXT,
                    categoria VARCHAR(50),
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
                """)
            
            if 'inventario_diario' not in tables:
                stmts.append("""
                CREATE TABLE inventario_diario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    habitacion_id INT NOT NULL,
                    objeto_id INT NOT NULL,
                    fecha_inventario DATE NOT NULL,
                    cantidad_esperada INT DEFAULT 1,
                    cantidad_encontrada INT,
                    estado VARCHAR(20),
                    observaciones TEXT,
                    usuario_inventario VARCHAR(100),
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (habitacion_id) REFERENCES nuevaHabitacion(id),
                    FOREIGN KEY (objeto_id) REFERENCES objeto_inventario(id),
                    UNIQUE KEY unique_inventario (habitacion_id, objeto_id, fecha_inventario)
                )
                """)
            
            if 'inventario_resumen' not in tables:
                stmts.append("""
                CREATE TABLE inventario_resumen (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fecha_inventario DATE NOT NULL UNIQUE,
                    total_habitaciones INT DEFAULT 0,
                    total_objetos_revisados INT DEFAULT 0,
                    objetos_completos INT DEFAULT 0,
                    objetos_faltantes INT DEFAULT 0,
                    objetos_pendientes INT DEFAULT 0,
                    porcentaje_completado FLOAT DEFAULT 0.0,
                    usuario_responsable VARCHAR(100),
                    observaciones_generales TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """)

            for s in stmts:
                try:
                    db.session.execute(text(s))
                    db.session.commit()
                    app.logger.info('Migración aplicada: %s', s)
                except Exception as e:
                    app.logger.exception('No se pudo aplicar la migración %s: %s', s, e)

            db.create_all()

    except Exception as e:
        app.logger.exception('Error inicializando la base de datos: %s', e)

    # ------------------------------------------------------------
    # GOOGLE OAUTH
    # ------------------------------------------------------------
    oauth = OAuth(app)
    app.config['OAUTH'] = oauth

    oauth.register(
        name="google",
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    # ------------------------------------------------------------
    # Registro de Blueprints
    # ------------------------------------------------------------
    from routes.registro import registro_bp
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.dashboard.nuevahabitacion_routes import admin_bp
    from routes.dashboard.perfil_admin_routes import perfil_admin_bp
    from routes.dashboard.inventario_routes import inventario_bp
    from routes.recuperar_contraseña import recuperar_bp
    from routes.usuario.reservahuesped_routes import reservahuesped_bp
    from routes.usuario.perfil_usuario_routes import perfil_usuario_bp
    from routes.dashboard.estadisticasgenerales_routes import estadisticasgenerales_bp
    from routes.dashboard.reservarmenu_routes import reservas_bp
    from routes.dashboard.nuevoplato_routes import nuevoplato_bp
    from routes.dashboard.nuevamesa_routes import nuevamesa_bp
    from routes.usuario.restaurante_routes import usuario_restaurante

    def safe_register(bp, prefix=None):
        """Registra un blueprint evitando duplicar prefijos."""
        try:
            if getattr(bp, 'url_prefix', None):
                app.register_blueprint(bp)
            elif prefix:
                app.register_blueprint(bp, url_prefix=prefix)
            else:
                app.register_blueprint(bp)
        except Exception as e:
            app.logger.exception('Error registrando blueprint %s: %s', getattr(bp, 'name', str(bp)), e)

    # Rutas públicas / secciones
    safe_register(registro_bp, prefix='/registro')
    safe_register(main_bp)
    safe_register(auth_bp)
    safe_register(admin_bp, prefix='/admin')
    safe_register(recuperar_bp, prefix='/recuperar')

    # Perfil de administrador (interfaz para editar el perfil del admin)
    safe_register(perfil_admin_bp, prefix='/admin')
    
    # Inventario de administrador
    safe_register(inventario_bp)

    # Usuario / hospedaje (unificado)
    safe_register(reservahuesped_bp, prefix='/usuario')
    safe_register(perfil_usuario_bp, prefix='/perfil')

    # Dashboard admin
    safe_register(estadisticasgenerales_bp)
    safe_register(reservas_bp, prefix='/admin')
    safe_register(nuevoplato_bp, prefix='/admin')
    safe_register(nuevamesa_bp, prefix='/admin')

    # Usuario restaurante
    safe_register(usuario_restaurante, prefix='/usuario')

    # ------------------------------------------------------------
    # Aliases de Rutas (compatibilidad con plantillas)
    # ------------------------------------------------------------
    from routes import main as _main
    from routes import auth as _auth
    from routes import registro as _registro

    app.add_url_rule('/', endpoint='home', view_func=_main.home)
    app.add_url_rule('/hospedaje', endpoint='hospedaje', view_func=_main.hospedaje)
    app.add_url_rule('/restaurante', endpoint='restaurantes', view_func=_main.restaurantes)
    app.add_url_rule('/nosotros', endpoint='nosotros', view_func=_main.nosotros)
    app.add_url_rule('/Experiencias', endpoint='experiencias', view_func=_main.experiencias, methods=['GET', 'POST'])
    app.add_url_rule('/login', endpoint='login', view_func=_registro.login, methods=['GET', 'POST'])
    app.add_url_rule('/google-login', endpoint='google_login', view_func=_auth.google_login)

    # ------------------------------------------------------------
    # Configuración de logs
    # ------------------------------------------------------------
    logging.basicConfig(level=logging.DEBUG)

    return app


# ------------------------------------------------------------
# Ejecución de la aplicación
# ------------------------------------------------------------
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
