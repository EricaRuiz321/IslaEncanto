from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from utils.extensions import db

class EstadisticasGenerales(db.Model):
    __tablename__ = "estadisticasGenerales"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False, unique=True, default=date.today)
    total_huespedes = db.Column(db.Integer, nullable=False, default=0)
    usuarios_registrados = db.Column(db.Integer, nullable=False, default=0)
    check_out_hoy = db.Column(db.Integer, nullable=False, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EstadisticasGenerales {self.fecha} - H:{self.total_huespedes} U:{self.usuarios_registrados}>"
