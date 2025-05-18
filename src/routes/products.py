from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db
from models.product import Producto
from models.price import Precio
from models.stock import Stock

products_bp = Blueprint("products", __name__)

#Ruta para añadir un producto
@products_bp.route("/products/add", methods=["POST"])
def add_product():
    try:
        data = request.get_json()

        #Validar que se hayan enviado todos los campos requeridos para añadir el producto
        campos_requeridos = ["Código del producto", "Marca", "Código", "Nombre", "Precio"]
        if not all(campo in data for campo in campos_requeridos):
            campos_faltantes = [campo for campo in campos_requeridos if campo not in data]
            return jsonify({
                "message": "Faltan campos requeridos",
                "campos_faltantes": campos_faltantes
            }), 400

        #Validar que el producto no exista
        producto_existente = db.session.query(Producto).filter_by(codigo_producto=data["Código del producto"]).first()
        if producto_existente:
            return jsonify({
                "message": "Ya existe un producto con este código",
                "error": "Código de producto duplicado"
            }), 409

        nuevo_producto = Producto(
            codigo_producto=data['Código del producto'],
            marca=data['Marca'],
            codigo=data['Código'],
            nombre=data['Nombre']
        )

        #Validar y agregar los precios
        for precio in data['Precio']:
            if "Fecha" not in precio or "Valor" not in precio:
                return jsonify({
                    "message": "Formato de precio incorrecto",
                    "error": "Cada precio debe tener Fecha y Valor"
                }), 400

            try:
                fecha = datetime.fromisoformat(precio["Fecha"])
                valor = float(precio["Valor"])

                nuevo_precio = Precio(
                    fecha=fecha,
                    valor=valor,
                    producto=nuevo_producto
                )
                db.session.add(nuevo_precio)
            except ValueError as e:
                return jsonify({
                    "message": "Error en los datos del precio",
                    "error": str(e)
                }), 400
        
        #Guardar el producto y sus precios
        db.session.add(nuevo_producto)
        db.session.commit()

        precios = [{"Fecha": p.fecha.isoformat(), "Valor": p.valor} for p in nuevo_producto.precios]
        return jsonify({
            "message": "Producto añadido exitósamente",
            "producto": {
                "Código del producto": nuevo_producto.codigo_producto,
                "Marca": nuevo_producto.marca,
                "Código": nuevo_producto.codigo,
                "Nombre": nuevo_producto.nombre,
                "Precio": precios
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e)
        }), 500

#Ruta para actualizar un producto
@products_bp.route("/products/update/<codigo>", methods=["PUT"])
def update_product(codigo):
    try:
        data = request.get_json()

        #Validar que se hayan enviado datos para actualizar el producto
        if not data:
            return jsonify({
                "message": "No se enviaron datos para actualizar el producto",
                "error": "Datos vacíos"
            }), 400
        
        #Buscar el producto en la base de datos
        producto = db.session.query(Producto).filter_by(codigo_producto=codigo).first()
        if not producto:
            return jsonify({
                "message": "Producto no encontrado",
                "error": "Código del producto no existe"
            }), 404
        
        #Actualizar los campos permitidos
        campos_permitidos = ["Marca", "Código", "Nombre"]
        for campo in campos_permitidos:
            if campo in data:
                setattr(producto, campo.lower(), data[campo])

        #Actualizar precios si se envían
        if "Precio" in data:
            #Agregar precios nuevos
            for precio in data["Precio"]:
                if "Fecha" not in precio or "Valor" not in precio:
                    return jsonify({
                        "message": "Formato de precio incorrecto",
                        "error": "Cada precio debe tener Fecha y valor"
                    }), 400
        
            try:
                fecha = datetime.fromisoformat(precio["Fecha"])
                valor = float(precio["Valor"])

                nuevo_precio = Precio(
                    fecha=datetime.fromisoformat(precio['Fecha']),
                    valor=precio['Valor'],
                    producto=producto
                )
                db.session.add(nuevo_precio)

            except ValueError as e:
                return jsonify({
                    "message": "Error en los datos del precio",
                    "error": str(e)
                }), 400

        #Guarda el producto actualizado
        db.session.commit()

        precios = [{"Fecha": p.fecha.isoformat(), "Valor": p.valor} for p in producto.precios]
        return jsonify({
            "message": "Producto actualizado exitósamente",
            "producto": {
                "Código del producto": producto.codigo_producto,
                "Marca": producto.marca,
                "Código": producto.codigo,
                "Nombre": producto.nombre,
                "Precio": precios
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e)
        }), 500

#Ruta para eliminar un producto
@products_bp.route("/products/delete/<codigo>", methods=["DELETE"])
def delete_product(codigo):
    try:
        #Buscar el producto
        producto = db.session.query(Producto).filter_by(codigo_producto=codigo).first()
        if not producto:
            return jsonify({
                "message": "Producto no encontrado",
                "codigo buscado": codigo
                }), 404

        #Aquí se eliminan todos los precios asociados al producto
        db.session.query(Precio).filter_by(producto_id=producto.id).delete()
        #Aquí se eliminan todos los stocks asociados al producto
        db.session.query(Stock).filter_by(producto_id=producto.id).delete()

        #Se hace la eliminación del producto y se guardan los cambios en la base de datos
        db.session.delete(producto)
        db.session.commit()

        return jsonify({"message": "Producto eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error al eliminar el producto",
            "error": str(e)
            }), 500

#Ruta para obtener todos los productos
@products_bp.route("/products/all", methods=["GET"])
def get_all_products():
    try:
        productos = db.session.query(Producto).all()
        result = []
        for producto in productos:
            precios = [{"Fecha": p.fecha.isoformat(), "Valor": p.valor} for p in producto.precios]
            result.append({
                "Código del producto": producto.codigo_producto,
                "Marca": producto.marca,
                "Código": producto.codigo,
                "Nombre": producto.nombre,
                "Precio": precios
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e) 
        }), 500

#Ruta para obtener un producto por su código
@products_bp.route("/products/product/<codigo>", methods=["GET"])
def get_product(codigo):
    try:
        producto = db.session.query(Producto).filter_by(codigo_producto=codigo).first()
        if not producto:
            return jsonify({"message": "Producto no encontrado"}), 404
        
        precios = [{"Fecha": p.fecha.isoformat(), "Valor": p.valor} for p in producto.precios]
        return jsonify({
            "Código del producto": producto.codigo_producto,
            "Marca": producto.marca,
            "Código": producto.codigo,
            "Nombre": producto.nombre,
            "Precio": precios
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e)
        }), 500