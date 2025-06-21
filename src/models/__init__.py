from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Importar modelos aquí para que estén disponibles al importar desde models
# Los modelos deben importarse después de inicializar db
from .product import Producto
from .price import Precio
from .stock import Stock
from .sucursal import Sucursal

# Hacer los modelos disponibles al importar desde models
__all__ = ['db', 'Producto', 'Precio', 'Stock', 'Sucursal']