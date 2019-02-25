import json
import os
from run import app
from . import TestMinimal
from test_settings import MONGO_DBNAME

app.config['MONGO_HOST'] = "localhost"
app.config['MONGO_PORT'] = 27017
app.config['MONGO_USERNAME'] = "test_user"
app.config['MONGO_PASSWORD'] = "test_pw"
app.config['MONGO_DBNAME'] = "eve_test"


class TestCompaniesAPI(TestMinimal):
    
    def setUp(self, url_converters=None):
        super(TestCompaniesAPI, self).setUp(url_converters=url_converters)
        self.known_resource = 'companies'
        self.test_client = app.test_client()

    def bulk_insert(self):
        _db = self.connection[MONGO_DBNAME]
        _db.companies.insert_one({'index': 1, 'company': "ABC"})
        _db.companies.insert_one({'index': 2, 'company': "DEF"})
    
    def test_companies_get_call(self):
        response, status_code = self.get(self.known_resource)
        self.assert200(status_code)
        self.assertCacheControl(self.known_resource)
        self.assertEquals(response['_items'][0]['index'], 1) 
        self.assertEquals(response['_items'][0]['company'], 'ABC') 

    def test_companies_get_item_call(self):
        response, status_code = self.get(self.known_resource, item=1)
        self.assert200(status_code)
        self.assertCacheControl(self.known_resource)
        self.assertEquals(response['index'], 1) 
        self.assertEquals(response['company'], 'ABC') 


class TestEmployeesAPI(TestMinimal):
    
    def setUp(self, url_converters=None):
        self.test_client = app.test_client()
        self.known_resource = 'employees'
        path = os.path.join(os.path.dirname(__file__), 'employees.json')
        with open(path, 'r') as emp_data:
            self.employees = json.loads(emp_data.read())
        super(TestEmployeesAPI, self).setUp(url_converters=url_converters)
        self.maxDiff = None

    def bulk_insert(self):
        _db = self.connection[MONGO_DBNAME]
        _db.companies.insert_one({'index': 1, 'company': "ABC"})
        _db.companies.insert_one({'index': 2, 'company': "DEF"})
        self.post(self.known_resource, data=self.employees[0])
        self.post(self.known_resource, data=self.employees[1])
    
    def test_employees_get_call(self):
        response, status_code = self.get(self.known_resource)
        self.assert200(status_code)
        self.assertCacheControl(self.known_resource)
        del response['_items'][0]['_created']
        del response['_items'][0]['_updated']
        del response['_items'][0]['_etag']
        del response['_items'][0]['_links']
        del response['_items'][0]['vegetables']
        del response['_items'][0]['fruits']
        del response['_items'][0]['registered']
        del self.employees[0]['registered']
        self.assertDictEqual(response['_items'][0], self.employees[0]) 

    def test_companies_get_item_call(self):
        response, status_code = self.get(self.known_resource, query="?where={\"index\":0}")
        self.assert200(status_code)
        self.assertCacheControl(self.known_resource)
        del response['_items'][0]['_created']
        del response['_items'][0]['_updated']
        del response['_items'][0]['_etag']
        del response['_items'][0]['_links']
        del response['_items'][0]['vegetables']
        del response['_items'][0]['fruits']
        del response['_items'][0]['registered']
        del self.employees[0]['registered']
        self.assertDictEqual(response['_items'][0], self.employees[0]) 
 

class TestCompanyEmployeesAPI(TestMinimal):
    
    def setUp(self, url_converters=None):
        self.test_client = app.test_client()
        path = os.path.join(os.path.dirname(__file__), 'employees.json')
        with open(path, 'r') as emp_data:
            self.employees = json.loads(emp_data.read())
        super(TestCompanyEmployeesAPI, self).setUp(url_converters=url_converters)
        self.maxDiff = None

    def bulk_insert(self):
        _db = self.connection[MONGO_DBNAME]
        _db.companies.insert_one({'index': 1, 'company': "ABC"})
        _db.companies.insert_one({'index': 2, 'company': "DEF"})
        self.post('employees', data=self.employees[0])
        self.post('employees', data=self.employees[1])
    
    def test_company_employees_get_call(self):
        response = app.test_client().get('/get_company_employees/ABC')
        self.assert200(response.status_code)
        response, _ = self.parse_response(response)
        del response['_items'][0]['_created']
        del response['_items'][0]['_updated']
        del response['_items'][0]['_etag']
        del response['_items'][0]['_links']
        del response['_items'][0]['vegetables']
        del response['_items'][0]['fruits']
        del response['_items'][0]['registered']
        del self.employees[0]['registered']
        self.assertDictEqual(response['_items'][0], self.employees[0]) 

class TestEmployeesWithMutualBrownEyesAliveFriendsAPI(TestMinimal):
    
    def setUp(self, url_converters=None):
        self.test_client = app.test_client()
        path = os.path.join(os.path.dirname(__file__), 'employees.json')
        with open(path, 'r') as emp_data:
            self.employees = json.loads(emp_data.read())
        super(TestEmployeesWithMutualBrownEyesAliveFriendsAPI, self).setUp(url_converters=url_converters)
        self.maxDiff = None

    def bulk_insert(self):
        _db = self.connection[MONGO_DBNAME]
        _db.companies.insert_one({'index': 1, 'company': "ABC"})
        _db.companies.insert_one({'index': 2, 'company': "DEF"})
        self.post('employees', data=self.employees[0])
        self.post('employees', data=self.employees[1])
        self.post('employees', data=self.employees[2])
    
    def test_common_alive_friends_with_brown_eyes_get_call(self):
        response = app.test_client().get('/friends/common/1/2')
        self.assert200(response.status_code)
        response, _ = self.parse_response(response)
        del response['_items'][0]['_created']
        del response['_items'][0]['_updated']
        del response['_items'][0]['_etag']
        del response['_items'][0]['_links']
        del self.employees[0]['registered']
        self.assertDictEqual(response['_items'][0]['friends'][0], {'index': 0}) 
        self.assertDictEqual(response['_items'][1]['friends'][0], {'index': 0}) 
        self.assertEquals(len(response['_items'][1]['friends']), 1) 
        self.assertEquals(len(response['_items'][0]['friends']), 1) 
