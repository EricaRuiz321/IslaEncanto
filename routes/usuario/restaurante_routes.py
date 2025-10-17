from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.nuevamesa import NuevaMesa
from models.nuevoplato import NuevoPlato
from models.reservarmenu import ReservaMenu
from utils.extensions import db
from datetime import datetime

usuario_restaurante = Blueprint('usuario_restaurante', __name__)

# Página de usuario para ver platos y reservar
@usuario_restaurante.route('/usuario/restaurante')
def restaurante_usuario():
    platos = NuevoPlato.query.all()
    mesas = NuevaMesa.query.filter_by(disponible=True).all()
    return render_template('usuario/restaurante_usuario.html', platos=platos, mesas=mesas)

# Guardar reserva
@usuario_restaurante.route('/usuario/reservar', methods=['POST'])
def reservar():
    nombreCliente = request.form['nombreCliente']
    telefono = request.form['telefono']
    numeroDocumento = request.form['numeroDocumento']
    idMesa = request.form['idMesa']
    idPlato = request.form['idPlato']
    fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
    hora = datetime.strptime(request.form['hora'], '%H:%M').time()

    nueva_reserva = ReservaMenu(
        nombreCliente=nombreCliente,
        telefono=telefono,
        numeroDocumento=numeroDocumento,
        idMesa=idMesa,
        idPlato=idPlato,
        fecha=fecha,
        hora=hora
    )
    db.session.add(nueva_reserva)

    # Marcar mesa como no disponible
    mesa = NuevaMesa.query.get(idMesa)
    mesa.disponible = False
    db.session.commit()

    flash('Reserva realizada correctamente', 'success')
    return redirect(url_for('usuario_restaurante.restaurante_usuario'))
