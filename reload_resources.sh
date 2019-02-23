# !/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

echo 'Deleting existing data...'
clearCompanies='curl -X DELETE http://127.0.0.1:5000/companies'
clearEmployees='curl -X DELETE http://127.0.0.1:5000/employees'
eval $clearCompanies
eval $clearEmployees

echo
echo 'Existing data deleted!'
echo
echo 'Loading data from resources folder...'
echo
addCompanies="curl --data-binary '@${SCRIPTPATH}/resources/companies.json' -H 'Content-Type: application/json'  http://127.0.0.1:5000/companies"
addEmployees="curl --data-binary '@${SCRIPTPATH}/resources/people.json' -H 'Content-Type: application/json'  http://127.0.0.1:5000/employees"
eval $addCompanies > /dev/null
eval $addEmployees > /dev/null
echo
echo 'Loadind resources done!'
echo
