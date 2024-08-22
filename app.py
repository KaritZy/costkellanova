from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Contraseña para acceder a la aplicación
PASSWORD = 'semsa'

# Simulación de base de datos
cotizaciones = []

# Función para verificar recordatorios
def verificar_recordatorios():
    hoy = datetime.now()
    for cotizacion in cotizaciones:
        fecha_registro = datetime.strptime(cotizacion['fecha'], '%Y-%m-%d')
        if hoy - fecha_registro > timedelta(days=7) and not cotizacion.get('respondido'):
            cotizacion['recordatorio'] = 'Pendiente de respuesta desde hace más de 7 días'

@app.route('/')
def index():
    verificar_recordatorios()
    return render_template('index.html', cotizaciones=cotizaciones)

@app.route('/login', methods=['POST'])
def login():
    password = request.form['password']
    if password == PASSWORD:
        session['logged_in'] = True
        flash('Inicio de sesión exitoso.')
        return redirect(url_for('index'))
    else:
        flash('Contraseña incorrecta, intente nuevamente.')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Sesión cerrada correctamente.')
    return redirect(url_for('index'))

@app.route('/agregar', methods=['POST'])
def agregar():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        folio = request.form['folio']
        fecha = request.form['fecha']
        componente = request.form['componente']
        cotizacion = request.form['cotizacion']
        
        nueva_cotizacion = {
            'folio': folio,
            'fecha': fecha,
            'componente': componente,
            'cotizacion': cotizacion,
            'recordatorio': '',
            'respondido': False
        }
        cotizaciones.append(nueva_cotizacion)
        flash('Cotización registrada exitosamente.')
        return redirect(url_for('index'))

@app.route('/buscar', methods=['POST'])
def buscar():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    criterio = request.form['criterio']
    valor = request.form['valor']
    resultados = [c for c in cotizaciones if c[criterio] == valor]
    return render_template('index.html', cotizaciones=resultados)

@app.route('/responder/<folio>', methods=['POST'])
def responder(folio):
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    for cotizacion in cotizaciones:
        if cotizacion['folio'] == folio:
            cotizacion['respondido'] = True
            cotizacion['recordatorio'] = ''
            flash(f'Cotización con folio {folio} marcada como respondida.')
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
