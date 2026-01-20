from app import create_app, db

app = create_app()

with app.app_context():
    # 1. Borrar todas las tablas existentes
    db.drop_all()
    print("--- Base de datos eliminada ---")
    
    # 2. Crear tablas nuevas limpias
    db.create_all()
    print("--- Base de datos regenerada (Usuarios eliminados) ---")
    print("--- Listo para pruebas ---")