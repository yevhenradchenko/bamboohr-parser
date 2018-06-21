from PyBambooHR import PyBambooHR
from pprint import pprint

bamboo = PyBambooHR(subdomain='domain', api_key='apikey')

employees = bamboo.get_employee_directory()

pprint(employees)
