from redis import Redis
from configuration import Configuration
from flask import Flask
from models import database, Product, Category, ProductCategory, OrderItem, Order
from sqlalchemy import and_
import json

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)

while True:
    try:
        data = None
        with Redis(host = Configuration.REDIS_URI) as redis:
            print("Waiting for product...", flush=True)
            data = redis.blpop(Configuration.REDIS_PRODUCTS_LIST)

        products = json.loads(data[1])
        with application.app_context() as context:
            for product in products:
                prod = Product.query.filter( Product.name == product["name"] ).first()
                if not prod:
                    prod = Product(name = product["name"], quantity = product["quantity"], price = product["price"])

                    database.session.add(prod)
                    database.session.commit()

                    categories = product["categories"].split("|")

                    for category in categories:
                        cat = Category.query.filter( Category.name == category).first()

                        if not cat:
                            cat = Category(name = category)

                            database.session.add(cat)
                            database.session.commit()

                        relation = ProductCategory(productId = prod.id, categoryId = cat.id)

                        database.session.add(relation)
                        database.session.commit()
                    print(f"Added new product {prod.name}", flush=True)
                else:
                    categoriesDelivered = product["categories"].split("|")
                    categoriesInDatabase = [p.name for p in prod.categories]
                    if categoriesDelivered == categoriesInDatabase:
                        newPrice = (float(prod.quantity * prod.price + int(product["quantity"]) * float(product["price"])))/(prod.quantity+int(product["quantity"]))
                        prod.quantity += product["quantity"]
                        prod.price = newPrice
                        database.session.commit()
                        print(f"Updated quantity and price for product {prod.name}")
                        potentialOrders = OrderItem.query.filter(
                            and_(OrderItem.productId == prod.id, OrderItem.received < OrderItem.requested)
                        ).all()
                        print(f"Potential orders: {potentialOrders}", flush=True)
                        for orderProduct in potentialOrders:
                            need = orderProduct.requested - orderProduct.received
                            gave = need if need < prod.quantity else prod.quantity
                            prod.quantity -= gave
                            orderProduct.received += gave
                            isCompleted = OrderItem.query.filter(
                                and_(OrderItem.orderId == orderProduct.orderId, OrderItem.received < OrderItem.requested)
                            ).first()
                            if not isCompleted:
                                order = Order.query.filter(Order.id == orderProduct.orderId).first()
                                order.status = "COMPLETE"
                            database.session.commit()
                            if prod.quantity == 0:
                                break
                    else:
                        print(f"Categories don't match up for delivered product {prod.name}")
    except Exception as e:
        print(e)