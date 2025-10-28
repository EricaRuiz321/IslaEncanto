from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db


class ReservaHuesped(db.Model):
    __tablename__ = 'reservahuesped'

    id = db.Column(db.Integer, primary_key=True)
    # Contact / primary guest
    nombre = db.Column(db.String(100), nullable=False)
    tipoDocumento = db.Column(db.String(50), nullable=True)
    numeroDocumento = db.Column(db.String(50), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(255), nullable=True)
    procedencia = db.Column(db.String(100), nullable=True)

    # Reservation details
    habitacion_id = db.Column(db.Integer, db.ForeignKey('nuevaHabitacion.id'), nullable=True)
    precio = db.Column(db.Float, nullable=True, default=0.0)
    cantidad_personas = db.Column(db.Integer, nullable=False, default=1)
    check_in = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.Date, nullable=True)
    estado = db.Column(db.String(30), nullable=True, default='Activa')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<ReservaHuesped {self.id} hab:{self.habitacion_id} - {self.nombre}>"
