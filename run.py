import json
import os
from eve import Eve
from eve.methods.get import get
from eve.render import send_response
from flask import abort
from eve_swagger import swagger, add_documentation

app = Eve()
app.register_blueprint(swagger)

app.config['SWAGGER_INFO'] = {
    'title': 'First ever Eve API',
    'version': '1.0',
    'description': 'Backend coding challenge api written in python eve',
    'termsOfService': 'No terms',
    'contact': {
        'name': 'Harpreet',
        'url': 'https://au.linkedin.com/in/harpreet-singh-789aa35a',
    },
    'license': {
        'name': 'BSD',
        'url': 'https://github.com/pyeve/eve-swagger/blob/master/LICENSE'
    },
    'schemes': ['http', 'https']
}

def employee_insert(items):
    path = os.path.join(os.path.dirname(__file__), 'fruits.json')
    with open(path, 'r') as fruit_list:
        fruits = json.loads(fruit_list.read())
        for item in items:
            item['fruits'] = list(filter(lambda x: x in fruits, item['favouriteFood']))
            item['vegetables'] = list(set(item['favouriteFood']) - set(item['fruits']))

def companies_insert(items):
    for item in items:
        item['index'] = item['index'] + 1

def post_favourite_food_callback(request, payload):
    result = json.loads(payload.response[0])
    username = result['_items'][0]['name']
    del result['_items'][0]['name']
    result['_items'][0]['username'] = username
    data_dump = json.dumps(result)
    payload.response[0] = data_dump
    payload.headers[1] = ('Content-Length', str(len(data_dump)))

def post_friends_callback(request, payload):
    result = json.loads(payload.response[0])
    friends_first = result['_items'][0]['friends']
    friends_second = result['_items'][1]['friends']
    friends_first_indexes = set([])
    friends_second_indexes = set([])
    for friend in friends_first:
        friends_first_indexes.add(friend['index'])
    for friend in friends_second:
        friends_second_indexes.add(friend['index'])
    common_friends = friends_first_indexes & friends_second_indexes
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
    dump_data = json.dumps(result)
    payload.response[0] = dump_data
    payload.headers[1] = ('Content-Length', str(len(dump_data)))

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
