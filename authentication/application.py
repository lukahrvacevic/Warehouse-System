from flask import Flask, request, Response
from configuration import Configuration
from models import database, User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
import json
import re

application = Flask ( __name__ )
application.config.from_object ( Configuration )

@application.route ( "/register", methods = ["POST"] )
def register():
    email = request.json.get ( "email", "" )
    password = request.json.get ( "password", "" )
    forename = request.json.get ( "forename", "" )
    surname = request.json.get ( "surname", "" )
    isCustomer = request.json.get ( "isCustomer", "" )

    if len(forename) == 0:
        return Response(json.dumps({"message": "Field forename is missing."}), 400)
    if len(surname) == 0:
        return Response(json.dumps({"message": "Field surname is missing."}), 400)
    if len(email) == 0:
        return Response(json.dumps({"message": "Field email is missing."}), 400)
    if len(password) == 0:
        return Response(json.dumps({"message": "Field password is missing."}), 400)
    if isCustomer == "":
        return Response(json.dumps({"message": "Field isCustomer is missing."}), 400)

    if not re.match(r"[^@]+@[^@]+\.[^@]{2,}", email):
        return Response(json.dumps({"message": "Invalid email."}), 400)

    if not bool(re.search(r'\d', password)) or not bool(re.search(r'[a-z]', password)) or not bool(re.search(r'[A-Z]', password)) or len(password)<8:
        return Response(json.dumps({"message": "Invalid password."}), 400)

    user = User.query.filter(User.email == email).first()

    if user:
        return Response(json.dumps({"message": "Email already exists."}), 400)

    user = User ( email = email, password = password, forename = forename, surname = surname, role = "buyer" if isCustomer else "warehouseman" );
    database.session.add ( user )
    database.session.commit ( )

    return Response ( "", status = 200 )

jwt = JWTManager ( application )

@application.route ( "/login", methods = ["POST"] )
def login ( ):
    email = request.json.get ( "email", "" )
    password = request.json.get ( "password", "" )

    if len(email) == 0:
        return Response(json.dumps({"message": "Field email is missing."}), 400)
    if len(password) == 0:
        return Response(json.dumps({"message": "Field password is missing."}), 400)

    if not re.match(r"[^@]+@[^@]+\.[^@]{2,}", email):
        return Response(json.dumps({"message": "Invalid email."}), 400)

    user = User.query.filter ( and_ ( User.email == email, User.password == password ) ).first ( )

    if not user:
        return Response(json.dumps({"message": "Invalid credentials."}), 400)

    additionalClaims = {
            "forename": user.forename,
            "surname": user.surname,
            "role": user.role
    }

    accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims )
    refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims )

    return Response(json.dumps({"accessToken" : accessToken, "refreshToken" : refreshToken}), status = 200)

@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):
    identity = get_jwt_identity ( )
    refreshClaims = get_jwt ( )

    additionalClaims = {
            "forename": refreshClaims["forename"],
            "surname": refreshClaims["surname"],
            "role": refreshClaims["role"]
    }

    return Response ( json.dumps({"accessToken" : create_access_token ( identity = identity, additional_claims = additionalClaims )}), status = 200 )

@application.route ( "/delete", methods = ["POST"] )
@jwt_required()
def delete():
    additionalClaims = get_jwt()

    if additionalClaims["role"] != "admin":
        return Response(json.dumps({"msg" : "Missing Authorization Header"}), status=401)

    email = request.json.get("email", "")

    if len(email) == 0:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    if not re.match(r"[^@]+@[^@]+\.[^@]{2,}", email):
        return Response(json.dumps({"message": "Invalid email."}), 400)

    user = User.query.filter(User.email == email).first()

    if not user:
        return Response(json.dumps({"message": "Unknown user."}), 400)

    database.session.delete(user)
    database.session.commit()

    return Response("", status=200)

if  __name__ == "__main__" :
    database.init_app ( application );
    application.run ( debug = True, host = "0.0.0.0", port = 5002 );