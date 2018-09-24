from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ElementalTree
import config
import requests
import json

Base = declarative_base()

BAMBOO_URL = 'https://' + config.API_KEY + config.API_REQUEST_GATE + config.DOMAIN + config.API_DIRECTORY_REQUEST


class EmployeeData(Base):
    _tablename = 'employee_data'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    department = Column(String(120))
    jobTitle = Column(String(120))
    email = Column(String(120))
    mobilePhone = Column(String(120))

    def __init__(self, name, department, job_title, email, _id, mobile_phone):
        self.name = name
        self.department = department
        self.jobTitle = job_title
        self.email = email
        self.id = _id
        self.mobilePhone = mobile_phone


class BambooParser:

    def __init__(self, url: str):
        self._bamboo_url = url

    def _database_init(self):

        engine = create_engine('sqlite:///employee_db.db')

        connection = engine.connect()

        Base.metadata.create_all(engine)

        session_factory = sessionmaker(engine)

        return session_factory, connection

    def _get_employees(self):
        try:
            response = requests.get(self._bamboo_url)
            xml = ElementalTree.fromstring(response.text)
            return xml

        except requests.HTTPError:
            return False

    def available_fields(self):

        xml_fields = self._get_employees()
        padding = 8

        for fields_set in xml_fields.iter('fieldset'):
            fields_list = [field.attrib['id'] for field in fields_set.iter('field')]

            box_len = max([len(title) for title in fields_list]) + padding
            top_and_bottom = ''.join(['+'] + ['-' * box_len] + ['+'])
            result = top_and_bottom

            for title in fields_list:
                if len(title) % 2:
                    right_indent = (box_len - len(title)) // 2 + 1
                else:
                    right_indent = (box_len - len(title)) // 2

                left_indent = (box_len - len(title)) // 2
                left_spaces = ' ' * left_indent

                right_spaces = ' ' * right_indent
                result += '\n' + '|' + left_spaces + title + right_spaces + '|\n'

            result += top_and_bottom

            return result

    def bamboo_parse(self):
        xml = self._get_employees()

        if not xml:
            return

        employees = []
        for emp in xml.iter('employee'):
            name_tag = {'name': '', 'department': '', 'jobTitle': '',
                        'email': '', 'id': int(emp.attrib['id']), 'mobilePhone': ''}

            for data in emp.iter('field'):
                attrib_id = data.attrib['id']
                text = data.text

                if attrib_id == 'displayName':
                    name_tag['name'] = text
                elif attrib_id == 'department':
                    name_tag['department'] = text
                elif attrib_id == 'jobTitle':
                    name_tag['jobTitle'] = text
                elif attrib_id == 'workEmail':
                    name_tag['email'] = text
                elif attrib_id == 'id':
                    name_tag['id'] = text
                elif attrib_id == 'mobilePhone':
                    name_tag['mobilePhone'] = text
                else:
                    continue

            employees.append(name_tag)

            self._write_session(employees)

    def _write_session(self, emp):

        session_factory, connection = self._database_init()

        session = session_factory()

        employees_list = [EmployeeData(name=item['name'],
                                       department=item['department'],
                                       job_title=item['jobTitle'],
                                       email=item['email'],
                                       _id=item['id'],
                                       mobile_phone=item['mobilePhone']) for item in emp]

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
        with open('employee_data.json', 'w') as file:
            json.dump(write_list, file, indent=4)

        session.close()
        connection.close()


if __name__ == '__main__':
    bamboo_parser = BambooParser(url=BAMBOO_URL)
    print(bamboo_parser.available_fields())
    bamboo_parser.bamboo_parse()
