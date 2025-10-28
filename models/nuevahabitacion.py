from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

class NuevaHabitacion(db.Model):
    __tablename__ = "nuevaHabitacion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Disponible")
    cupo_personas = db.Column(db.Integer, nullable=False, default=1)
    imagen = db.Column(db.String(255), nullable=True)  # Ruta de la imagen
    objetos_incluidos = db.Column(db.Text, nullable=True)  # Lista de objetos incluidos (secador, plancha, mini bar, etc.)
    
    # Ahora la relación apunta a ReservaHuesped (modelo unificado)
    huespedes = db.relationship("ReservaHuesped", backref="habitacion", lazy=True)

    def __repr__(self):
        return f"<nuevaHabitacion {self.nombre} - {self.estado}>"
    