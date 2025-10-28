from flask import Blueprint, request, redirect, url_for, flash, render_template
from models.nuevamesa import NuevaMesa
from utils.extensions import db

nuevamesa_bp = Blueprint('nuevamesa', __name__, url_prefix='/admin/nuevamesa')

# Añadir nueva mesa
@nuevamesa_bp.route('/nueva', methods=['POST'])
def nueva_mesa():
    numeroMesa = request.form.get('numeroMesa')
    capacidad = request.form.get('capacidad', 4)
    ubicacion = request.form.get('ubicacion', None)
    if not numeroMesa:
        flash('Número de mesa requerido', 'warning')
        return redirect(request.referrer or '/admin')
    # comprobar duplicado por numero de mesa
    if NuevaMesa.query.filter_by(numeroMesa=numeroMesa).first():
        flash(f"Ya existe la mesa {numeroMesa}. Elige otro número.", 'warning')
        return redirect(request.referrer or '/admin')

    mesa = NuevaMesa(numeroMesa=numeroMesa, capacidad=int(capacidad) if capacidad else 4)
    # opcional: guardar ubicación si el modelo tiene el campo
    if hasattr(mesa, 'ubicacion') and ubicacion:
        mesa.ubicacion = ubicacion
    db.session.add(mesa)
    db.session.commit()
    flash('Mesa creada', 'success')
    return redirect(request.referrer or '/admin')

# Editar mesa (POST)
@nuevamesa_bp.route('/editar/<int:mesa_id>', methods=['POST'])
def editar_mesa(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)
    numero = request.form.get('numeroMesa') or mesa.numeroMesa
    capacidad = request.form.get('capacidad') or getattr(mesa, 'capacidad', None)
    ubicacion = request.form.get('ubicacion') if 'ubicacion' in request.form else getattr(mesa, 'ubicacion', None)
    mesa.numeroMesa = numero
    if capacidad is not None:
        try:
            mesa.capacidad = int(capacidad)
        except Exception:
            pass
    if hasattr(mesa, 'ubicacion') and ubicacion is not None:
        mesa.ubicacion = ubicacion
    db.session.commit()
    flash('Mesa actualizada', 'success')
    return redirect(request.referrer or '/admin')

# Eliminar mesa (POST)
@nuevamesa_bp.route('/eliminar/<int:mesa_id>', methods=['POST'])
def eliminar_mesa(mesa_id):
    mesa = NuevaMesa.query.get_or_404(mesa_id)
    db.session.delete(mesa)
    db.session.commit()
    flash('Mesa eliminada', 'success')
    return redirect(request.referrer or '/admin')