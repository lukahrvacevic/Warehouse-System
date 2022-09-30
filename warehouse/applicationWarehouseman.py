from flask import Flask, request, Response
from configurationWarehouseman import Configuration
from flask_jwt_extended import JWTManager
from roleCheck import roleCheck
from redis import Redis
import json
import io
import csv

application = Flask ( __name__ )
application.config.from_object ( Configuration )

jwt = JWTManager ( application )

@application.route("/update", methods=["POST"])
def update():
    val = roleCheck("warehouseman")
    if val is not None:
        return val
    file = None
    try:
        file = request.files["file"]
    except Exception:
        return Response(json.dumps({"message" : "Field file is missing."}), status=400)
    content = file.stream.read ( ).decode ( "utf-8" )
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    products = []
    line = 0
    for row in reader:
        if len(row) != 4:
            return Response(json.dumps({"message" : f"Incorrect number of values on line {line}."}), status=400)
        categories = row[0]
        name = row[1]
        quantity = row[2]
        price = row[3]
        try:
            quantity = int(quantity)
            if quantity<=0:
                raise Exception
        except Exception:
            return Response(json.dumps({"message" : f"Incorrect quantity on line {line}."}), status=400)
        try:
            price = float(price)
            if price<=0:
                raise Exception
        except Exception:
            return Response(json.dumps({"message" : f"Incorrect price on line {line}."}), status=400)
        product = {
            "categories" : categories,
            "name" : name,
            "quantity" : quantity,
            "price" : price
        }
        products.append(product)
        line += 1

    print(products)

    with Redis(host=Configuration.REDIS_URI) as redis:
        redis.rpush(Configuration.REDIS_PRODUCTS_LIST, json.dumps(products))

    return Response("", status = 200)


if  __name__ == "__main__" :
    application.run ( debug = True, host = "0.0.0.0", port = 5003 );