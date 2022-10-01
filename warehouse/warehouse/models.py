from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy ( )

class ProductCategory(database.Model):
    __tablename__ = "productcategory"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)

class OrderProduct(database.Model):
    __tablename__ = "orderproduct"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    itemId = database.Column(database.Integer, database.ForeignKey("orderitems.id"), nullable=False)

class Product ( database.Model ):
    __tablename__ = "products"

    id = database.Column ( database.Integer, primary_key = True )
    name = database.Column ( database.String ( 256 ), nullable = False)
    quantity = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orderItems = database.relationship("OrderItem", secondary=OrderProduct.__table__, back_populates="products")

    def __repr__(self):
        return self.name

class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return self.name

class OrderItem(database.Model):
    __tablename__ = "orderitems"

    id = database.Column(database.Integer, primary_key=True)
    orderId = database.Column ( database.Integer, database.ForeignKey ( "orders.id" ), nullable = False )
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    received = database.Column(database.Integer, nullable=False)
    requested = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)

    order = database.relationship("Order", back_populates="products")
    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orderItems")

class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(10), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)
    email = database.Column(database.String(256), nullable=False)

    products = database.relationship ( "OrderItem", back_populates = "order" );