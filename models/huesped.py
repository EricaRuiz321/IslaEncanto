from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

class Huesped(db.Model):
    __tablename__ = "huesped"

    idHuesped = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipoDocumento = db.Column(db.String(50), nullable=False)
    numeroDocumento = db.Column(db.Integer, nullable=False, unique=True)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(255), nullable=True)
    procedencia = db.Column(db.String(100), nullable=True)
    habitacion_id = db.Column(db.Integer, db.ForeignKey("nuevaHabitacion.id"), nullable=True)
    

    def __repr__(self):
        return f"<Huesped {self.nombre} en habitacion {self.habitacion_id}>"
