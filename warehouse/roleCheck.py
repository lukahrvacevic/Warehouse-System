from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Response
import json

def roleCheck ( role ):
    verify_jwt_in_request ( )
    claims = get_jwt ( )
    if not ("role" in claims) or role != claims["role"]:
        return Response ( json.dumps({"msg" : "Missing Authorization Header"}), status = 401 )
    else:
        return None