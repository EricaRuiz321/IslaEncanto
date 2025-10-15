from flask import Blueprint, request, redirect, url_for
from models.huesped import Huesped
from models.habitacionhuesped import HabitacionHuesped
from utils.extensions import db
from datetime import date

huesped_bp = Blueprint('huesped', __name__)

@huesped_bp.route('/guardar_huesped', methods=['POST'])
def guardar_huesped():
    habitacion_id = request.form.get("habitacion_id")
    nombre = request.form.get("nombre")
    tipo_doc = request.form.get("tipoDocumento")
    numero_doc = request.form.get("numeroDocumento")
    procedencia = request.form.get("procedencia")
    telefono = request.form.get("telefono")
    correo = request.form.get("correo")

    # Guardar huésped
    huesped = Huesped(
        nombre=nombre,
        tipoDocumento=tipo_doc,
        numeroDocumento=numero_doc,
        telefono=telefono,
        correo=correo,
        procedencia=procedencia,
        habitacion_id=habitacion_id
    )
    db.session.add(huesped)
    db.session.commit()

    # Si presionó "Agregar otro", volvemos a mostrar el modal
    if request.form.get("agregar_otro"):
        return redirect(url_for('habitacionHuesped.hospedaje_usuario', habitacion_id=habitacion_id))

    # Si no, terminamos y regresamos normalmente
    return redirect(url_for('habitacionHuesped.hospedaje_usuario'))
