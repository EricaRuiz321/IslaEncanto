from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.nuevamesa import NuevaMesa
from models.nuevoplato import NuevoPlato
from models.reservarmenu import ReservaMenu
from utils.extensions import db
from datetime import datetime

usuario_restaurante = Blueprint('usuario_restaurante', __name__)

@usuario_restaurante.route('/usuario/restaurante')
def restaurante_usuario():
    platos = NuevoPlato.query.order_by(NuevoPlato.categoria, NuevoPlato.nombre).all()
    mesas = NuevaMesa.query.filter_by(disponible=True).all()
    return render_template('usuario/restaurante_usuario.html', platos=platos, mesas=mesas)

@usuario_restaurante.route('/usuario/reservar', methods=['POST'])
def reservar():
    # datos cliente(s)
    clientes_nombres = request.form.getlist('cliente_nombre[]')
    clientes_telefonos = request.form.getlist('cliente_telefono[]')

    # mesa y platos (varios)
    idMesa = request.form.get('idMesa')
    platos_ids = request.form.getlist('idPlato[]') or request.form.getlist('idPlato') or []
    fecha = request.form.get('fecha') or datetime.utcnow().date().isoformat()
    hora = request.form.get('hora') or datetime.utcnow().time().strftime("%H:%M")

    if not idMesa or not platos_ids or len(clientes_nombres) == 0:
        flash('Faltan datos para realizar la reserva', 'warning')
        return redirect(url_for('usuario_restaurante.restaurante_usuario'))

    # detalles: crear una ReservaMenu por cada plato seleccionado
    total = 0.0
    platos_seleccionados = []
    reservas_creadas = []
    for pid in platos_ids:
        plato = NuevoPlato.query.get(pid)
        if not plato:
            continue
        total += float(plato.precio or 0)
        platos_seleccionados.append({"id": plato.idPlato, "nombre": plato.nombre, "precio": float(plato.precio)})

    try:
        # Crear reservas (una por plato) usando primer cliente como titular, y guardar también clientes adicionales en la "nota" (detalles)
        titular_nombre = clientes_nombres[0]
        titular_telefono = clientes_telefonos[0] if len(clientes_telefonos) > 0 else ''
        nota_clientes = []
        for i, cn in enumerate(clientes_nombres):
            if cn and cn.strip():
                nota_clientes.append({"nombre": cn.strip(), "telefono": (clientes_telefonos[i] if i < len(clientes_telefonos) else '')})

        for pid in platos_ids:
            nueva_reserva = ReservaMenu(
                nombreCliente = titular_nombre,
                telefono = titular_telefono,
                numeroDocumento = request.form.get('numeroDocumento',''),
                idMesa = int(idMesa),
                idPlato = int(pid),
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date() if isinstance(fecha, str) else fecha,
                hora = datetime.strptime(hora, '%H:%M').time() if isinstance(hora, str) else hora
            )
            db.session.add(nueva_reserva)
            reservas_creadas.append(nueva_reserva)

        # marcar mesa como no disponible
        mesa = NuevaMesa.query.get(int(idMesa))
        if mesa:
            mesa.disponible = False

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error al guardar la reserva: ' + str(e), 'danger')
        return redirect(url_for('usuario_restaurante.restaurante_usuario'))

    # preparar invoice
    invoice = {
        "mesa_numero": mesa.numeroMesa if mesa else f"#{idMesa}",
        "fecha": fecha,
        "hora": hora,
        "clientes": nota_clientes,
        "platos": platos_seleccionados,
        "total": total
    }

    # renderizar la misma vista mostrando invoice en modal
    platos = NuevoPlato.query.order_by(NuevoPlato.categoria, NuevoPlato.nombre).all()
    mesas_disponibles = NuevaMesa.query.filter_by(disponible=True).all()
    return render_template('usuario/restaurante_usuario.html',
                           platos=platos,
                           mesas=mesas_disponibles,
                           invoice=invoice,
                           show_invoice=True)
