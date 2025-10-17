from flask import Blueprint, request, redirect, url_for, flash
from models.nuevamesa import NuevaMesa
from utils.extensions import db

nuevamesa_bp = Blueprint('nuevamesa', __name__)

# Añadir nueva mesa
@nuevamesa_bp.route('/admin/mesa/nueva', methods=['POST'])
def nueva_mesa():
    numeroMesa = request.form['numeroMesa']
    capacidad = request.form['capacidad']
    ubicacion = request.form['ubicacion']

    nueva = NuevaMesa(numeroMesa=numeroMesa, capacidad=capacidad, ubicacion=ubicacion)
    db.session.add(nueva)
    db.session.commit()

    flash('Mesa añadida correctamente', 'success')
    return redirect(url_for('main.restaurante_admin'))
