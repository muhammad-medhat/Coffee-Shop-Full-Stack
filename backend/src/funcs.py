import json
from operator import truediv
from .database.models import db_drop_and_create_all, setup_db, Drink

def get_drinks_list(short=True):
    drinks = Drink.query.all()
    if len(drinks > 0):
        if short:
            return [drink.short() for drink in drinks]
        else:
            return [drink.long() for drink in drinks]
    else:
        return []