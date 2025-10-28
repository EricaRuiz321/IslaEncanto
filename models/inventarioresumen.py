from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from utils.extensions import db

class InventarioResumen(db.Model):
    """Tabla de resumen de inventarios por fecha"""
    __tablename__ = "inventario_resumen"
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_inventario = db.Column(db.Date, default=date.today, nullable=False, unique=True)
    total_habitaciones = db.Column(db.Integer, default=0)
    total_objetos_revisados = db.Column(db.Integer, default=0)
    objetos_completos = db.Column(db.Integer, default=0)
    objetos_faltantes = db.Column(db.Integer, default=0)
    objetos_pendientes = db.Column(db.Integer, default=0)
    porcentaje_completado = db.Column(db.Float, default=0.0)
    usuario_responsable = db.Column(db.String(100), nullable=True)
    observaciones_generales = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<InventarioResumen {self.fecha_inventario} - {self.porcentaje_completado}%>"
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del resumen basado en los inventarios diarios"""
        # Importar aquí para evitar circular imports
        from models.inventariodiario import InventarioDiario
        
        inventarios_dia = InventarioDiario.query.filter_by(fecha_inventario=self.fecha_inventario).all()
        
        self.total_objetos_revisados = len(inventarios_dia)
        self.objetos_completos = len([i for i in inventarios_dia if i.estado_calculado == 'completo'])
        self.objetos_faltantes = len([i for i in inventarios_dia if i.estado_calculado == 'faltante'])
        self.objetos_pendientes = len([i for i in inventarios_dia if i.estado_calculado == 'pendiente'])
        
        # Calcular porcentaje (solo objetos revisados, no pendientes)
        objetos_revisados = self.objetos_completos + self.objetos_faltantes
        if objetos_revisados > 0:
            self.porcentaje_completado = round((self.objetos_completos / objetos_revisados) * 100, 2)
        else:
            self.porcentaje_completado = 0.0
        
        # Contar habitaciones únicas
        habitaciones_inventario = set([i.habitacion_id for i in inventarios_dia])
        self.total_habitaciones = len(habitaciones_inventario)