from flask import Flask, request, Response
from configuration import Configuration
from models import database, Category, Product, Order, OrderItem, OrderProduct
from flask_jwt_extended import JWTManager, get_jwt_identity
from roleCheck import roleCheck
from sqlalchemy import func
import json

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager ( application )

@application.route("/search", methods=["GET"])
def search():
    val = roleCheck("buyer")
    if val is not None:
        return val
    categoryName = request.args.get("category", "")
    productName = request.args.get("name", "")

    categories = database.session.query(Category.name).join(Category.products)
    if categoryName!="":
        categories = categories.filter(Category.name.like(f"%{categoryName}%"))
    if productName!="":
        categories = categories.filter(Product.name.like(f"%{productName}%"))
    categories = categories.group_by(Category.id).all()
    categories = [cat[0] for cat in categories]

    products = database.session.query(Product.id, Product.name, Product.price, Product.quantity).join(Category.products)
    if categoryName != "":
        products = products.filter(Category.name.like(f"%{categoryName}%"))
    if productName != "":
        products = products.filter(Product.name.like(f"%{productName}%"))
    products = products.group_by(Product.id).all()

    return Response(json.dumps({
        "categories" : categories,
        "products" : [
            {
                "categories" : [c[0] for c in database.session.query(Category.name).join(Category.products).filter(Product.id==p[0]).group_by(Category.id).all()],
                "id" : p[0],
                "name" : p[1],
                "price" : p[2],
                "quantity" : p[3]
            } for p in products
        ]
    }), status=200)

@application.route("/order", methods=["POST"])
def order():
    val = roleCheck("buyer")
    if val is not None:
        return val
    requests = request.json.get("requests", None)

    if requests is None:
        return Response(json.dumps({"message" : "Field requests is missing."}), status=400)

    i = 0
    for req in requests:
        idP = req.get("id", None)
        if idP is None:
            return Response(json.dumps({"message" : f"Product id is missing for request number {i}."}), status=400)
        quantity = req.get("quantity", None)
        if quantity is None:
            return Response(json.dumps({"message" : f"Product quantity is missing for request number {i}."}), status=400)
        try:
            idP = int(idP)
            if idP<=0:
                raise Exception
        except Exception:
            return Response(json.dumps({"message": f"Invalid product id for request number {i}."}), status=400)
        try:
            quantity = int(quantity)
            if quantity<=0:
                raise Exception
        except Exception:
            return Response(json.dumps({"message": f"Invalid product quantity for request number {i}."}), status=400)
        product = Product.query.filter(Product.id == idP).first()
        if not product:
            return Response(json.dumps({"message": f"Invalid product for request number {i}."}), status=400)
        i += 1

    email = get_jwt_identity ( )
    order = Order(price = 0, status = "COMPLETE", email = email, timestamp=func.now())

    database.session.add(order)
    database.session.commit()

    fullPrice = 0

    for req in requests:
        product = Product.query.filter(Product.id==req["id"]).first()
        orderItem = OrderItem(orderId = order.id, productId = product.id, price = product.price, requested = int(req["quantity"]))
        if product.quantity >= int(req["quantity"]):
            product.quantity -= int(req["quantity"])
            orderItem.received = int(req["quantity"])
        else:
            orderItem.received = product.quantity
            product.quantity = 0
            order.status = "PENDING"
        fullPrice += (product.price * orderItem.requested)
        database.session.add(orderItem)
        database.session.commit()

        orderProduct = OrderProduct(productId=product.id, itemId=orderItem.id)
        database.session.add(orderProduct)
        database.session.commit()

    order.price = fullPrice
    database.session.commit()

    return Response(json.dumps({"id" : order.id}), status=200)

@application.route("/status", methods=["GET"])
def status():
    val = roleCheck("buyer")
    if val is not None:
        return val
    email = get_jwt_identity()
    orders = Order.query.filter(Order.email==email).all()

    return Response(
        json.dumps(
            {
                "orders" : [
                    {
                        "products" : [
                            {
                                "categories": [c[0] for c in database.session.query(Category.name).join(Category.products).filter(Product.id == product.productId).group_by(Category.id).all()],
                                "name": Product.query.filter(Product.id==product.productId).first().name,
                                "price": product.price,
                                "received" : product.received,
                                "requested" : product.requested
                            } for product in order.products
                        ],
                        "price" : order.price,
                        "status" : order.status,
                        "timestamp" : order.timestamp.isoformat()
                    } for order in orders
                ]
            }
        ), status=200
    )

if  __name__ == "__main__" :
    database.init_app ( application );
    application.run ( debug = True, host = "0.0.0.0", port = 5004 );