"""
Simple migration helper (non-destructive):
- Creates the `reservahuesped` table if not exists.
- Copies basic data from `huesped` into `reservahuesped`.

IMPORTANT: This script attempts a best-effort migration for convenience.
Review the resulting data and backup your DB before running in production.
"""
from run import create_app
from utils.extensions import db

def migrate():
    app = create_app()
    with app.app_context():
        # Ensure table exists
        db.create_all()

        # Best-effort copy from old Huesped table if it exists
        try:
            from models.huesped import Huesped
            from models.reservahuesped import ReservaHuesped
        except Exception as e:
            print('No se pudo importar modelos antiguos:', e)
            return

        existing = ReservaHuesped.query.first()
        if existing:
            print('Parece que ya hay datos en reservahuesped; abortando copia automática para evitar duplicados.')
            return

        count = 0
        for h in Huesped.query.all():
            r = ReservaHuesped(
                nombre=h.nombre,
                tipoDocumento=getattr(h, 'tipoDocumento', None),
                numeroDocumento=getattr(h, 'numeroDocumento', None),
                telefono=getattr(h, 'telefono', None),
                correo=getattr(h, 'correo', None),
                procedencia=getattr(h, 'procedencia', None),
                habitacion_id=getattr(h, 'habitacion_id', None),
                # precio/checkin/checkout/cantidad_personas cannot be reliably recovered here
            )
            db.session.add(r)
            count += 1

        db.session.commit()
        print(f'Migración completa: {count} filas copiadas desde huesped → reservahuesped')

if __name__ == '__main__':
    print('Ejecutando migración (asegúrate de tener backup).')
    migrate()
