from flask import Flask, request, jsonify
from datetime import datetime
from models import db
from models.product import Producto
from models.price import Precio
from models.stock import Stock
from models.sucursal import Sucursal
from routes.products import products_bp

app = Flask(__name__)

#Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ferreteria.db"  # Usamos SQLite para simplicidad
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Inicializa la instancia de SQLAlchemy
db.init_app(app)

#Registra los Blueprints
app.register_blueprint(products_bp)

# Ruta para obtener todas las sucursales
@app.route('/sucursales', methods=['GET'])
def obtener_sucursales():
    sucursales = Sucursal.query.all()
    result = []
    for sucursal in sucursales:
        result.append({
            "id": sucursal.id,
            "Nombre": sucursal.nombre,
            "Dirección": sucursal.direccion
        })
    return jsonify(result), 200

# Ruta para crear stock en una sucursal
@app.route('/sucursales/<int:sucursal_id>/stock', methods=['POST'])
def crear_stock(sucursal_id):
    data = request.get_json()
    sucursal = Sucursal.query.get(sucursal_id)
    if not sucursal:
        return jsonify({"message": "Sucursal no encontrada"}), 404

    for item in data:
        producto = Producto.query.filter_by(codigo_producto=item['Codigo del producto']).first()
        if not producto:
            return jsonify({"message": f"Producto {item['Codigo del producto']} no encontrado"}), 404

        stock = Stock.query.filter_by(producto_id=producto.id, sucursal_id=sucursal_id).first()
        if stock:
            stock.cantidad += item['Cantidad']
        else:
            stock = Stock(producto_id=producto.id, sucursal_id=sucursal_id, cantidad=item['Cantidad'])
            db.session.add(stock)

    db.session.commit()
    return jsonify({"message": "Stock actualizado correctamente"}), 200

# Ruta para obtener el stock de una sucursal
@app.route('/sucursales/<int:sucursal_id>/stock', methods=['GET'])
def obtener_stock_sucursal(sucursal_id):
    sucursal = Sucursal.query.get(sucursal_id)
    if not sucursal:
        return jsonify({"message": "Sucursal no encontrada"}), 404
    
    stock_items = Stock.query.filter_by(sucursal_id=sucursal_id).all()
    result = []
    
    for stock in stock_items:
        producto = Producto.query.get(stock.producto_id)
        result.append({
            "Codigo del producto": producto.codigo_producto,
            "Nombre": producto.nombre,
            "Marca": producto.marca,
            "Cantidad": stock.cantidad
        })
    
    return jsonify(result), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
