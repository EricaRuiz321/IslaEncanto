from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

class NuevoPlato(db.Model):
    __tablename__ = "plato"

    idPlato = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # desayuno, almuerzo o cena
    imagen = db.Column(db.String(200), nullable=True)
    idMesa = db.Column(db.Integer, db.ForeignKey("mesa.idMesa"), nullable=True)

    mesa = db.relationship("NuevaMesa", backref="platos")

    def __repr__(self):
        return f"<Plato {self.nombre}>"