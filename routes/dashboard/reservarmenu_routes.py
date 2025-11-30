# -------------------- IMPORTS --------------------
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime

# Modelos
from utils.extensions import db
from models.nuevoplato import NuevoPlato
from models.nuevamesa import NuevaMesa
from models.reservarmenu import ReservaMenu


# -------------------- BLUEPRINTS --------------------

# 🔹 1. BLUEPRINT PARA RUTAS API (JSON/CARRITO)
reservarmenu_bp = Blueprint("reservarmenu_bp", __name__)

# 🔹 2. BLUEPRINT PARA RUTAS DE VISTAS DE ADMINISTRACIÓN (HTML/RENDER_TEMPLATE)
# NOTA: Se mantiene 'reservas_bp' con su prefijo /admin
reservas_bp = Blueprint(
    'reservas_bp',
    __name__,
    url_prefix='/admin'
)

# ---------------------------------------------------
# 🚀 RUTAS API (reservarmenu_bp)
# ---------------------------------------------------

# 🔹 1. GUARDAR RESERVAS DESDE EL CARRITO (POST)
@reservarmenu_bp.route("/reservar_carrito", methods=["POST"])
def reservar_carrito():
    data = request.get_json()

    nombre = data.get("nombre")
    telefono = data.get("telefono")
    documento = data.get("documento")
    idMesa = data.get("mesa")
    fecha = data.get("fecha")
    hora = data.get("hora")
    platos = data.get("platos", [])

    if not all([nombre, documento, idMesa, fecha, hora, platos]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    # Convertir fecha y hora
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

    # Buscar mesa por ID
    try:
        mesa = NuevaMesa.query.get(int(idMesa))
    except ValueError:
        return jsonify({"error": "ID de mesa inválido"}), 400

    if not mesa:
        return jsonify({"error": "La mesa no existe"}), 404
    
    # Crear una reserva por cada plato del carrito
    reserva = None
    for item in platos:
        reserva = ReservaMenu(
            nombreCliente=nombre,
            telefono=telefono,
            numeroDocumento=documento,
            idMesa=mesa.idMesa,
            idPlato=item["idPlato"],
            fecha=fecha_obj,
            hora=hora_obj,
            estado="Activa"
        )
        db.session.add(reserva)

    # Marcar mesa como ocupada
    if hasattr(mesa, "estado"):
        mesa.estado = "Reservada"
    elif hasattr(mesa, "disponible"):
        mesa.disponible = False

    db.session.commit()

    # Devolver el ID de la última reserva creada
    return jsonify({"message": "Reservas creadas con éxito", "id_reserva": reserva.idReserva}), 200


# 🔹 2. LISTAR TODAS LAS RESERVAS (GET)
@reservarmenu_bp.route("/reservas", methods=["GET"])
def obtener_reservas():
    reservas = ReservaMenu.query.all()

    resultado = []
    for r in reservas:
        resultado.append({
            "idReserva": r.idReserva,
            "nombreCliente": r.nombreCliente,
            "telefono": r.telefono,
            "documento": r.numeroDocumento,
            "mesa": r.mesa.numeroMesa if r.mesa else None,
            "plato": r.plato.nombre if r.plato else None,
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "hora": r.hora.strftime("%H:%M"),
            "estado": r.estado
        })

    return jsonify(resultado), 200


# 🔹 3. CANCELAR UNA RESERVA (PUT)
@reservarmenu_bp.route("/cancelar_reserva/<int:idReserva>", methods=["PUT"])
def cancelar_reserva(idReserva):
    reserva = ReservaMenu.query.get(idReserva)

    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    reserva.estado = "Cancelada"
    db.session.commit()

    return jsonify({"message": "Reserva cancelada"}), 200


# 🔹 4. LIBERAR UNA MESA MANUALMENTE (PUT)
@reservarmenu_bp.route("/liberar_mesa/<int:idMesa>", methods=["PUT"])
def liberar_mesa_api(idMesa):
    mesa = NuevaMesa.query.get(idMesa)

    if not mesa:
        return jsonify({"error": "Mesa no encontrada"}), 404

    if hasattr(mesa, "estado"):
        mesa.estado = "Disponible"
    elif hasattr(mesa, "disponible"):
        mesa.disponible = True

    db.session.commit()

    return jsonify({"message": "Mesa liberada"}), 200


# ---------------------------------------------------
# 🖥️ RUTAS DE VISTAS DE ADMINISTRACIÓN (reservas_bp)
# ---------------------------------------------------

# 🔹 5. LISTAR RESERVAS Y MESAS (GET - Vista)
@reservas_bp.route('/', methods=['GET'])
def reservas_admin():
    # Obtener mesas ordenadas
    mesas = NuevaMesa.query.order_by(
        getattr(NuevaMesa, 'numeroMesa', NuevaMesa.idMesa)
    ).all()
    
    # Obtener platos para el modal de edición
    platos = NuevoPlato.query.all()

    # Obtener reservas ordenadas
    reservas = ReservaMenu.query.order_by(
        getattr(ReservaMenu, 'fecha', ReservaMenu.idReserva).desc()
    ).all()

    return render_template(
        'dashboard/reservas_admin.html',
        reservas=reservas,
        mesas=mesas,
        platos=platos
    )


# 🔹 6. RESERVAR UNA MESA (POST - Vista)
@reservas_bp.route('/reservar/<int:mesa_id>', methods=['POST'])
def reservar_mesa_vista(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)

    nombre = request.form.get('nombreCliente')
    telefono = request.form.get('telefono')
    # detalles = request.form.get('detalles') # Ya se determinó que no existe en el modelo
    documento = request.form.get('numeroDocumento')

    # Crear la reserva
    reserva = ReservaMenu(nombreCliente=nombre)

    # Asignar campos extras si existen en el modelo
    reserva.telefono = telefono if hasattr(reserva, 'telefono') else None
    reserva.idMesa = mesa_id if hasattr(reserva, 'idMesa') else None
    reserva.numeroDocumento = documento if hasattr(reserva, 'numeroDocumento') else None

    # Asignar fecha y hora
    try:
        fecha_str = request.form.get('fecha', '')
        # Asumiendo que el campo 'fecha' está presente en el formulario de reserva de mesa.
        reserva.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else datetime.utcnow().date()
    except Exception:
        reserva.fecha = datetime.utcnow().date()

    try:
        hora_str = request.form.get('hora', '')
        # Asumiendo que el campo 'hora' está presente en el formulario de reserva de mesa.
        reserva.hora = datetime.strptime(hora_str, '%H:%M').time() if hora_str else datetime.utcnow().time()
    except Exception:
        reserva.hora = datetime.utcnow().time()
        
    reserva.estado = 'Activa' # Establecer estado por defecto
    # Si la reserva incluye plato (como el formulario general del otro HTML), asignarlo
    id_plato = request.form.get('idPlato')
    if id_plato and hasattr(reserva, 'idPlato'):
         try:
             reserva.idPlato = int(id_plato)
         except ValueError:
             pass

    db.session.add(reserva)

    # Marcar mesa como no disponible/reservada
    if hasattr(mesa, 'disponible'):
        mesa.disponible = False
    elif hasattr(mesa, 'estado'):
        mesa.estado = 'Reservada'

    db.session.commit()

    flash('Mesa reservada', 'success')
    # Redirigir a la vista de administración de reservas
    return redirect(request.referrer or url_for('reservas_bp.reservas_admin'))


# 🔹 7. LIBERAR MESA (POST - Vista)
@reservas_bp.route('/liberar/<int:mesa_id>', methods=['POST'])
def liberar_mesa_vista(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)

    # Marcar mesa como libre/disponible
    if hasattr(mesa, 'disponible'):
        mesa.disponible = True
    elif hasattr(mesa, 'estado'):
        mesa.estado = 'Libre'

    # Si la reserva tiene idMesa, marcar como finalizada
    if hasattr(ReservaMenu, 'idMesa'):
        # Buscamos solo las reservas activas/reservadas asociadas a esta mesa
        reservas = ReservaMenu.query.filter_by(idMesa=mesa_id, estado='Activa').all()
        for r in reservas:
            if hasattr(r, 'estado'):
                r.estado = 'Finalizada'

    db.session.commit()

    flash('Mesa liberada', 'success')
    # Redirigir a la vista de administración de reservas
    return redirect(request.referrer or url_for('reservas_bp.reservas_admin'))


# 🔹 8. EDITAR CLIENTE DE LA RESERVA (POST - Vista)
@reservas_bp.route('/editar_cliente', methods=['POST'])
def editar_reserva_cliente():
    # En el HTML se recomienda pasar el idReserva si existe.
    # Como el HTML actual usa la última reserva de una mesa, usamos el mesa_id_hidden.
    
    mesa_id_form = request.form.get('mesa_id_hidden')
    id_reserva_form = request.form.get('idReserva_hidden') # Asumiendo que se puede pasar

    if not mesa_id_form:
        flash('Error: ID de mesa no proporcionado', 'danger')
        return redirect(request.referrer or url_for('reservas_bp.reservas_admin'))

    try:
        mesa_id = int(mesa_id_form)
    except ValueError:
        flash('Error: ID de mesa inválido', 'danger')
        return redirect(request.referrer or url_for('reservas_bp.reservas_admin'))
    
    # Intenta obtener la reserva por ID si se pasa, si no, usa la última de la mesa.
    reserva = None
    if id_reserva_form:
        try:
            reserva = ReservaMenu.query.get(int(id_reserva_form))
        except ValueError:
             pass # Si es inválido, buscar por mesa
             
    if not reserva:
        # Obtenemos la última reserva asociada a esa mesa
        reserva = (
            ReservaMenu.query
            .filter_by(idMesa=mesa_id)
            .order_by(getattr(ReservaMenu, 'idReserva', 'id').desc())
            .first() 
        )

    if not reserva:
        flash('No se encontró reserva activa para editar', 'warning')
        return redirect(request.referrer or url_for('reservas_bp.reservas_admin'))

    # Actualizar datos básicos
    nombre = request.form.get('nombreCliente')
    telefono = request.form.get('telefono')
    numeroDocumento = request.form.get('numeroDocumento')
    idPlato = request.form.get('idPlato')
    fecha_str = request.form.get('fecha', '')
    hora_str = request.form.get('hora', '')
    estado = request.form.get('estado')
    
    # La lógica de 'hasattr' está bien para asegurar la portabilidad del modelo, la mantengo
    if hasattr(reserva, 'nombreCliente'):
        reserva.nombreCliente = nombre or reserva.nombreCliente

    if hasattr(reserva, 'telefono'):
        reserva.telefono = telefono or reserva.telefono

    if hasattr(reserva, 'numeroDocumento') and numeroDocumento is not None:
        reserva.numeroDocumento = (
            numeroDocumento or reserva.numeroDocumento
        )

    if idPlato and hasattr(reserva, 'idPlato'):
        try:
            reserva.idPlato = int(idPlato)
        except Exception:
            pass

    if hasattr(reserva, 'fecha') and fecha_str:
        try:
            reserva.fecha = datetime.strptime(
                fecha_str, '%Y-%m-%d'
            ).date()
        except Exception:
            pass

    if hasattr(reserva, 'hora') and hora_str:
        try:
            reserva.hora = datetime.strptime(
                hora_str, '%H:%M'
            ).time()
        except Exception:
            pass

    if hasattr(reserva, 'estado') and estado:
        reserva.estado = estado

    db.session.commit()

    flash('Reserva actualizada', 'success')
    return redirect(request.referrer or url_for('reservas_bp.reservas_admin'))