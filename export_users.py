from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    
    with open("lista_de_usuarios.txt", "w", encoding="utf-8") as f:
        f.write(f"REPORTE DE USUARIOS REGISTRADOS\n")
        f.write(f"=================================\n")
        for user in users:
            estado = "CONFIRMADO" if user.confirmed else "PENDIENTE"
            f.write(f"ID: {user.id}\n")
            f.write(f"Usuario: {user.username}\n")
            f.write(f"Email: {user.email}\n")
            f.write(f"Estado: {estado}\n")
            f.write(f"---------------------------------\n")
            
    print(f"Se han exportado {len(users)} usuarios al archivo 'lista_de_usuarios.txt'.")