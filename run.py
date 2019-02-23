import json
from eve import Eve
from eve.methods.get import get
from eve.render import send_response
from flask import abort
app = Eve()

def employee_insert(items):
    with open('fruits.json', 'r') as fruit_list:
        fruits = json.loads(fruit_list.read())
        for item in items:
            item['fruits'] = list(filter(lambda x: x in fruits, item['favouriteFood']))
            item['vegetables'] = list(set(item['favouriteFood']) - set(item['fruits']))

def companies_insert(items):
    for item in items:
        item['index'] = item['index'] + 1

def pre_get_employees_get_callback(request, lookup):
    pass
    
    """db = app.data.driver.db
    company = db['companies'].find_one({"company": request.view_args['company_id']})
    if db['companies'].count_documents({"company": request.view_args['company_id']}) > 0:
        request.view_args['company_id'] = int(company['index'])
        lookup['company_id'] = int(company['index'])
    """
def post_favourite_food_callback(request, payload):
    result = json.loads(payload.response[0])
    username = result['_items'][0]['name']
    del result['_items'][0]['name']
    result['_items'][0]['username'] = username

def post_friends_callback(request, payload):
    result = json.loads(payload.response[0])
    friends_first = result['_items'][0]['friends']
    friends_second = result['_items'][1]['friends']
    friends_first.extend(friends_second)
    common_friends = set([])
    for friend in friends_first:
        common_friends.add(friend['index'])
    db = app.data.driver.db
    alive_friends_with_brown_eyes = db['employees'].find({'index': {'$in': list(common_friends)}, 'eyeColor': 'brown', 'has_died': False})
    common_friends = []
    for friend in alive_friends_with_brown_eyes:
        common_friends.append({'index': friend['index']})
    result['_items'][0]['friends'] = common_friends
    result['_items'][1]['friends'] = common_friends
    del result['_items'][0]['has_died']
    del result['_items'][1]['has_died']
    del result['_items'][0]['eyeColor']
    del result['_items'][1]['eyeColor']
    payload.response[0] = json.dumps(result)

app.on_pre_GET_get_employees += pre_get_employees_get_callback
app.on_post_GET_friends += post_friends_callback
app.on_post_GET_favourite_food += post_favourite_food_callback
app.on_insert_employees += employee_insert
app.on_insert_companies += companies_insert
@app.route('/favourite_food/<int:person>')
def get_favourite_food(person):
    response = get('favourite_food', {'index': person})
    return send_response('favourite_food', response)

@app.route('/friends/common/<int:person_one>/<int:person_two>')
def get_common_friends(person_one, person_two):
    response = get('friends', {'index': {'$in': [person_one, person_two]}})
    if response[-1][0][-1] != 2:
        return abort(404)
    return send_response('friends', response)

@app.route('/get_company_employees/<string:company_name>')
def get_company_name_employees(company_name):
    db = app.data.driver.db
    company = db['companies'].find_one({"company": company_name})
    if db['companies'].count_documents({"company": company_name}) > 0:
        response = get('get_employees', {'company_id': int(company['index'])})
        return send_response('get_employees', response)
    return abort(404)


if __name__ == '__main__':
    app.run()
