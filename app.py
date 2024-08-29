from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Reemplaza con tu clave secreta

# Simulación de base de datos para cotizaciones
cotizaciones = []

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
        for cotizacion in cotizaciones:
            fecha_cotizacion = datetime.strptime(cotizacion['fecha'], '%Y-%m-%d')
            diferencia_dias = (datetime.now() - fecha_cotizacion).days
            cotizacion['mostrar_recordatorio'] = diferencia_dias > 3 and not cotizacion['respondido']

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
    nueva_cotizacion = {
        'folio': len(cotizaciones) + 1,
        'fecha': fecha,
        'componente': componente,
        'cotizacion': cotizacion,
        'recordatorio': 'Pendiente',
        'respondido': False,
        'numero_serie': numero_serie,  # Añadir el número de serie
        'mostrar_recordatorio': False  # Inicialmente sin recordatorio
    }

    # Agregar la nueva cotización a la "base de datos"
    cotizaciones.append(nueva_cotizacion)
    flash('Cotización registrada exitosamente.')
    return redirect(url_for('index'))

@app.route('/buscar', methods=['POST'])
def buscar_cotizacion():
    criterio = request.form['criterio']
    valor = request.form['valor']
    resultados = []

    for cotizacion in cotizaciones:
        if criterio == 'folio' and str(cotizacion['folio']) == valor:
            resultados.append(cotizacion)
        elif criterio == 'fecha' and cotizacion['fecha'] == valor:
            resultados.append(cotizacion)

    return render_template('index.html', cotizaciones=resultados)

@app.route('/responder/<int:folio>', methods=['POST'])
def responder_cotizacion(folio):
    admin_name = request.form['admin_name']
    admin_password = request.form['admin_password']
    
    # Verificación del nombre de administrador y contraseña
    if admin_name == 'Ricardo' and admin_password == 'Acdcministrador':
        for cotizacion in cotizaciones:
            if cotizacion['folio'] == folio:
                cotizacion['respondido'] = True
                cotizacion['recordatorio'] = 'Respondido'  # Actualiza el recordatorio a "Respondido"
                flash(f'Cotización con folio {folio} marcada como respondida.')
                break
    else:
        flash('Nombre de administrador o contraseña incorrectos.')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
