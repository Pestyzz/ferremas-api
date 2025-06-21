from flask import Blueprint, request, jsonify, Response, stream_with_context
from models import db
from models.product import Producto
from models.stock import Stock
from models.sucursal import Sucursal
import json
import time
from datetime import datetime

branches_bp = Blueprint("branches", __name__)

#Ruta para obtener todas las sucursales registradas
@branches_bp.route("/branches/all", methods=["GET"])
def get_all_branches():
    try:
        sucursales = db.session.query(Sucursal).all()
        resultado = []
        for sucursal in sucursales:
            resultado.append({
                "id": sucursal.id,
                "Nombre": sucursal.nombre,
                "Dirección": sucursal.direccion
            })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e)
        }), 500

#Ruta para crear stock de un producto en una sucursal
@branches_bp.route("/branches/<int:sucursal_id>/stock/add", methods=["POST"])
def branch_add_stock(sucursal_id):
    try:
        data = request.get_json()

        #Se valida que se haya enviado al menos un producto
        if not data or not isinstance(data, list):
            return jsonify({
                "message": "Se debe enviar una lista de productos",
                "error": "Formato de datos incorrecto"
            }), 400

        #Se busca la sucursal en la base de datos
        sucursal = db.session.query(Sucursal).get(sucursal_id)
        if not sucursal:
            return jsonify({"message": "Sucursal no encontrada"}), 404

        #Se procesa cada producto
        for item in data:
            #Validación de campos requeridos
            if not all(key in item for key in ["Código del producto", "Cantidad"]):
                return jsonify({
                    "message": "Faltan campos requeridos",
                    "error": "Cada producto debe tener Código del producto y Cantidad"
                }), 400
            
            try:
                cantidad = int(item["Cantidad"])
                if cantidad <= 0:
                    return jsonify({
                        "message": "Cantidad inválida",
                        "error": "La cantidad debe ser un número entero"
                    }), 400
            except ValueError:
                return jsonify({
                    "message": "Valor inválido",
                    "error": "La cantidad debe ser un número"
                }), 400

            #Se busca el producto
            producto = db.session.query(Producto).filter_by(codigo_producto=item['Código del producto']).first()
            if not producto:
                return jsonify({
                    "message": f"Producto {item['Codigo del producto']} no encontrado",
                    "error": "Producto no existe"
                    }), 404

            #Actualizar o crear stock
            stock = db.session.query(Stock).filter_by(producto_id=producto.id, sucursal_id=sucursal_id).first()
            if stock:
                stock.cantidad += cantidad
            else:
                stock = Stock(
                producto_id=producto.id, 
                sucursal_id=sucursal_id, 
                cantidad=cantidad
                )
                db.session.add(stock)
                
        #Se guardan los cambios
        db.session.commit()

        #Obtener el stock actualizado
        stocks = db.session.query(Stock).filter_by(sucursal_id=sucursal_id).all()
        resultado = []
        for stock in stocks:
            producto = db.session.query(Producto).get(stock.producto_id)
            resultado.append({
                "Código del producto": producto.codigo_producto,
                "Nombre": producto.nombre,
                "Cantidad": stock.cantidad
            })

        return jsonify({
            "message": "Stock actualizado correctamente",
            "stock": resultado
            }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e)
        }), 500

#Ruta para obtener todo el stock de una sucursal
@branches_bp.route("/branches/<int:sucursal_id>/stock/all", methods=["GET"])
def branch_get_stock(sucursal_id):
    try:
        #Buscar la sucursal en la base de datos
        sucursal = db.session.query(Sucursal).get(sucursal_id)
        if not sucursal:
            return jsonify({
                "message": "Sucursal no encontrada",
                "error": f"Sucursal con ID {sucursal_id} no existe"
                }), 404
        
        #Obtener el stock de la sucursal
        stock_items = db.session.query(Stock).filter_by(sucursal_id=sucursal_id).all()
        if not stock_items:
            return jsonify({
                "message": "No hay stock registrado en esta sucursal",
                "sucursal": {
                    "id": sucursal.id,
                    "nombre": sucursal.nombre,
                    "direccion": sucursal.direccion
                }
            }), 200
        
        #Mostrar una respuesta con la información detallada    
        resultado = []
        for stock in stock_items:
            producto = db.session.query(Producto).get(stock.producto_id)
            precios = [{"Fecha": p.fecha.isoformat(), "Valor": p.valor} for p in producto.precios]

            resultado.append({
                "producto": {
                    "Código del producto": producto.codigo_producto,
                    "Nombre": producto.nombre,
                    "Marca": producto.marca,
                    "Precio": precios
                },
                "stock": {
                    "Cantidad": stock.cantidad
                }
            })
        
        return jsonify({
            "message": "Stock obtenido exitósamente",
            "sucursal": {
                "id": sucursal.id,
                "nombre": sucursal.nombre,
                "direccion": sucursal.direccion
            },
            "stock": resultado
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Error interno en el servidor",
            "error": str(e)
        }), 500

# Ruta para monitorear stock bajo mediante SSE
@branches_bp.route("/branches/stock-alerts", methods=["GET"])
def stock_alerts():
    umbral = request.args.get('umbral', default=5, type=int)
    
    def generate():
        # Mensaje inicial de conexión
        yield f"data: {json.dumps({'message': 'Conexión de monitoreo establecida', 'umbral': umbral})}\n\n"
        
        # Bucle principal para verificar stock periódicamente
        try:
            while True:
                # Consultar productos con stock bajo en todas las sucursales
                stocks_bajos = db.session.query(Stock, Producto, Sucursal).join(
                    Producto, Stock.producto_id == Producto.id
                ).join(
                    Sucursal, Stock.sucursal_id == Sucursal.id
                ).filter(Stock.cantidad < umbral).all()
                
                # Enviar información de diagnóstico
                yield f"data: {json.dumps({
                    'type': 'info', 
                    'message': f'Verificación completada', 
                    'productos_bajo_stock': len(stocks_bajos),
                    'timestamp': datetime.now().isoformat()
                })}\n\n"
                
                # Enviar alertas para cada producto con stock bajo
                if stocks_bajos:
                    for stock, producto, sucursal in stocks_bajos:
                        data = {
                            "message": "Stock Bajo",
                            "producto": producto.nombre,
                            "codigo": producto.codigo_producto,
                            "sucursal": sucursal.nombre,
                            "cantidad": stock.cantidad,
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                else:
                    # Notificar que no hay productos con stock bajo
                    yield f"data: {json.dumps({
                        'type': 'info',
                        'message': 'No hay productos con stock bajo',
                        'timestamp': datetime.now().isoformat()
                    })}\n\n"
                
                # Heartbeat para mantener la conexión viva
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                
                # Esperar antes de la siguiente verificación (reducido para pruebas)
                time.sleep(10)  # Verificar cada 10 segundos
                
        except Exception as e:
            # Enviar error si ocurre alguna excepción
            error_data = {
                "message": "Error en monitoreo",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    # Configurar los headers para SSE
    response = Response(stream_with_context(generate()), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # Para servidores Nginx
    return response