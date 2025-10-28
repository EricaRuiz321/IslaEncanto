from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.objetoinventario import ObjetoInventario
from models.inventariodiario import InventarioDiario
from models.inventarioresumen import InventarioResumen
from models.nuevahabitacion import NuevaHabitacion
from utils.extensions import db
from flask import session
from datetime import date, datetime

inventario_bp = Blueprint("inventario", __name__, url_prefix="/admin")

# ==========================
# 📋 GESTIÓN DE INVENTARIO
# ==========================

@inventario_bp.route("/inventario")
def inventario_index():
    """Página principal del inventario"""
    habitaciones = NuevaHabitacion.query.all()
    
    # Verificar que todas las habitaciones tengan precio
    for habitacion in habitaciones:
        if habitacion.precio is None:
            habitacion.precio = 0
            db.session.add(habitacion)
    db.session.commit()
    
    objetos_disponibles = ObjetoInventario.query.filter_by(activo=True).all()
    fecha_hoy = date.today()
    
    # Calcular estado de inventario para cada habitación
    for habitacion in habitaciones:
        habitacion.inventario_realizado = False  # Flag para saber si ya se hizo inventario
        
        if habitacion.objetos_incluidos:
            nombres_objetos = [obj.strip() for obj in habitacion.objetos_incluidos.split(',') if obj.strip()]
            
            objetos_completos = 0
            objetos_faltantes = 0
            objetos_pendientes = 0
            objetos_con_inventario = 0  # Objetos que ya tienen inventario del día
            total_objetos = len(nombres_objetos)
            
            for nombre in nombres_objetos:
                objeto = ObjetoInventario.query.filter_by(nombre=nombre, activo=True).first()
                if objeto:
                    inventario = InventarioDiario.query.filter_by(
                        habitacion_id=habitacion.id,
                        objeto_id=objeto.id,
                        fecha_inventario=fecha_hoy
                    ).first()
                    
                    if inventario and inventario.cantidad_encontrada is not None:
                        objetos_con_inventario += 1
                        if inventario.cantidad_encontrada >= inventario.cantidad_esperada:
                            objetos_completos += 1
                        else:
                            objetos_faltantes += 1
                    else:
                        objetos_pendientes += 1
            
            # Si al menos un objeto tiene inventario del día, considerar que se realizó inventario
            if objetos_con_inventario > 0:
                habitacion.inventario_realizado = True
                
                # Determinar estado general de la habitación
                if objetos_faltantes > 0:
                    habitacion.estado_inventario = 'faltante'
                elif objetos_pendientes > 0:
                    habitacion.estado_inventario = 'parcial'  # Nuevo estado para inventario parcial
                else:
                    habitacion.estado_inventario = 'completo'
            else:
                # No se ha realizado inventario
                habitacion.inventario_realizado = False
                habitacion.estado_inventario = 'sin_inventario'
        else:
            habitacion.estado_inventario = 'sin_objetos'
            habitacion.inventario_realizado = True  # No necesita inventario
    
    # Calcular estadísticas generales basadas en habitaciones
    habitaciones_pendientes = 0
    habitaciones_completas = 0
    habitaciones_faltantes = 0
    habitaciones_con_objetos = 0
    
    for habitacion in habitaciones:
        if habitacion.objetos_incluidos:  # Solo contar habitaciones que tienen objetos
            habitaciones_con_objetos += 1
            if not habitacion.inventario_realizado:
                habitaciones_pendientes += 1
            elif habitacion.estado_inventario == 'completo':
                habitaciones_completas += 1
            elif habitacion.estado_inventario in ['faltante', 'parcial']:
                habitaciones_faltantes += 1
    
    # Calcular porcentaje de progreso basado en habitaciones completas
    if habitaciones_con_objetos > 0:
        porcentaje_progreso = (habitaciones_completas / habitaciones_con_objetos) * 100
    else:
        porcentaje_progreso = 100  # Si no hay habitaciones con objetos, 100%
    
    # Crear estadísticas de resumen personalizadas
    estadisticas_inventario = {
        'habitaciones_pendientes': habitaciones_pendientes,
        'habitaciones_completas': habitaciones_completas, 
        'habitaciones_faltantes': habitaciones_faltantes,
        'total_habitaciones_con_objetos': habitaciones_con_objetos,
        'porcentaje_progreso': round(porcentaje_progreso, 1)
    }
    
    # Obtener resumen del día actual
    resumen_hoy = InventarioResumen.query.filter_by(fecha_inventario=fecha_hoy).first()
    if not resumen_hoy:
        resumen_hoy = InventarioResumen(fecha_inventario=fecha_hoy)
        db.session.add(resumen_hoy)
        db.session.commit()
        # Inicializar estadísticas
        resumen_hoy.actualizar_estadisticas()
        db.session.commit()
    
    return render_template("dashboard/inventario_admin.html", 
                         habitaciones=habitaciones, 
                         objetos_disponibles=objetos_disponibles,
                         resumen_hoy=resumen_hoy,
                         estadisticas_inventario=estadisticas_inventario,
                         fecha_hoy=fecha_hoy)

@inventario_bp.route("/inventario/habitacion/<int:habitacion_id>")
def inventario_habitacion(habitacion_id):
    """Ver inventario específico de una habitación"""
    habitacion = NuevaHabitacion.query.get_or_404(habitacion_id)
    
    # Verificar que la habitación tenga precio
    if habitacion.precio is None:
        habitacion.precio = 0
        db.session.add(habitacion)
        db.session.commit()
    
    fecha_hoy = date.today()
    
    # Obtener objetos de la habitación
    objetos_habitacion = []
    if habitacion.objetos_incluidos:
        nombres_objetos = [obj.strip() for obj in habitacion.objetos_incluidos.split(',') if obj.strip()]
        
        for nombre in nombres_objetos:
            # Buscar o crear el objeto en la tabla de objetos
            objeto = ObjetoInventario.query.filter_by(nombre=nombre, activo=True).first()
            if not objeto:
                objeto = ObjetoInventario(nombre=nombre, categoria="amenidades")
                db.session.add(objeto)
                db.session.commit()
            
            # Buscar inventario del día
            inventario = InventarioDiario.query.filter_by(
                habitacion_id=habitacion_id,
                objeto_id=objeto.id,
                fecha_inventario=fecha_hoy
            ).first()
            
            if not inventario:
                inventario = InventarioDiario(
                    habitacion_id=habitacion_id,
                    objeto_id=objeto.id,
                    fecha_inventario=fecha_hoy,
                    cantidad_esperada=1
                )
                db.session.add(inventario)
                db.session.commit()
            
            objetos_habitacion.append({
                'objeto': objeto,
                'inventario': inventario
            })
    
    return render_template("dashboard/inventario_habitacion.html", 
                         habitacion=habitacion, 
                         objetos_habitacion=objetos_habitacion,
                         fecha_hoy=fecha_hoy,
                         modo_edicion=True)

@inventario_bp.route("/inventario/ver/<int:habitacion_id>")
def ver_inventario_habitacion(habitacion_id):
    """Ver inventario de una habitación (solo lectura)"""
    habitacion = NuevaHabitacion.query.get_or_404(habitacion_id)
    
    # Verificar que la habitación tenga precio
    if habitacion.precio is None:
        habitacion.precio = 0
        db.session.add(habitacion)
        db.session.commit()
    
    fecha_hoy = date.today()
    
    # Obtener objetos de la habitación
    objetos_habitacion = []
    if habitacion.objetos_incluidos:
        nombres_objetos = [obj.strip() for obj in habitacion.objetos_incluidos.split(',') if obj.strip()]
        
        for nombre in nombres_objetos:
            # Buscar el objeto en la tabla de objetos
            objeto = ObjetoInventario.query.filter_by(nombre=nombre, activo=True).first()
            if objeto:
                # Buscar inventario del día
                inventario = InventarioDiario.query.filter_by(
                    habitacion_id=habitacion_id,
                    objeto_id=objeto.id,
                    fecha_inventario=fecha_hoy
                ).first()
                
                if inventario:
                    objetos_habitacion.append({
                        'objeto': objeto,
                        'inventario': inventario
                    })
    
    return render_template("dashboard/inventario_habitacion.html", 
                         habitacion=habitacion, 
                         objetos_habitacion=objetos_habitacion,
                         fecha_hoy=fecha_hoy,
                         modo_edicion=False)

# ==========================
# 📝 GESTIÓN DE OBJETOS
# ==========================

@inventario_bp.route("/inventario/objetos")
def gestionar_objetos():
    """Redireccionar a la página principal de inventario"""
    return redirect(url_for("inventario.inventario_index"))

@inventario_bp.route("/inventario/objetos/nuevo", methods=["POST"])
def crear_objeto():
    """Crear nuevo objeto de inventario"""
    try:
        nombre = request.form["nombre"].strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria = request.form.get("categoria", "amenidades").strip()
        
        # Verificar que no existe
        existe = ObjetoInventario.query.filter_by(nombre=nombre).first()
        if existe:
            if existe.activo:
                flash(f"❌ El objeto '{nombre}' ya existe", "warning")
            else:
                # Reactivar si estaba inactivo
                existe.activo = True
                db.session.commit()
                flash(f"✅ Objeto '{nombre}' reactivado", "success")
        else:
            # Crear nuevo
            objeto = ObjetoInventario(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria
            )
            db.session.add(objeto)
            db.session.commit()
            flash(f"✅ Objeto '{nombre}' creado correctamente", "success")
            
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al crear objeto: {e}", "danger")
    
    return redirect(url_for("inventario.inventario_index"))

@inventario_bp.route("/inventario/objetos/editar/<int:objeto_id>", methods=["POST"])
def editar_objeto(objeto_id):
    """Editar objeto existente"""
    objeto = ObjetoInventario.query.get_or_404(objeto_id)
    
    try:
        objeto.nombre = request.form["nombre"].strip()
        objeto.descripcion = request.form.get("descripcion", "").strip()
        objeto.categoria = request.form.get("categoria", "amenidades").strip()
        
        db.session.commit()
        flash(f"✅ Objeto '{objeto.nombre}' actualizado", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al actualizar objeto: {e}", "danger")
    
    return redirect(url_for("inventario.inventario_index"))

@inventario_bp.route("/inventario/objetos/eliminar/<int:objeto_id>", methods=["POST"])
def eliminar_objeto(objeto_id):
    """Desactivar objeto (eliminación lógica)"""
    objeto = ObjetoInventario.query.get_or_404(objeto_id)
    
    try:
        objeto.activo = False
        db.session.commit()
        flash(f"🗑️ Objeto '{objeto.nombre}' desactivado", "warning")
        
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al desactivar objeto: {e}", "danger")
    
    return redirect(url_for("inventario.inventario_index"))

# ==========================
# 📊 ACTUALIZACIÓN DE INVENTARIO
# ==========================

@inventario_bp.route("/inventario/actualizar", methods=["POST"])
def actualizar_inventario():
    """Actualizar inventario de una habitación"""
    try:
        habitacion_id = request.form["habitacion_id"]
        fecha_inventario = request.form.get("fecha_inventario", date.today())
        usuario = session.get('user', {}).get('nombre', 'Administrador')
        
        # Procesar cada objeto
        for key, value in request.form.items():
            if key.startswith("cantidad_"):
                objeto_id = key.replace("cantidad_", "")
                cantidad_encontrada = int(value) if value.isdigit() else 0
                observaciones = request.form.get(f"observaciones_{objeto_id}", "")
                
                # Buscar inventario existente
                inventario = InventarioDiario.query.filter_by(
                    habitacion_id=habitacion_id,
                    objeto_id=objeto_id,
                    fecha_inventario=fecha_inventario
                ).first()
                
                if inventario:
                    inventario.cantidad_encontrada = cantidad_encontrada
                    inventario.observaciones = observaciones
                    inventario.usuario_inventario = usuario
                    inventario.estado = inventario.estado_calculado
                
        db.session.commit()
        
        # Actualizar resumen del día
        resumen = InventarioResumen.query.filter_by(fecha_inventario=fecha_inventario).first()
        if resumen:
            resumen.actualizar_estadisticas()
            db.session.commit()
        
        flash("✅ Inventario actualizado correctamente", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al actualizar inventario: {e}", "danger")
    
    return redirect(url_for("inventario.inventario_index"))

# ==========================
# 📈 API ENDPOINTS
# ==========================

@inventario_bp.route("/api/objetos-disponibles")
def api_objetos_disponibles():
    """API para obtener objetos disponibles"""
    objetos = ObjetoInventario.query.filter_by(activo=True).order_by(ObjetoInventario.nombre).all()
    return jsonify([{
        'id': obj.id,
        'nombre': obj.nombre,
        'categoria': obj.categoria
    } for obj in objetos])

@inventario_bp.route("/api/inventario/resumen/<fecha>")
def api_resumen_inventario(fecha):
    """API para obtener resumen de inventario por fecha"""
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        resumen = InventarioResumen.query.filter_by(fecha_inventario=fecha_obj).first()
        
        if resumen:
            return jsonify({
                'fecha': fecha,
                'total_habitaciones': resumen.total_habitaciones,
                'objetos_completos': resumen.objetos_completos,
                'objetos_faltantes': resumen.objetos_faltantes,
                'objetos_pendientes': resumen.objetos_pendientes,
                'porcentaje_completado': resumen.porcentaje_completado
            })
        else:
            return jsonify({'error': 'No hay datos para esta fecha'})
            
    except Exception as e:
        return jsonify({'error': str(e)})
