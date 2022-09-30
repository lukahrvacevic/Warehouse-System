from flask import Flask, request, Response
from configuration import Configuration
from models import database, Product, OrderItem, Category
from flask_jwt_extended import JWTManager
from roleCheck import roleCheck
from sqlalchemy import and_, func, desc
import json
import re

application = Flask ( __name__ )
application.config.from_object ( Configuration )

jwt = JWTManager ( application )

@application.route("/productStatistics", methods=["GET"])
def productStatistics():
    val = roleCheck("admin")
    if val is not None:
        return val

    products = database.session.query(
        Product.name,
        func.sum(OrderItem.requested),
        func.sum(OrderItem.requested) - func.sum(OrderItem.received)
    ).join(Product.orderItems).group_by(Product.id).all()


    return Response(json.dumps({
        "statistics" : [
            {
                "name" : product[0],
                "sold" : int(product[1]),
                "waiting" : int(product[2])
            } for product in products
        ]
    }), status=200)

@application.route("/categoryStatistics", methods=["GET"])
def categoryStatistics():
    val = roleCheck("admin")
    if val is not None:
        return val

    categories = database.session.query(
        Category.name,
        func.sum(OrderItem.requested)
    ).join(Category.products).outerjoin(Product.orderItems).group_by(Category.id).order_by(desc(func.sum(OrderItem.requested)), Category.name).all()

    return Response(json.dumps({
        "statistics" : [
            category[0] for category in categories
        ]
    }), status=200)

if  __name__ == "__main__" :
    database.init_app ( application );
    application.run ( debug = True, host = "0.0.0.0", port = 5005 );