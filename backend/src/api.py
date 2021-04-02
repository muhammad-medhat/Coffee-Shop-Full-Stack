import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)


# -------------------------------------------------------------
# Helper Functions
def get_drinks_list(short=True):
    drinks = Drink.query.all()
    if len(drinks) > 0:
        if short:
            return [drink.short() for drink in drinks]
        else:
            return [drink.long() for drink in drinks]
    else:
        return []

# db_drop_and_create_all()
# ROUTES


@app.route("/drinks")
def get_drinks():
    return jsonify({
        "status": 200,
        "success": True,
        "drinks": get_drinks_list()
    })


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(pld):
    return jsonify({
        "status": 200,
        "success": True,
        "drinks": get_drinks_list(False)
    })


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(pld):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    drink = Drink(title=title, recipe=json.dumps(recipe))

    drink.insert()
    return jsonify({
        "status": 200,
        "success": True,
        "drinks": get_drinks_list(False)
    })


@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(pld, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        if drink:
            body = request.get_json()
            if body.get('title'):
                drink.title = body.get('title')
            if body.get('recipe'):
                drink.recipe = json.dumps(body.get('recipe'))
            drink.update()
            return jsonify({
                'status': 200,
                "success": True,
                "drink": drink
            })
        else:
            abort(404)
    except:
        abort(500)


@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(pld, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        print(drink)
        if drink:
            drink.delete()
            return jsonify({
                'status': 200,
                "success": True,
                "drink": drink_id
            })
        else:
            abort(404)
    except:
        abort(401)

# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request',
        "code": error.code,
        "description": error.description
    }), 400


@app.errorhandler(401)
def uauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized",
        "code": error.code,
        "description": error.description
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden",
        "code": error.code,
        "description": error.description
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found",
            "code": error.code,
            "description": error.description
        }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500
