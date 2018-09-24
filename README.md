# Python BambooHR 'Read and Parse' w/o API usage

If you ever needed local database or automate data usage from BambooHR service, you can use this script for you needs.
Parse though all of your data on BambooHR.

Also you can pin this link for fast access:[ BambooHR Parser ](https://yevhenradchenko.github.io/bamboohr-parser/)


## Install all needed libraries

```shell
pip install -r requirements.txt
``` 
### You can see all field you have acces to though :

```python
def available_fields():
```

### Pay attentions to all places what you need to change is case off adding new fields:


- Add new field's to :

```python
class EmployeeData(Base):
```

```python
def bamboo_parse():
```

```python
def write_session(emp):
```

- And don't forget about write list :

```python
write_list = [{'id': i[0],
                   'name': i[1],
                   'department': i[2],
                   'jobTitle': i[3],
                   'email': i[4],
                   'mobilePhone': i[5]
                   'MY_NEW_FIELD': i[6] } for i in list(connection.execute('select * from employee_data'))]
```
