from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.nuevamesa import NuevaMesa
from models.nuevoplato import NuevoPlato
from models.reservarmenu import ReservaMenu
from utils.extensions import db
from datetime import datetime

reservas_bp = Blueprint('reservas', __name__)

# Panel de reservas admin
@reservas_bp.route('/admin/reservas')
def reservas_admin():
    reservas = ReservaMenu.query.all()
    mesas = NuevaMesa.query.all()
    return render_template('dashboard/reservas_admin.html', reservas=reservas, mesas=mesas)

# Liberar mesa
@reservas_bp.route('/admin/liberar/<int:mesa_id>', methods=['POST'])
def liberar_mesa(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)
    mesa.disponible = True

    reserva = ReservaMenu.query.filter_by(idMesa=mesa_id, estado='Activa').first()
    if reserva:
        reserva.estado = 'Liberada'
        db.session.commit()

    flash('Mesa liberada correctamente', 'info')
    return redirect(url_for('reservas.reservas_admin'))
