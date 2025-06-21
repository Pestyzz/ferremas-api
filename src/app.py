from flask import Flask
from flask_cors import CORS
from models import db
from routes.products import products_bp
from routes.branches import branches_bp

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
import os

# Obtener la ruta absoluta al directorio instance en la raíz del proyecto
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
instance_dir = os.path.join(project_dir, 'instance')
os.makedirs(instance_dir, exist_ok=True)  # Asegurar que el directorio exista
db_path = os.path.join(instance_dir, 'ferreteria.db')

# Configurar la URI de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar la base de datos
db.init_app(app)

# Registrar blueprints
app.register_blueprint(products_bp)
app.register_blueprint(branches_bp)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)