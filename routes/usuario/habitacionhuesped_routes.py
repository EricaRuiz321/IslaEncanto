from flask import Blueprint, render_template, request, redirect, url_for
from models.habitacionhuesped import HabitacionHuesped
from models.nuevahabitacion import NuevaHabitacion
from utils.extensions import db
from datetime import date

habitacionHuesped_bp = Blueprint('habitacionHuesped', __name__)

@habitacionHuesped_bp.route('/hospedaje_usuario')
def hospedaje_usuario():
    print("hospedaje usuario ------------")
    habitaciones = NuevaHabitacion.query.all()
    habitacion_id = request.args.get("habitacion_id")  # <-- detecta si se acaba de reservar
    return render_template(
        'usuario/hospedaje_usuario.html',
        habitaciones=habitaciones,
        current_date=date.today().strftime("%Y-%m-%d"),
        habitacion_id=habitacion_id
    )



@habitacionHuesped_bp.route('/reservar_habitacion', methods=['POST'])
def reservar_habitacion():
    habitacion_id = request.form.get("habitacion_id")
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    cantidad_personas = int(request.form.get("cantidad_personas", 1))
    check_in = request.form.get("check_in") or date.today()
    check_out = request.form.get("check_out")

    habitacion = NuevaHabitacion.query.get(habitacion_id)
    if habitacion and cantidad_personas > habitacion.cupo_personas:
        return redirect(url_for('habitacionHuesped.hospedaje_usuario'))

    # Guardar reserva
    reserva = HabitacionHuesped(
        nombre=nombre,
        precio=precio,
        cantidad_personas=cantidad_personas,
        check_in=check_in,
        check_out=check_out
    )
    db.session.add(reserva)

    if habitacion:
        habitacion.estado = "Ocupada"

    db.session.commit()

    # Redirigir al formulario de huésped pasándole la habitación
    return redirect(url_for('habitacionHuesped.hospedaje_usuario', habitacion_id=habitacion_id))

@habitacionHuesped_bp.route('/liberar_habitacion/<int:habitacion_id>', methods=['POST'])
def liberar_habitacion(habitacion_id):
    habitacion = NuevaHabitacion.query.get(habitacion_id)
    if habitacion:
        # Borrar los huéspedes asociados
        from models.huesped import Huesped
        Huesped.query.filter_by(habitacion_id=habitacion_id).delete()
        # Cambiar estado
        habitacion.estado = "Disponible"
        db.session.commit()
    return redirect(url_for('main.hospedaje_admin'))


@habitacionHuesped_bp.route('/nuevo_huesped')
def nuevo_huesped():
    # Tomar la primera habitación disponible
    habitacion = NuevaHabitacion.query.filter_by(estado="Disponible").first()

    if habitacion:
        # Redirigir al hospedaje_usuario con el ID y una marca para abrir el modal de reserva
        return redirect(url_for('main.hospedaje_usuario', habitacion_id=habitacion.id, abrir='reserva'))
    else:
        # Si no hay disponibles, solo abrir la vista
        return redirect(url_for('main.hospedaje_usuario'))
