from . import db

class Stock(db.Model):
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    
    # Claves foráneas
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursales.id'), nullable=False)
    
    def __repr__(self):
        return f'<Stock {self.cantidad} unidades (Producto: {self.producto_id}, Sucursal: {self.sucursal_id})>'