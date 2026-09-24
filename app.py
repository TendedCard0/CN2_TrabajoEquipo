import os
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

# Cargar las variables de entorno
load_dotenv()

# Crear instancia
app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Modelo Marca
class Marca(db.Model):
    __tablename__ = 'marcas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)


# Modelo Vehiculo
class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    id = db.Column(db.Integer, primary_key=True)
    marca_id = db.Column(db.Integer, db.ForeignKey('marcas.id'))
    modelo = db.Column(db.String(50))
    anio = db.Column(db.Integer)
    precio = db.Column(db.Float)  # En PostgreSQL 'double precision' equivale a Float
    imagen_url = db.Column(db.String(255))

    # Relación para acceder a la marca desde el vehículo
    marca = db.relationship('Marca', backref=db.backref('vehiculos', lazy=True))


# Ruta para ver todos los vehiculos
@app.route('/')
def index():
    vehiculos = Vehiculo.query.all()
    return render_template('index.html', vehiculos=vehiculos)


# Ruta para crear/agregar un nuevo vehiculo
@app.route('/crear', methods=['GET', 'POST'])
def crear_vehiculo():
    # Si el usuario envía el formulario
    if request.method == 'POST':
        marca_id = request.form.get('marca_id')
        modelo = request.form.get('modelo')
        anio = request.form.get('anio')
        precio = request.form.get('precio')
        imagen_url = request.form.get('imagen_url')

        nuevo_vehiculo = Vehiculo(
            marca_id=int(marca_id),
            modelo=modelo,
            anio=int(anio) if anio else None,
            precio=float(precio) if precio else None,
            imagen_url=imagen_url,
        )

        db.session.add(nuevo_vehiculo)
        db.session.commit()

        # Al terminar, redirige al inicio
        return redirect(url_for('index'))

    # Si es petición GET, mostramos el formulario con las marcas disponibles
    marcas = Marca.query.all()
    return render_template('crear_vehiculo.html', marcas=marcas)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_vehiculo(id):
    # Buscar el vehículo por su ID
    vehiculo = Vehiculo.query.get_or_404(id)
    
    try:
        # Eliminar el vehículo de la base de datos
        db.session.delete(vehiculo)
        db.session.commit()
    except Exception as e:
        # En caso de error, puedes imprimirlo para depurar
        print(f"Error al eliminar: {e}")
        db.session.rollback()
        
    # Redirigir de vuelta al index
    return redirect(url_for('index'))

@app.route('/vehiculos/<int:id>/editar', methods=['GET', 'POST'])
def editar_vehiculo(id):

    vehiculo = Vehiculo.query.get_or_404(id)
    marcas = Marca.query.order_by(Marca.nombre).all()

    if request.method == 'POST':

        vehiculo.marca_id = request.form['marca_id']
        vehiculo.modelo = request.form['modelo']
        vehiculo.anio = request.form['anio']
        vehiculo.precio = request.form['precio']
        vehiculo.imagen_url = request.form.get('imagen_url')

        db.session.commit()

        return redirect(url_for('index'))

    return render_template(
        'editar.html',
        vehiculo=vehiculo,
        marcas=marcas
    )

if __name__ == '__main__':
    app.run(debug=True)