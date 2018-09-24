from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ElementalTree
import config
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


class BambooParser:
    _url = 'https://' + config.API_KEY + config.API_REQUEST_GATE + config.DOMAIN + config.API_DIRECTORY_REQUEST


    def _database_init(self):
        engine = create_engine('sqlite:///employee_db.db')
        Base.metadata.create_all(engine)
        self._connection = engine.connect()
        self._session_factory = sessionmaker(engine)

    def _get_employees_xml(self):
        try:
            request = requests.get(self._url)
            xml_root = ElementalTree.fromstring(request.text)
            return xml_root
        except requests.HTTPError:
            return None

    def parse(self):
        root = self._get_employees_xml()
        if not root:
            return

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

        self.write_session(employees)

    def write_session(self, employees):

        self._database_init()
        session = self._session_factory()

        def _parse_employee(item):
            return EmployeeData(name=item['name'], department=item['department'], jobTitle=item['jobTitle'],
                                email=item['email'], id=item['id'], mobilePhone=item['mobilePhone'])

        employees_list = [_parse_employee(item) for item in employees]

        avoid_duplicates = list(self._connection.execute('select * from employee_data'))

        for i in employees_list:
            if i.name not in [j[1] for j in avoid_duplicates]:
                session.add(i)

        session.commit()

        write_list = [{'id': i[0],
                       'name': i[1],
                       'department': i[2],
                       'jobTitle': i[3],
                       'email': i[4],
                       'mobilePhone': i[5]} for i in list(self._connection.execute('select * from employee_data'))]
        with open('employee_data.json', 'w') as file:
            json.dump(write_list, file)

        session.close()
        self._connection.close()


if __name__ == '__main__':
    BambooParser().parse()
