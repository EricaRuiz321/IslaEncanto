from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.extensions import db

class HabitacionHuesped(db.Model):
    __tablename__ = "habitacionHuesped"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False, default=1)
    check_in = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.Date, nullable=True)
    

    def __repr__(self):
        return f"<HabitacionHuesped {self.nombre} - {self.check_in} to {self.check_out}>"