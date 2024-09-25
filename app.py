from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configurar la URL de la base de datos con Railway con SSL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:XGkABujfcUSOfTvxliOmOZcoQKpsjfft@autorack.proxy.rlwy.net:44589/railway?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(hours=1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# Modelos de la Base de Datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    componente = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), nullable=True)  # Permite nulos
    cotizacion = db.Column(db.String(100), nullable=False)
    recordatorio = db.Column(db.String(20), default='Pendiente')
    respondido = db.Column(db.Boolean, default=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    mostrar_recordatorio = db.Column(db.Boolean, default=False)
    mensaje_david = db.Column(db.String(255), nullable=True)

class Papelera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    componente = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    cotizacion = db.Column(db.String(100), nullable=False)
    recordatorio = db.Column(db.String(20), default='Pendiente')
    respondido = db.Column(db.Boolean, default=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    mostrar_recordatorio = db.Column(db.Boolean, default=False)

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    componentes = db.relationship('Componente', backref='equipo', lazy=True)

class Componente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(100), nullable=False)
    num_parte = db.Column(db.String(100), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipo.id'), nullable=False)

# Crear todas las tablas en la base de datos
with app.app_context():
    db.create_all()

# Ruta Principal - Página principal con validación de contraseña
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'semsa':
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            flash('Contraseña incorrecta.')
    return render_template('home.html')

# Página principal después de autenticación con contraseña
@app.route('/index')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    cotizaciones = Cotizacion.query.all()
    return render_template('index.html', cotizaciones=cotizaciones)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    flash('Sesión cerrada.')
    return redirect(url_for('home'))

# Resto de rutas para gestión de cotizaciones, componentes, equipos, y papelera
@app.route('/agregar', methods=['POST'])
def agregar_cotizacion():
    fecha = request.form['fecha']
    componente = request.form['componente']
    codigo = request.form['codigo']
    cotizacion = request.form['cotizacion']
    numero_serie = request.form['numero_serie']

    nueva_cotizacion = Cotizacion(
        fecha=fecha,
        componente=componente,
        codigo=codigo,
        cotizacion=cotizacion,
        numero_serie=numero_serie
    )

    db.session.add(nueva_cotizacion)
    db.session.commit()
    flash('Cotización registrada exitosamente.')
    return redirect(url_for('index'))

@app.route('/buscar', methods=['POST'])
def buscar_cotizacion():
    criterio = request.form['criterio']
    valor = request.form['valor']
    resultados = []

    if criterio == 'folio' and valor.isdigit():
        resultados = Cotizacion.query.filter_by(id=int(valor)).all()
    elif criterio == 'fecha':
        resultados = Cotizacion.query.filter_by(fecha=valor).all()

    if resultados:
        flash(f'Se encontraron {len(resultados)} resultados.')
    else:
        flash('No se encontraron cotizaciones con los criterios especificados.')

    return render_template('index.html', cotizaciones=resultados)

@app.route('/david_dashboard', methods=['GET', 'POST'])
def david_dashboard():
    if 'david_authenticated' not in session:
        return redirect(url_for('david_login'))

    if request.method == 'POST':
        folio = request.form['folio']
        mensaje = request.form['mensaje']
        cotizacion = Cotizacion.query.get(folio)
        if cotizacion:
            cotizacion.mensaje_david = mensaje
            db.session.commit()
            flash('Mensaje enviado correctamente.')
        return redirect(url_for('david_dashboard'))

    cotizaciones = Cotizacion.query.all()
    return render_template('david_dashboard.html', cotizaciones=cotizaciones)

@app.route('/david_login', methods=['GET', 'POST'])
def david_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'David' and password == 'Peruyero':
            session['david_authenticated'] = True
            return redirect(url_for('david_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.')
    return render_template('david_login.html')

@app.route('/enviar_mensaje/<int:folio>', methods=['POST'])
def enviar_mensaje_david(folio):
    mensaje = request.form.get('mensaje')
    cotizacion = Cotizacion.query.get(folio)
    if cotizacion:
        cotizacion.mensaje_david = mensaje
        db.session.commit()
        flash('Mensaje enviado correctamente.')
    else:
        flash('Cotización no encontrada.')
    return redirect(url_for('david_dashboard'))

@app.route('/responder/<int:folio>', methods=['POST'])
def responder_cotizacion(folio):
    admin_name = request.form['admin_name']
    admin_password = request.form['admin_password']

    if admin_name == 'Ricardo' and admin_password == 'Acdcministrador':
        cotizacion = Cotizacion.query.get(folio)
        if cotizacion:
            cotizacion.respondido = True
            db.session.commit()
            flash(f'Cotización con folio {folio} marcada como respondida.')
        else:
            flash('Cotización no encontrada.')
    else:
        flash('Nombre de administrador o contraseña incorrectos.')

    return redirect(url_for('index'))

@app.route('/eliminar/<int:folio>', methods=['POST'])
def eliminar_cotizacion(folio):
    admin_name = request.form['admin_name']
    admin_password = request.form['admin_password']

    if admin_name == 'Ricardo' and admin_password == 'Acdcministrador':
        cotizacion = Cotizacion.query.get(folio)
        if cotizacion:
            papelera = Papelera(
                fecha=cotizacion.fecha,
                componente=cotizacion.componente,
                codigo=cotizacion.codigo,
                cotizacion=cotizacion.cotizacion,
                recordatorio=cotizacion.recordatorio,
                respondido=cotizacion.respondido,
                numero_serie=cotizacion.numero_serie,
                mostrar_recordatorio=cotizacion.mostrar_recordatorio
            )
            db.session.add(papelera)

            db.session.delete(cotizacion)
            db.session.commit()
            flash(f'Cotización con folio {folio} ha sido eliminada y movida a la papelera.')
        else:
            flash('Cotización no encontrada.')
    else:
        flash('Nombre de administrador o contraseña incorrectos.')

    return redirect(url_for('index'))

@app.route('/mostrar_equipos')
def mostrar_equipos():
    equipos = Equipo.query.all()
    return render_template('equipos.html', equipos=equipos)

@app.route('/agregar_equipo', methods=['POST'])
def agregar_equipo():
    nombre = request.form['nombre']
    nuevo_equipo = Equipo(nombre=nombre)
    db.session.add(nuevo_equipo)
    db.session.commit()
    flash('Equipo agregado exitosamente.')
    return redirect(url_for('mostrar_equipos'))

@app.route('/mostrar_componentes/<int:equipo_id>')
def mostrar_componentes(equipo_id):
    componentes = Componente.query.filter_by(equipo_id=equipo_id).all()
    return render_template('componentes.html', componentes=componentes)

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

@app.route('/componentes')
def componentes():
    return render_template('componentes.html')

@app.route('/papelera', methods=['GET', 'POST'])
def ver_papelera():
    admin_name = request.form.get('admin_name')
    admin_password = request.form.get('admin_password')

    if admin_name == 'Ricardo' and admin_password == 'PaolA2001@$':
        cotizaciones_eliminadas = Papelera.query.all()
        return render_template('papelera.html', cotizaciones=cotizaciones_eliminadas)
    else:
        flash('Nombre de administrador o contraseña incorrectos.')
        return redirect(url_for('index'))

@app.route('/restaurar_cotizacion/<int:id>', methods=['POST'])
def restaurar_cotizacion(id):
    cotizacion = Papelera.query.get(id)
    if cotizacion:
        nueva_cotizacion = Cotizacion(
            fecha=cotizacion.fecha,
            componente=cotizacion.componente,
            codigo=cotizacion.codigo,
            cotizacion=cotizacion.cotizacion,
            recordatorio=cotizacion.recordatorio,
            respondido=cotizacion.respondido,
            numero_serie=cotizacion.numero_serie,
            mostrar_recordatorio=cotizacion.mostrar_recordatorio
        )
        db.session.add(nueva_cotizacion)
        db.session.delete(cotizacion)
        db.session.commit()
        flash(f'Cotización con folio {id} ha sido restaurada.')
    else:
        flash('Cotización no encontrada en la papelera.')
    return redirect(url_for('ver_papelera'))

@app.route('/eliminar_definitivo/<int:id>', methods=['POST'])
def eliminar_definitivo(id):
    cotizacion = Papelera.query.get(id)
    if cotizacion:
        db.session.delete(cotizacion)
        db.session.commit()
        flash(f'Cotización con folio {id} ha sido eliminada definitivamente.')
    else:
        flash('Cotización no encontrada en la papelera.')
    return redirect(url_for('ver_papelera'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)