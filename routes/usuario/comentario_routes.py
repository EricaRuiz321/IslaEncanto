from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
# Asumo que las extensiones como db (SQLAlchemy) están aquí
from utils.extensions import db 
# DEBES AJUSTAR esta importación para que apunte a la ubicación real de tu modelo Comentario
from models.comentario import Comentario 

# Definición del Blueprint. Usamos 'usuario_comentario' como prefijo de endpoint
# y '/usuario/comentarios' como prefijo de URL para agrupar las rutas.
usuario_comentario_bp = Blueprint('usuario_comentario', __name__, url_prefix='/usuario/comentarios')

@usuario_comentario_bp.route('/add', methods=['POST'])
@login_required
def add_comment():
    """
    Ruta para agregar un nuevo comentario a una experiencia.
    Requiere: 'experiencia_id' y 'texto'.
    """
    data = request.form # Esperamos datos de formulario (form-data)

    experiencia_id = data.get('experiencia_id')
    texto = data.get('texto')

    if not all([experiencia_id, texto]):
        return jsonify({"success": False, "message": "Faltan datos requeridos (ID de experiencia o texto)."}), 400

    try:
        # Asegúrate de que el campo para el ID de usuario en tu modelo Comentario
        # se llama 'id_usuario' y que el ID del usuario logueado es 'current_user.id'
        nuevo_comentario = Comentario(
            id_experiencia=experiencia_id,
            id_usuario=current_user.id,
            texto=texto
        )
        db.session.add(nuevo_comentario)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Comentario agregado exitosamente.",
            "comentario": {
                "id": nuevo_comentario.id,
                "texto": nuevo_comentario.texto,
                "autor": current_user.nombre_usuario # Ajusta esto al campo de nombre de tu modelo Usuario
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error al agregar comentario: {str(e)}"}), 500


@usuario_comentario_bp.route('/edit/<int:comment_id>', methods=['POST'])
@login_required
def edit_comment(comment_id):
    """
    Ruta para editar un comentario existente.
    Verifica que el usuario logueado sea el dueño del comentario.
    """
    data = request.form # Esperamos datos de formulario (form-data)

    nuevo_texto = data.get('comment_text')

    if not nuevo_texto:
        return jsonify({"success": False, "message": "El texto del comentario no puede estar vacío."}), 400

    try:
        comentario = db.session.get(Comentario, comment_id)

        if not comentario:
            return jsonify({"success": False, "message": "Comentario no encontrado."}), 404

        # Lógica de autorización: el usuario debe ser el autor
        if comentario.id_usuario != current_user.id:
            return jsonify({"success": False, "message": "No tienes permiso para editar este comentario."}), 403

        comentario.texto = nuevo_texto
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "Comentario editado exitosamente.",
            "comentario": {
                "id": comentario.id,
                "texto": comentario.texto
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error al editar comentario: {str(e)}"}), 500


@usuario_comentario_bp.route('/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    Ruta para eliminar un comentario.
    Verifica que el usuario logueado sea el dueño del comentario.
    """
    try:
        comentario = db.session.get(Comentario, comment_id)

        if not comentario:
            return jsonify({"success": False, "message": "Comentario no encontrado."}), 404

        # Lógica de autorización: el usuario debe ser el autor
        if comentario.id_usuario != current_user.id:
            return jsonify({"success": False, "message": "No tienes permiso para eliminar este comentario."}), 403

        db.session.delete(comentario)
        db.session.commit()

        return jsonify({"success": True, "message": "Comentario eliminado exitosamente."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error al eliminar comentario: {str(e)}"}), 500