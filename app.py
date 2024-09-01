from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Asegúrate de que está importado
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Reemplaza con tu clave secreta

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cotizaciones.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Asegúrate de que esto esté presente

# Modelo de Cotización
class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    componente = db.Column(db.String(100), nullable=False)
    cotizacion = db.Column(db.String(100), nullable=False)
    recordatorio = db.Column(db.String(20), default='Pendiente')
    respondido = db.Column(db.Boolean, default=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    mostrar_recordatorio = db.Column(db.Boolean, default=False)

# Modelo de Equipo
class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    componentes = db.relationship('Componente', backref='equipo', lazy=True)

# Modelo de Componente
class Componente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(100), nullable=False)
    num_parte = db.Column(db.String(100), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipo.id'), nullable=False)

# Crear la base de datos (solo la primera vez)
with app.app_context():
    db.create_all()

@app.route('/componentes')
def componentes():
    return render_template('componentes.html')

@app.route('/')
def index():
    # Verifica si el usuario está logueado
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        # Calcular la diferencia de días para cada cotización
        cotizaciones = Cotizacion.query.all()
        for cotizacion in cotizaciones:
            fecha_cotizacion = datetime.strptime(cotizacion.fecha, '%Y-%m-%d')
            diferencia_dias = (datetime.now() - fecha_cotizacion).days
            cotizacion.mostrar_recordatorio = diferencia_dias > 3 and not cotizacion.respondido

        return render_template('index.html', cotizaciones=cotizaciones)

@app.route('/login', methods=['POST'])
def login():
    # Validación de contraseña simple
    if request.form['password'] == 'semsa':  # Reemplaza con una lógica más segura para producción
        session['logged_in'] = True
        flash('Inicio de sesión exitoso.')
    else:
        flash('Contraseña incorrecta.')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('Sesión cerrada.')
    return redirect(url_for('index'))

@app.route('/agregar', methods=['POST'])
def agregar_cotizacion():
    fecha = request.form['fecha']
    componente = request.form['componente']
    cotizacion = request.form['cotizacion']
    numero_serie = request.form['numero_serie']  # Capturar el nuevo campo "Número de Serie"

    # Crear un nuevo registro de cotización
    nueva_cotizacion = Cotizacion(
        fecha=fecha,
        componente=componente,
        cotizacion=cotizacion,
        numero_serie=numero_serie
    )

    # Agregar la nueva cotización a la base de datos
    db.session.add(nueva_cotizacion)
    db.session.commit()
    flash('Cotización registrada exitosamente.')
    return redirect(url_for('index'))

@app.route('/buscar', methods=['POST'])
def buscar_cotizacion():
    criterio = request.form['criterio']
    valor = request.form['valor']
    resultados = []

    if criterio == 'folio':
        resultados = Cotizacion.query.filter_by(id=int(valor)).all()
    elif criterio == 'fecha':
        resultados = Cotizacion.query.filter_by(fecha=valor).all()

    return render_template('index.html', cotizaciones=resultados)

@app.route('/responder/<int:folio>', methods=['POST'])
def responder_cotizacion(folio):
    admin_name = request.form['admin_name']
    admin_password = request.form['admin_password']

    # Verificación del nombre de administrador y contraseña
    if admin_name == 'Ricardo' and admin_password == 'Acdcministrador':
        cotizacion = Cotizacion.query.get(folio)  # Usa query.get() para obtener por ID
        if cotizacion:
            cotizacion.respondido = True
            db.session.commit()  # Asegúrate de hacer commit para guardar los cambios
            flash(f'Cotización con folio {folio} marcada como respondida.')
        else:
            flash('Cotización no encontrada.')
    else:
        flash('Nombre de administrador o contraseña incorrectos.')

    return redirect(url_for('index'))


@app.route('/agregar_equipo', methods=['POST'])
def agregar_equipo():
    nombre = request.form['nombre']
    nuevo_equipo = Equipo(nombre=nombre)
    db.session.add(nuevo_equipo)
    db.session.commit()
    flash('Equipo agregado exitosamente.')
    return redirect(url_for('mostrar_equipos'))

@app.route('/agregar_componente', methods=['POST'])
def agregar_componente():
    descripcion = request.form['descripcion']
    codigo = request.form['codigo']
    num_parte = request.form['num_parte']
    equipo_id = request.form['equipo_id']
    nuevo_componente = Componente(
        descripcion=descripcion,
        codigo=codigo,
        num_parte=num_parte,
        equipo_id=equipo_id
    )
    db.session.add(nuevo_componente)
    db.session.commit()
    flash('Componente agregado exitosamente.')
    return redirect(url_for('mostrar_componentes', equipo_id=equipo_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)