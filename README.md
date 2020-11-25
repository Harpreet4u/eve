# Eve
Python eve Rest API

# Prerequisities:
  - Python3
  - python  eve
  - mongodb
  
# Installation instrustions:
  - It's based upon python eve framework
  - Run `pip install -r requirements.txt` for most of the packages used.
  - Make sure you have `mongodb` up and running as python eve uses mongodb as data store.
  

# REST API SWAGGER:
  - User `https://editor.swagger.io/` to check REST endpoints.
  - Copy paste `swagger.ymal` file from code base.
  - Make sure to use `http` endpoint with python server running on port 5000.
  
  
# How to run python server:
  - `python3 run.py` (It will only run with python3)
  
# Populate resources command
  - Use `sh reload_resources.sh` script to populate resources to REST API.

  ## NOTE:
  ```
  companies.json file company object index starts from 0 but people.json file assumes it to be starting from 1.
  So, code automatically fixes the indexing to start from 1.
  Make sure your resources files respects that intentional/un-intentional rule.
  ```
  
### Endpoint "Given a company return it's all employees":
  - `/get_company_employees/<string:company_name>` or `/get_company_employees/<int:company_id>`
  - company indexes starts from 1.
  
### Endpoint "Given 2 people, provide their information (Name, Age, Address, phone) and the list of their friends in common which have brown eyes and are still alive.":
  - `/friends/common/<int:person_one>/<int:person_two>`
  - person indexes starts from 0

### Endpoint "Given 1 people, provide a list of fruits and vegetables they like. This endpoint must respect this interface for the output: {"username": "Ahi", "age": "30", "fruits": ["banana", "apple"], "vegetables": ["beetroot", "lettuce"]}":
  - `/favourite_food/<int:person>`
  
## Running tests:
  - cd to tests directory and run `python3 -m "nose"`
