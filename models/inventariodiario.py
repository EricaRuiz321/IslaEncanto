from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from utils.extensions import db

class InventarioDiario(db.Model):
    """Tabla de inventarios diarios por habitación y objeto"""
    __tablename__ = "inventario_diario"
    
    id = db.Column(db.Integer, primary_key=True)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('nuevaHabitacion.id'), nullable=False)
    objeto_id = db.Column(db.Integer, db.ForeignKey('objeto_inventario.id'), nullable=False)
    fecha_inventario = db.Column(db.Date, default=date.today, nullable=False)
    cantidad_esperada = db.Column(db.Integer, default=1, nullable=False)  # Cantidad que debería haber
    cantidad_encontrada = db.Column(db.Integer, nullable=True)  # Cantidad que realmente hay
    estado = db.Column(db.String(20), nullable=True)  # 'completo', 'faltante', 'pendiente'
    observaciones = db.Column(db.Text, nullable=True)
    usuario_inventario = db.Column(db.String(100), nullable=True)  # Quien hizo el inventario
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    habitacion = db.relationship("NuevaHabitacion", backref="inventarios_diarios")
    
    # Índice único para evitar duplicados por día
    __table_args__ = (db.UniqueConstraint('habitacion_id', 'objeto_id', 'fecha_inventario', name='_habitacion_objeto_fecha_uc'),)
    
    def __repr__(self):
        return f"<InventarioDiario {self.habitacion.nombre} - {self.objeto.nombre} - {self.fecha_inventario}>"
    
    @property
    def estado_calculado(self):
        """Calcula el estado basado en las cantidades"""
        if self.cantidad_encontrada is None:
            return 'pendiente'
        elif self.cantidad_encontrada >= self.cantidad_esperada:
            return 'completo'
        else:
            return 'faltante'
    
    @property
    def color_estado(self):
        """Devuelve el color para mostrar en la interfaz"""
        estado = self.estado_calculado
        if estado == 'completo':
            return 'success'  # Verde
        elif estado == 'faltante':
            return 'danger'   # Rojo
        else:
            return 'warning'  # Amarillo para pendiente