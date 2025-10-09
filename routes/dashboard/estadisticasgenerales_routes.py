from flask import Blueprint, render_template
from datetime import date, timedelta
from sqlalchemy import func
from models.huesped import Huesped
from models.usuario import Usuario
from models.nuevahabitacion import NuevaHabitacion
from models.habitacionhuesped import HabitacionHuesped
from models.estadisticasgenerales import EstadisticasGenerales
from utils.extensions import db

estadisticasgenerales_bp = Blueprint("estadisticasgenerales", __name__, url_prefix="/admin")


@estadisticasgenerales_bp.route("/dashboard")
def dashboard():
    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=6)

    # 🔹 Recolectar estadísticas del día
    total_huespedes = Huesped.query.count()
    check_out_hoy = HabitacionHuesped.query.filter(HabitacionHuesped.check_out == hoy).count()
    usuarios_registrados = Usuario.query.filter(db.func.date(Usuario.fechaRegistro) == hoy).count()

    # 🔹 Guardar o actualizar estadísticas generales del día
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

    # 🔹 Gráficas (últimos 7 días)
    labels = []
    data_huespedes = []
    data_usuarios = []

    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        registro = EstadisticasGenerales.query.filter_by(fecha=dia).first()

        labels.append(dia.strftime("%d/%m"))
        data_huespedes.append(registro.total_huespedes if registro else 0)
        data_usuarios.append(registro.usuarios_registrados if registro else 0)

    # 🔹 Traer habitaciones para mostrar en hospedaje_admin
    habitaciones = NuevaHabitacion.query.all()

    return render_template(
        "dashboard/hospedaje_admin.html",
        habitaciones=habitaciones,
        total_huespedes=total_huespedes,
        check_out_hoy=check_out_hoy,
        labels=labels,
        data_huespedes=data_huespedes,
        data_usuarios=data_usuarios
    )
