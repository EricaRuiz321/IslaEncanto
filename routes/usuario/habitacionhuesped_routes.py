from flask import Blueprint, render_template, request, redirect, url_for
from models.habitacionhuesped import HabitacionHuesped
from models.nuevahabitacion import NuevaHabitacion
from utils.extensions import db
from datetime import date

habitacionHuesped_bp = Blueprint('habitacionHuesped', __name__)

@habitacionHuesped_bp.route('/hospedaje_usuario')
def hospedaje_usuario():
    habitaciones = HabitacionHuesped.query.all()
    habitacion_id = request.args.get("habitacion_id")  # <-- para saber si se acaba de reservar
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

    # Cambiar estado
    if habitacion:
        habitacion.estado = "Ocupada"

    db.session.commit()

    # Redirigir usando el ID de la NUEVA reserva
    return redirect(url_for('habitacionHuesped.hospedaje_usuario', habitacion_id=reserva.id))
