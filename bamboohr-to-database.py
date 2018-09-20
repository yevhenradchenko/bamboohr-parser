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


def database_init():

    engine = create_engine('sqlite:///employee_db.db')

    connection = engine.connect()

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(engine)

    return session_factory, connection


def bamboo_request():

    url = 'https://' + config.API_KEY + config.API_REQUEST_GATE + config.DOMAIN + config.API_DIRECTORY_REQUEST

    try:
        requested_url = requests.get(url)
        root = ElementalTree.fromstring(requested_url.text)

        return root

    except requests.HTTPError:
        return False


def available_fields():

    xml_fields = bamboo_request()

    padding = 8

    for fields_set in xml_fields.iter('fieldset'):
        fields_list = [field.attrib['id']for field in fields_set.iter('field')]

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


def bamboo_parse():
    root = bamboo_request()
    if root:
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

        write_session(employees)


def write_session(emp):

    session_factory, connection = database_init()

    session = session_factory()

    employees_list = [EmployeeData(name=item['name'],
                                   department=item['department'],
                                   jobTitle=item['jobTitle'],
                                   email=item['email'],
                                   id=item['id'],
                                   mobilePhone=item['mobilePhone']) for item in emp]

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
    print(available_fields())
    bamboo_parse()
