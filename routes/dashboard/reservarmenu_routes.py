from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.nuevamesa import NuevaMesa
from models.nuevoplato import NuevoPlato
from models.reservarmenu import ReservaMenu
from utils.extensions import db
from datetime import datetime

reservas_bp = Blueprint('reservas', __name__, url_prefix='/admin/reservas')

@reservas_bp.route('/', methods=['GET'])
def reservas_admin():
    mesas = NuevaMesa.query.order_by(getattr(NuevaMesa, 'numeroMesa', NuevaMesa.idMesa)).all()
    reservas = ReservaMenu.query.order_by(getattr(ReservaMenu, 'fecha', ReservaMenu.idReserva).desc()).all()
    return render_template('dashboard/reservas_admin.html', reservas=reservas, mesas=mesas)

@reservas_bp.route('/reservar/<int:mesa_id>', methods=['POST'])
def reservar_mesa(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)
    nombre = request.form.get('nombreCliente')
    telefono = request.form.get('telefono')
    detalles = request.form.get('detalles')

    reserva = ReservaMenu(nombreCliente=nombre)
    # asignar campos opcionales si el modelo los tiene
    if hasattr(reserva, 'telefono'):
        reserva.telefono = telefono
    if hasattr(reserva, 'detalles'):
        reserva.detalles = detalles
    if hasattr(reserva, 'idMesa'):
        reserva.idMesa = mesa_id
    if hasattr(reserva, 'fecha'):
        try:
            reserva.fecha = datetime.strptime(request.form.get('fecha',''), '%Y-%m-%d').date()
        except Exception:
            reserva.fecha = datetime.utcnow().date()
    if hasattr(reserva, 'hora'):
        try:
            reserva.hora = datetime.strptime(request.form.get('hora',''), '%H:%M').time()
        except Exception:
            reserva.hora = datetime.utcnow().time()

    db.session.add(reserva)
    # marcar mesa como no disponible si el atributo existe
    if hasattr(mesa, 'disponible'):
        mesa.disponible = False
    elif hasattr(mesa, 'estado'):
        mesa.estado = 'Reservada'
    db.session.commit()
    flash('Mesa reservada', 'success')
    return redirect(request.referrer or url_for('reservas.reservas_admin'))

@reservas_bp.route('/liberar/<int:mesa_id>', methods=['POST'])
def liberar_mesa(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)
    # marcar mesa libre
    if hasattr(mesa, 'disponible'):
        mesa.disponible = True
    elif hasattr(mesa, 'estado'):
        mesa.estado = 'Libre'
    # opcional: cerrar/actualizar reservas asociadas
    if hasattr(ReservaMenu, 'idMesa'):
        for r in ReservaMenu.query.filter_by(idMesa=mesa_id).all():
            if hasattr(r, 'estado'):
                r.estado = 'Finalizada'
    db.session.commit()
    flash('Mesa liberada', 'success')
    return redirect(request.referrer or url_for('reservas.reservas_admin'))

@reservas_bp.route('/editar_cliente/<int:mesa_id>', methods=['POST'])
def editar_reserva_cliente(mesa_id):
    nombre = request.form.get('nombreCliente')
    telefono = request.form.get('telefono')
    # buscar última reserva de la mesa (si existe campo idMesa)
    reserva = None
    if hasattr(ReservaMenu, 'idMesa'):
        reserva = ReservaMenu.query.filter_by(idMesa=mesa_id).order_by(getattr(ReservaMenu, 'idReserva', 'id').desc()).first()
    else:
        reserva = ReservaMenu.query.order_by(getattr(ReservaMenu, 'idReserva', 'id').desc()).first()
    if not reserva:
        flash('No se encontró reserva para editar', 'warning')
        return redirect(request.referrer or url_for('reservas.reservas_admin'))

    # campos básicos
    if hasattr(reserva, 'nombreCliente'):
        reserva.nombreCliente = nombre or reserva.nombreCliente
    if hasattr(reserva, 'telefono'):
        reserva.telefono = telefono or reserva.telefono

    # campos adicionales: numeroDocumento, idPlato, fecha, hora, estado
    numeroDocumento = request.form.get('numeroDocumento')
    idPlato = request.form.get('idPlato')
    fecha_str = request.form.get('fecha','')
    hora_str = request.form.get('hora','')
    estado = request.form.get('estado')

    if hasattr(reserva, 'numeroDocumento') and numeroDocumento is not None:
        reserva.numeroDocumento = numeroDocumento or reserva.numeroDocumento

    if idPlato:
        try:
            if hasattr(reserva, 'idPlato'):
                reserva.idPlato = int(idPlato)
        except Exception:
            pass

    if hasattr(reserva, 'fecha') and fecha_str:
        try:
            reserva.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except Exception:
            pass

    if hasattr(reserva, 'hora') and hora_str:
        try:
            reserva.hora = datetime.strptime(hora_str, '%H:%M').time()
        except Exception:
            pass

    if hasattr(reserva, 'estado') and estado:
        reserva.estado = estado

    db.session.commit()
    flash('Reserva actualizada', 'success')
    return redirect(request.referrer or url_for('reservas.reservas_admin'))