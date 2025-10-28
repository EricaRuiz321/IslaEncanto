from datetime import datetime
from utils.extensions import db

class Comentario(db.Model):
    __tablename__ = 'comentario'
    idComentario = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # opcionales para relacionar el comentario con un plato o habitación
    plato_id = db.Column(db.Integer, db.ForeignKey('plato.idPlato'), nullable=True)
    habitacion_id = db.Column(db.Integer, nullable=True)

    user = db.relationship('Usuario', backref=db.backref('comentarios', lazy='dynamic'))
    # relación con plato si existe el modelo y tabla 'plato'
    try:
        from models.nuevoplato import NuevoPlato as _NP  # pragma: no cover
        plato = db.relationship('NuevoPlato', backref=db.backref('comentarios', lazy='dynamic'), foreign_keys=[plato_id])
    except Exception:
        plato = None