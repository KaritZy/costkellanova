from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Aquí se debe colocar tu URL de conexión a la base de datos Railway
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:KvhCpEixJkXBwitQjowBcCbbQjbJqKJS@junction.proxy.rlwy.net:52243/railway?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Función para eliminar cotizaciones y resetear los folios
def reset_folios():
    try:
        # Iniciar el contexto de la aplicación
        with app.app_context():
            # Eliminar todas las cotizaciones
            db.session.execute(text("DELETE FROM cotizacion"))
            db.session.execute(text("DELETE FROM papelera"))
            db.session.commit()

            # Reiniciar la secuencia de IDs
            db.session.execute(text("ALTER SEQUENCE cotizacion_id_seq RESTART WITH 1"))
            db.session.execute(text("ALTER SEQUENCE papelera_id_seq RESTART WITH 1"))
            db.session.commit()

            print("Datos eliminados y secuencias de folios reiniciadas.")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

if __name__ == '__main__':
    # Asegurarse de que estamos corriendo el contexto de la aplicación
    with app.app_context():
        reset_folios()
