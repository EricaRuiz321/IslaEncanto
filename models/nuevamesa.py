from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

class NuevaMesa(db.Model):
    __tablename__ = "mesa"

    idMesa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numeroMesa = db.Column(db.String(20), nullable=False, unique=True)
    capacidad = db.Column(db.Integer, nullable=False)
    disponible = db.Column(db.Boolean, default=True)  # True = libre
    ubicacion = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Mesa {self.numeroMesa}>"