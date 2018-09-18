from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET
import requests
import json


Base = declarative_base()


class EmployeeData(Base):

    __tablename__ = 'employee_data'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    department = Column(String(120))
    jobTitle = Column(String(120))
    email = Column(String(120))
    mobilePhone = Column(String(120))

    def __init__(self, name, department, jobTitle, email, id, mobilePhone):
        self.name = name
        self.department = department
        self.jobTitle = jobTitle
        self.email = email
        self.id = id
        self.mobilePhone = mobilePhone


engine = create_engine('sqlite:///employee_db.db')

connection = engine.connect()

Base.metadata.create_all(engine)


api_key = 'YOURS_BAMBOOHR_APIKEY'
url = 'https://' + api_key + ':x@api.bamboohr.com/api/gateway.php/DOMAIN_NAME/v1/employees/directory'
r = requests.get(url)
root = ET.fromstring(r.text)


employees = []
for emp in root.iter('employee'):

        name_tag = {'name': '',
                    'department': '',
                    'jobTitle': '',
                    'email': '',
                    'id': int(emp.attrib['id']),
                    'mobilePhone': '',
                    }

        for data in emp.iter('field'):
            if data.attrib['id'] == 'displayName':
                name_tag['name'] = data.text
            elif data.attrib['id'] == 'department':
                name_tag['department'] = data.text
            elif data.attrib['id'] == 'jobTitle':
                name_tag['jobTitle'] = data.text
            elif data.attrib['id'] == 'workEmail':
                name_tag['email'] = data.text
            elif data.attrib['id'] == 'id':
                name_tag['id'] = data.text
            elif data.attrib['id'] == 'mobilePhone':
                name_tag['mobilePhone'] = data.text
            else:
                continue
        employees.append(name_tag)


session_factory = sessionmaker(engine)
session = session_factory()


employees_list = [EmployeeData(name=item['name'],
                               department=item['department'],
                               jobTitle=item['jobTitle'],
                               email=item['email'],
                               id=item['id'],
                               mobilePhone=item['mobilePhone']) for item in employees]

avoid_duplicates = list(connection.execute('select * from employee_data'))


for i in employees_list:
    if i.name not in [j[1] for j in avoid_duplicates]:
        session.add(i)

session.commit()

write_list = [{'id': i[0],
               'name': i[1],
               'department': i[2],
               'jobTitle': i[3],
               'email': i[4],
               'mobilePhone': i[5]} for i in list(connection.execute('select * from employee_data'))]

session.close()
connection.close()


with open('employee_data.json', 'w') as file:
    data = json.dump(write_list, file)
