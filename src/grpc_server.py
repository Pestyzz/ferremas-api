import grpc
from concurrent import futures
import time
import sys
import os

# Asegurarse de que el directorio src esté en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar los módulos generados por protoc
from protos import product_pb2, product_pb2_grpc

# Importar la aplicación Flask y los modelos
from app import app, db
from models import Producto

# Configurar el contexto de la aplicación
app.testing = True
app_context = app.app_context()
app_context.push()

# Asegurarse de que las tablas estén creadas
with app.app_context():
    db.create_all()

class ProductService(product_pb2_grpc.ProductServiceServicer):
    def AddProduct(self, request, context):
        with app.app_context():
            try:
                # Verificar si el producto ya existe
                if Producto.query.filter_by(codigo=request.code).first():
                    return product_pb2.Response(
                        success=False,
                        message="Ya existe un producto con este código"
                    )
                
                # Crear el producto
                producto = Producto(
                    codigo_producto=request.product_code,
                    marca=request.brand,
                    codigo=request.code,
                    nombre=request.name
                )
                
                db.session.add(producto)
                db.session.commit()
                
                return product_pb2.Response(
                    success=True,
                    message=f"Producto creado exitosamente con ID: {producto.id}"
                )
                
            except Exception as e:
                db.session.rollback()
                return product_pb2.Response(
                    success=False,
                    message=f"Error al crear el producto: {str(e)}"
                )

def serve():
    # Crear un servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Agregar el servicio al servidor
    product_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductService(), server
    )
    
    # Escuchar en el puerto 50051
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC iniciado en el puerto 50051...")
    
    try:
        while True:
            time.sleep(86400)  # Un día en segundos
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()