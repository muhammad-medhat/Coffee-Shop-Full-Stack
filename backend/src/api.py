import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
# import .funcs

app = Flask(__name__)
setup_db(app)
CORS(app)


def get_drinks_list(short=True):
    drinks = Drink.query.all()
    if len(drinks) > 0:
        if short:
            # return [drink.short() for drink in drinks]
            return [drink for drink in drinks]
        else:
            return [drink.long() for drink in drinks]
    else:
        return []

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():
    return jsonify({
        'msg':'GET /drinks', 
        "status":200,
        "success": True, 
        "drinks": get_drinks_list()
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    return jsonify({
        'msg': 'GET /drinks-detail', 
        "status":200,
        "success": True, 
        "drinks": get_drinks_list(False)
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
# @requires_auth('post:drinks')
def post_drinks():
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()
    
    return jsonify({
        'msg': 'POST /drinks',
        "status":200,
        "success": True, 
        "drinks": get_drinks_list(False)
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
# @requires_auth('patch:drinks')
def patch_drink(drink_id):
    try:
        drink=Drink.query.get(drink_id)
        if drink:
            body = request.get_json()
            drink.title = body.get('title', None)
            drink.recipe = body.get('recipe', None)  
            drink.update()          
            return jsonify({
                'msg': f'PATCH /drinks/{drink_id}', 
                'status':200, 
                "success": True, 
                "drink": drink
            })
        else:
            abort(404)
    except:
        abort(401)
        

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink=Drink.query.get(drink_id)
        print(drink)
        if drink:         

            drink.delete()  
            return jsonify({
                'msg': f'delete /drinks/{drink_id}', 
                'status':200, 
                "success": True, 
                "drink": drink_id
            })  
        else:            
            abort(404)  
    except:
        abort(401)

## Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request',
        "description": error.description

    }), 400
    
@app.errorhandler(401)
def invalid_header(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": error.description
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden",
        "code":error.code,
        "description": error.description      
    }), 401
    
@app.errorhandler(404)
def not_found(error):
    return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found",
            "code":error.code,
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








'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
