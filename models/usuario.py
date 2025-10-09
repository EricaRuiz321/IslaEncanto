from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date
from utils.extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    idUsuario = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=True, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)  
    direccion = db.Column(db.String(255), nullable=True)
    fechaNacimiento = db.Column(db.Date, nullable=True)
    rol = db.Column(db.String(20), nullable=True, default='usuario')
    fechaRegistro = db.Column(db.Date, default=date.today)

    def __repr__(self):
        return f"<Usuario {self.usuario}>"