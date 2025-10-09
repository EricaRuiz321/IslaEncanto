"""from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

# ------------------------------
# Tabla de Usuario
# ------------------------------
class Usuario(db.Model):
    __tablename__ = 'usuario'
    idUsuario = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=True, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)  
    direccion = db.Column(db.String(255), nullable=True)
    fechaNacimiento = db.Column(db.Date, nullable=True)
    rol = db.Column(db.String(20), nullable=True, default='usuario')

    def __repr__(self):
        return f"<Usuario {self.usuario}>"


# ------------------------------
# Tabla de nuevaHabitaciones
# ------------------------------
class nuevaHabitacion(db.Model):
    __tablename__ = "nuevaHabitacion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Disponible")
    cupo_personas = db.Column(db.Integer, nullable=False, default=1)
    imagen = db.Column(db.String(255), nullable=True)  # Ruta de la imagen

    def __repr__(self):
        return f"<nuevaHabitacion {self.nombre} - {self.estado}>"
    
    

# ------------------------------
# Tabla de habitacioneHuesped
# ------------------------------
  
class habitacionHuesped(db.Model):
    __tablename__ = "habitacionHuesped"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False, default=1)
    check_in = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.Date, nullable=True)
    

    def __repr__(self):
        return f"<HabitacionHuesped {self.nombre} - {self.check_in} to {self.check_out}>"
    
# ------------------------------
# Tabla de Huéspedes
# ------------------------------
class Huesped(db.Model):
    __tablename__ = "huesped"

    idHuesped = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipoDocumento = db.Column(db.String(50), nullable=False)
    numeroDocumento = db.Column(db.Integer, nullable=False, unique=True)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(255), nullable=True)
    procedencia = db.Column(db.String(100), nullable=True)
    habitacion_id = db.Column(db.Integer, db.ForeignKey("nuevaHabitacion.id"), nullable=False)
    

    def __repr__(self):
        return f"<Huesped {self.nombre} en habitacionHuesped {self.habitacionHuesped_id}>"
    
# ------------------------------
# Tabla de Restaurantes
# ------------------------------
class Restaurante(db.Model):
    __tablename__ = "restaurantes"

    idRestaurante = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_comida = db.Column(db.String(100), nullable=False)
    horario = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Restaurante {self.nombre}>"
        """