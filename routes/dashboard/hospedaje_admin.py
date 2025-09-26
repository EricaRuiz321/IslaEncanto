from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.baseDatos import db, nuevaHabitacion, Usuario
from flask import session

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Ruta para mostrar formulario de edición de habitación
@admin_bp.route("/hospedaje/editar/<int:habitacion_id>", methods=["GET"])
def hospedaje_editar(habitacion_id):
    habitacion = nuevaHabitacion.query.get_or_404(habitacion_id)
    return render_template("dashboard/editar_habitacion.html", habitacion=habitacion)

# Ruta para actualizar habitación en la base de datos
@admin_bp.route("/hospedaje/editar/<int:habitacion_id>", methods=["POST"])
def hospedaje_actualizar(habitacion_id):
    habitacion = nuevaHabitacion.query.get_or_404(habitacion_id)
    try:
        habitacion.nombre = request.form["nombre"]
        habitacion.precio = float(request.form["precio"])
        habitacion.cupo_personas = int(request.form.get("cupo_personas", 1))
        habitacion.estado = request.form.get("estado", "Disponible")
        imagen_file = request.files.get("imagen")
        if imagen_file and imagen_file.filename:
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(imagen_file.filename)
            img_folder = os.path.join("Static", "img")
            os.makedirs(img_folder, exist_ok=True)
            save_path = os.path.join(img_folder, filename)
            imagen_file.save(save_path)
            habitacion.imagen = f"img/{filename}"
        db.session.commit()
    # flash("✅ Habitación actualizada correctamente", "success")
    except Exception as e:
        db.session.rollback()
    # flash(f"❌ Error al actualizar la habitación: {e}", "danger")
    return redirect(url_for("admin.hospedaje_index"))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.baseDatos import db, nuevaHabitacion, Usuario
from flask import session

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ==========================
# 📌 SECCIÓN HOSPEDAJE
# ==========================
@admin_bp.route("/hospedaje")
def hospedaje_index():
    habitaciones = nuevaHabitacion.query.all()
    return render_template("dashboard/hospedaje_admin.html", habitaciones=habitaciones)

# ➕ añadir nueva habitación ----------------------------------------------------------

@admin_bp.route("/hospedaje/nueva", methods=["POST"])
def hospedaje_nueva():
    try:
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        cupo_personas = int(request.form.get("cupo_personas", 1))
        estado = request.form.get("estado", "Disponible")

        imagen_file = request.files.get("imagen")
        imagen_path = None
        if imagen_file and imagen_file.filename:
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(imagen_file.filename)
            img_folder = os.path.join("static", "img")  # 👈 corregí Static → static
            os.makedirs(img_folder, exist_ok=True)
            save_path = os.path.join(img_folder, filename)
            imagen_file.save(save_path)
            imagen_path = f"img/{filename}"

        habitacion = nuevaHabitacion(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            estado=estado,
            cupo_personas=cupo_personas,
            imagen=imagen_path
        )
        db.session.add(habitacion)
        db.session.commit()

        flash("✅ Habitación creada correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al crear la habitación: {e}", "danger")

    return redirect(url_for("admin.hospedaje_index"))


# ✏️ editar habitación --------------------------------------------------------------------------

@admin_bp.route("/hospedaje/editar/<int:habitacion_id>", methods=["POST"])
def hospedaje_editar(habitacion_id):
    habitacion = nuevaHabitacion.query.get_or_404(habitacion_id)
    try:
        habitacion.nombre = request.form["nombre"]
        habitacion.descripcion = request.form["descripcion"]
        habitacion.precio = float(request.form["precio"])
        habitacion.estado = request.form["estado"]
        habitacion.cupo_personas = int(request.form["cupo_personas"])

        imagen_file = request.files.get("imagen")
        if imagen_file and imagen_file.filename:
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(imagen_file.filename)
            img_folder = os.path.join("static", "img")
            os.makedirs(img_folder, exist_ok=True)
            save_path = os.path.join(img_folder, filename)
            imagen_file.save(save_path)
            habitacion.imagen = f"img/{filename}"

        db.session.commit()
        flash("✅ Habitación actualizada correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al editar la habitación: {e}", "danger")
    return redirect(url_for("admin.hospedaje_index"))


# 🗑️ eliminar habitación --------------------------------------------------------------------

@admin_bp.route("/hospedaje/eliminar/<int:habitacion_id>", methods=["POST"])
def hospedaje_eliminar(habitacion_id):
    habitacion = nuevaHabitacion.query.get_or_404(habitacion_id)
    try:
        db.session.delete(habitacion)  # 👈 aquí estaba el error
        db.session.commit()
        flash("🗑️ Habitación eliminada", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al eliminar: {e}", "danger")

    return redirect(url_for("admin.hospedaje_index"))
