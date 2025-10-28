from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

class ObjetoInventario(db.Model):
    """Tabla de objetos disponibles para inventario"""
    __tablename__ = "objeto_inventario"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(50), nullable=True)  # electrodomesticos, mobiliario, amenidades, etc.
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con inventarios diarios
    inventarios = db.relationship("InventarioDiario", backref="objeto", lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ObjetoInventario {self.nombre}>"