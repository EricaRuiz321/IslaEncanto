from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db


class ReservaMenu(db.Model):
    __tablename__ = "reserva_menu"

    idReserva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    numeroDocumento = db.Column(db.String(50), nullable=False)
    idMesa = db.Column(db.Integer, db.ForeignKey("mesa.idMesa"), nullable=False)
    idPlato = db.Column(db.Integer, db.ForeignKey("plato.idPlato"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default="Activa")  # Activa o Liberada

    mesa = db.relationship("NuevaMesa", backref="reservas")
    plato = db.relationship("NuevoPlato", backref="reservas")

    def __repr__(self):
        return f"<Reserva {self.nombreCliente}>"