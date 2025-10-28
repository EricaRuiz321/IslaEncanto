from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.reservahuesped import ReservaHuesped
from models.nuevahabitacion import NuevaHabitacion
from utils.extensions import db
from datetime import date, datetime

reservahuesped_bp = Blueprint('reservahuesped', __name__, url_prefix='/reservahuesped')


@reservahuesped_bp.route('/hospedaje_usuario')
def hospedaje_usuario():
    habitaciones = NuevaHabitacion.query.all()
    habitacion_id = request.args.get('habitacion_id')
    abrir = request.args.get('abrir')
    return render_template(
        'usuario/hospedaje_usuario.html',
        habitaciones=habitaciones,
        current_date=date.today().strftime('%Y-%m-%d'),
        habitacion_id=habitacion_id,
        abrir=abrir
    )


@reservahuesped_bp.route('/reservar_habitacion', methods=['POST'])
def reservar_habitacion():
    habitacion_id = request.form.get('habitacion_id')
    nombre = request.form.get('nombre')
    precio = float(request.form.get('precio') or 0)
    cantidad_personas = int(request.form.get('cantidad_personas', 1))
    check_in = request.form.get('check_in') or date.today()
    check_out = request.form.get('check_out')

    habitacion = NuevaHabitacion.query.get(habitacion_id)
    if habitacion and cantidad_personas > habitacion.cupo_personas:
        return redirect(url_for('reservahuesped.hospedaje_usuario'))

    reserva = ReservaHuesped(
        nombre=nombre,
        precio=precio,
        cantidad_personas=cantidad_personas,
        check_in=check_in,
        check_out=check_out,
        habitacion_id=habitacion_id
    )
    db.session.add(reserva)
    if habitacion:
        habitacion.estado = 'Ocupada'
    db.session.commit()
    return redirect(url_for('reservahuesped.hospedaje_usuario', habitacion_id=habitacion_id, abrir='datos'))


@reservahuesped_bp.route('/liberar_habitacion/<int:habitacion_id>', methods=['POST'])
def liberar_habitacion(habitacion_id):
    habitacion = NuevaHabitacion.query.get(habitacion_id)
    if habitacion:
        # Eliminar reservas asociadas a la habitación (si se desea)
        ReservaHuesped.query.filter_by(habitacion_id=habitacion_id).delete()
        habitacion.estado = 'Disponible'
        db.session.commit()
    return redirect(url_for('main.hospedaje_admin'))


@reservahuesped_bp.route('/nuevo_huesped')
def nuevo_huesped():
    habitacion = NuevaHabitacion.query.filter_by(estado='Disponible').first()
    if habitacion:
        return redirect(url_for('reservahuesped.hospedaje_usuario', habitacion_id=habitacion.id, abrir='reserva'))
    return redirect('/reservahuesped/hospedaje_usuario')


@reservahuesped_bp.route('/cambiar_estado', methods=['POST'])
def cambiar_estado():
    habitacion_id = request.form.get('habitacion_id')
    nuevo_estado = request.form.get('estado')
    if not habitacion_id or not nuevo_estado:
        return redirect(url_for('main.hospedaje_admin'))
    habitacion = NuevaHabitacion.query.get(habitacion_id)
    if not habitacion:
        return redirect(url_for('main.hospedaje_admin'))
    habitacion.estado = nuevo_estado
    db.session.commit()
    return redirect(url_for('main.hospedaje_admin'))


@reservahuesped_bp.route('/reservar_con_huespedes', methods=['POST'])
def reservar_con_huespedes():
    """
    Recibe arrays de datos de huéspedes desde el formulario de usuario.
    Crea una única ReservaHuesped (nivel reserva) y mantiene en memoria la lista
    de huéspedes para mostrarse en la factura (no los persiste individualmente).
    """
    habitacion_id = request.form.get('habitacion_id')
    precio = float(request.form.get('precio', 0))
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')

    nombres = request.form.getlist('nombre[]')
    tipos = request.form.getlist('tipoDocumento[]')
    numeros = request.form.getlist('numeroDocumento[]')
    procedencias = request.form.getlist('procedencia[]')
    telefonos = request.form.getlist('telefono[]')
    correos = request.form.getlist('correo[]')

    if not habitacion_id or not nombres:
        return redirect(url_for('reservahuesped.hospedaje_usuario'))

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date() if check_in_str else date.today()
    except Exception:
        check_in = date.today()
    try:
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date() if check_out_str else check_in
    except Exception:
        check_out = check_in

    dias = max(1, (check_out - check_in).days or 1)
    cantidad_huespedes = len([n for n in nombres if n and n.strip()]) or 1

    # Crear un registro por cada huésped proporcionado (guardamos cada uno en reservahuesped)
    creado_huespedes = []
    habitacion = NuevaHabitacion.query.get(habitacion_id)
    for i in range(len(nombres)):
        nombre = nombres[i].strip() if nombres[i] else None
        if not nombre:
            continue

        tipo = tipos[i] if i < len(tipos) else None
        numero = numeros[i] if i < len(numeros) else None
        procedencia = procedencias[i] if i < len(procedencias) else None
        telefono = telefonos[i] if i < len(telefonos) else None
        correo = correos[i] if i < len(correos) else None

        r = ReservaHuesped(
            nombre=nombre,
            tipoDocumento=tipo or '',
            numeroDocumento=str(numero) if numero is not None else '',
            telefono=telefono,
            correo=correo,
            procedencia=procedencia,
            habitacion_id=habitacion_id,
            precio=precio,
            cantidad_personas=1,
            check_in=check_in,
            check_out=check_out
        )
        db.session.add(r)

        creado_huespedes.append({
            'nombre': nombre,
            'tipoDocumento': tipo,
            'numeroDocumento': numero,
            'telefono': telefono,
            'correo': correo
        })

    # Marcar habitación como ocupada si existe y confirmar cambios
    if habitacion:
        habitacion.estado = 'Ocupada'

    db.session.commit()

    # El precio es por habitación por día, no por persona
    total = precio * dias
    factura = {
        'habitacion_id': habitacion_id,
        'habitacion_nombre': habitacion.nombre if habitacion else f'Habitación {habitacion_id}',
        'precio': precio,
        'dias': dias,
        'cantidad_huespedes': cantidad_huespedes,
        'total': total,
        'check_in': check_in.strftime('%Y-%m-%d'),
        'check_out': check_out.strftime('%Y-%m-%d'),
        'huespedes': creado_huespedes
    }

    habitaciones = NuevaHabitacion.query.order_by(NuevaHabitacion.id.desc()).all()
    return render_template(
        'usuario/hospedaje_usuario.html',
        habitaciones=habitaciones,
        current_date=date.today().strftime('%Y-%m-%d'),
        invoice=factura,
        show_invoice=True
    )


@reservahuesped_bp.route('/editar_huesped/<int:huesped_id>', methods=['POST'])
def editar_huesped(huesped_id):
    # Editar datos en el registro de reserva (si existe)
    r = ReservaHuesped.query.get_or_404(huesped_id)
    r.nombre = request.form.get('nombre') or r.nombre
    r.telefono = request.form.get('telefono') or r.telefono
    r.correo = request.form.get('correo') or r.correo
    r.tipoDocumento = request.form.get('tipoDocumento') or r.tipoDocumento
    r.numeroDocumento = request.form.get('numeroDocumento') or r.numeroDocumento
    r.procedencia = request.form.get('procedencia') or r.procedencia
    r.check_in = request.form.get('check_in') or r.check_in
    r.check_out = request.form.get('check_out') or r.check_out
    try:
        db.session.commit()
        flash('Reserva actualizada', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar reserva: ' + str(e), 'danger')
    return redirect(request.referrer or url_for('main.habitaciones_admin'))


@reservahuesped_bp.route('/guardar_huesped', methods=['POST'])
def guardar_huesped():
    # Endpoint para añadir huésped/contacto desde formularios compactos (se crea una reserva)
    habitacion_id = request.form.get('habitacion_id')
    nombre = request.form.get('nombre')
    tipo_doc = request.form.get('tipoDocumento')
    numero_doc = request.form.get('numeroDocumento')
    procedencia = request.form.get('procedencia')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')

    if not habitacion_id:
        return redirect(url_for('reservahuesped.hospedaje_usuario'))

    reserva = ReservaHuesped(
        nombre=nombre,
        tipoDocumento=tipo_doc,
        numeroDocumento=numero_doc,
        telefono=telefono,
        correo=correo,
        procedencia=procedencia,
        habitacion_id=habitacion_id
    )
    db.session.add(reserva)
    db.session.commit()

    if request.form.get('agregar_otro'):
        return redirect(url_for('reservahuesped.hospedaje_usuario', habitacion_id=habitacion_id))
    return redirect(url_for('reservahuesped.hospedaje_usuario'))


@reservahuesped_bp.route('/eliminar_huesped/<int:huesped_id>', methods=['POST'])
def eliminar_huesped(huesped_id):
    """Eliminar un huésped específico del sistema"""
    try:
        huesped = ReservaHuesped.query.get_or_404(huesped_id)
        
        # Obtener la habitación antes de eliminar para posible liberación
        habitacion_id = huesped.habitacion_id
        
        # Eliminar el huésped
        db.session.delete(huesped)
        
        # Verificar si quedan más huéspedes en la habitación
        huespedes_restantes = ReservaHuesped.query.filter_by(habitacion_id=habitacion_id).count()
        
        # Si no quedan huéspedes, liberar la habitación automáticamente
        if huespedes_restantes == 0 and habitacion_id:
            from models.nuevahabitacion import NuevaHabitacion
            habitacion = NuevaHabitacion.query.get(habitacion_id)
            if habitacion:
                habitacion.estado = 'Disponible'
        
        db.session.commit()
        flash('Huésped eliminado correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar huésped: {str(e)}', 'danger')
    
    return redirect(url_for('main.hospedaje_admin'))
