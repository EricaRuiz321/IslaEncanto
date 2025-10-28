from flask import Blueprint, render_template, url_for
from datetime import date, timedelta
from sqlalchemy import func, cast, Date
from models.reservahuesped import ReservaHuesped
from models.usuario import Usuario
from models.reservahuesped import ReservaHuesped as HabitacionHuesped
from models.estadisticasgenerales import EstadisticasGenerales
from utils.extensions import db

estadisticasgenerales_bp = Blueprint("estadisticasgenerales", __name__, url_prefix="/admin")

@estadisticasgenerales_bp.route("/dashboard")
def dashboard():
    hoy = date.today()

    # 🔹 Total de huéspedes (suma de cantidad_personas)
    total_huespedes = db.session.query(func.sum(HabitacionHuesped.cantidad_personas)).scalar() or 0

    # 🔹 Check-outs de hoy (comparando solo la fecha sin hora)
    # Usar ReservaHuesped como fuente unificada para check-outs
    checkouts_hoy = (
        db.session.query(
            HabitacionHuesped.nombre,
            HabitacionHuesped.numeroDocumento,
            HabitacionHuesped.telefono,
            HabitacionHuesped.check_in,
            HabitacionHuesped.check_out
        )
        .filter(func.date(HabitacionHuesped.check_out) == hoy)
        .all()
    )


    check_out_hoy = len(checkouts_hoy)

    # 🔹 Usuarios registrados hoy
    usuarios_registrados = Usuario.query.filter(cast(Usuario.fechaRegistro, Date) == hoy).count()

    # 🔹 Guardar o actualizar estadísticas
    estadistica = EstadisticasGenerales.query.filter_by(fecha=hoy).first()
    if estadistica:
        estadistica.total_huespedes = total_huespedes
        estadistica.check_out_hoy = check_out_hoy
        estadistica.usuarios_registrados = usuarios_registrados
    else:
        nueva = EstadisticasGenerales(
            fecha=hoy,
            total_huespedes=total_huespedes,
            usuarios_registrados=usuarios_registrados,
            check_out_hoy=check_out_hoy
        )
        db.session.add(nueva)
    db.session.commit()

    # 🔹 Gráficas últimos 7 días
    labels, data_huespedes, data_usuarios = [], [], []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        registro = EstadisticasGenerales.query.filter_by(fecha=dia).first()
        labels.append(dia.strftime("%d/%m"))
        data_huespedes.append(registro.total_huespedes if registro else 0)
        data_usuarios.append(registro.usuarios_registrados if registro else 0)
    
    # 🔹 Renderizar plantilla
    return render_template(
        "dashboard/estadisticas_admin.html",
        total_huespedes=total_huespedes,
        check_out_hoy=check_out_hoy,
        checkouts_hoy=checkouts_hoy,
        labels=labels,
        data_huespedes=data_huespedes,
        data_usuarios=data_usuarios,
        url_huespedes=url_for('main.home_admin'),
        url_habitaciones=url_for('main.estadisticas_admin'),
    )
