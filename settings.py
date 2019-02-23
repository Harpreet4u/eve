from datetime import datetime
to_date = lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S %z')
schema = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'firstname': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 10,
    },
    'lastname': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 15,
        'required': True,
        # talk about hard constraints! For the purpose of the demo
        # 'lastname' is an API entry-point, so we need it to be unique.
        'unique': True,
    },
    # 'role' is a list, and can only contain values from 'allowed'.
    'role': {
        'type': 'list',
        'allowed': ["author", "contributor", "copy"],
    },
    # An embedded 'strongly-typed' dictionary.
    'location': {
        'type': 'dict',
        'schema': {
            'address': {'type': 'string'},
            'city': {'type': 'string'}
        },
    },
    'born': {
        'type': 'datetime',
    },
}
people = {
    'item_title': 'person',

    # GET requests at '/people/<lastname>'.
    'additional_lookup': {
        'url': 'regex("[\W]+")',
        'field': 'lastname'
    },

    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    # most global settings can be overridden at resource level
    'resource_methods': ['GET', 'POST', 'DELETE'],

    'schema': schema
}
companies_schema = {
    
    'index': {
        'type': 'integer',
        'unique': True,
        'required': True,
    },
    'company': {
        'type': 'string',
    },
}
companies = {
    'id_field': 'index',
    'item_title': 'companies',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'index'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    'resource_methods': ['GET', 'POST', 'DELETE'],

    'schema': companies_schema
}
employees_schema = {
    'index': {
        'type': 'integer',
        'unique': True,
        'required': True,
    },
    'guid': {
        'type': 'string',
        'unique': True,
    },
    'has_died': {
        'type': 'boolean'
    },
    'balance': {
        'type': 'string'
    },
    'picture': {
        'type': 'string'
    },
    'age': {
        'type': 'integer'
    },
    'eyeColor': {
        'type': 'string'
    },
    'name': {
        'type': 'string'
    },
    'gender': {
        'type': 'string'
    },
    'company_id': {
        'type': 'integer',
        'data_relation': {
            'resource': 'companies',
            'field': 'index',
            'embeddable': True
        }
    },
    'email': {
        'type': 'string'
    },
    'phone': {
        'type': 'string'
    },
    'address': {
        'type': 'string'
    },
    'about': {
        'type': 'string'
    },
    'registered': {
        'type': 'datetime',
        'coerce': to_date
    },
    'tags': {
        'type': 'list',
        'schema': {
            'type': 'string'
        }
    },
    'friends': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'index': {
                    'type': 'integer'
                }
            }
        }
    },
    'greeting': {
        'type': 'string'
    },
    'favouriteFood': {
        'type': 'list',
        'schema': {
            'type': 'string'
        }
    },
    'fruits': {
        'type': 'list',
        'schema': {
            'type': 'string'
        }
    },
    'vegetables': {
        'type': 'list',
        'schema': {
            'type': 'string'
        }
    }
}
employees = {
    'item_title': 'employees',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'index'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    'resource_methods': ['GET', 'POST', 'DELETE'],

    'schema': employees_schema,
    'url': 'employees'
}

get_employees = {
    'schema': employees_schema,
    'url': 'get_company_employees/<int:company_id>',
    'datasource': {'source': 'employees'}
}

friends = {
    'schema': employees_schema,
    'datasource': {
        'source': 'employees',
        'projection': {
            'name': 1,
            'age': 1,
            'address': 1,
            'phone': 1,
            'eyeColor': 1,
            'has_died': 1,
            'friends': 1
        }
    }
}

favourite_food = {
    'schema': employees_schema,
    'datasource': {
        'source': 'employees',
        'projection': {
            'name': 1,
            'age': 1,
            'fruits': 1,
            'vegetables': 1
        }
    }
}

DOMAIN = {
'people': people,
'companies': companies,
'employees': employees,
'get_employees': get_employees,
'friends': friends,
'favourite_food': favourite_food
}
