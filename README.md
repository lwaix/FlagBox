##### [中文-Chinese](https://github.com/lwaix/Pmorm/blob/master/README-zh.md "中文-Chinese")

# pmorm.py - a simple mysql orm for python3

![](https://img.shields.io/badge/python-3.5-red.svg)

![](https://img.shields.io/badge/license-MIT-green.svg)

Functional overview

- Model-Oriented operations
- Basic CRUD
- Operator query
- Automatic safety escape

## Installing

```
shell>pip install Pmorm
```

## Basic

```python
from pmorm import Mysql

# Create a connection.Automatically create database(if it is not created)
db = Mysql('localhost', 'root', 'your-password', 'testdb1')

class Worker(db.Model):
    __table__ = 'worker'

    id = db.PrimaryKeyField()
    username = db.VarcharField(max_length=32, nullable=False, unique=True, default=None, comment="Worker's username")
    password = db.VarcharField(max_length=32, nullable=False, unique=False, default=None, comment="Worker's password")
    salary = db.FloatField(nullable=False, unique=False, default=0.0, comment="Worker's monthly salary")

Worker.create_table()

# Insert
jack = Worker(username='Jack', password='JackSoHandsome', salary=3999.2)
jack.insert()

mary = Worker()
mary.username = 'Mary'
mary.password = 'MarySoBeautiful'
mary.insert()

# Get all and get the first
all_workers = Worker.select().all()
the_first_worker = Worker.select().first()

# Query by operators
rich_workers = Worker.select(Worker.salary>=3000.0).all()

# Complex query by operators & and |
worker_jack = Worker.select(
	((Worker.username == 'jack') & (Worker.password == 'JackSoHandsome')) | (Worker.salary=='3999.2')
).first()

# Order the rows
the_richest_worker = Worker.select(orders=[-Worker.salary]).first()

# Use the result
for worker in all_workers:
	print('username:{} password:{} salary:{}'.format(worker.username, worker.password, worker.salary))
print('And the richest worker is {}'.format(the_richest_worker.username))

# Update one row
worker_jack.salary = 3000.0
worker_jack.update()

# Delete one row
worker_jack.delete()
```

## Else

### Currently supported MySQL fields

Pmorm|Mysql
--|:--:
PrimaryKeyField|NO
BooleanField|BOOLEAN
IntField|INT
BigIntField|BIGINT
FloatField|FLOAT
DoubleField|DOUBLE
VarcharField|VARCHAR
TextField|TEXT

PrimaryKeyField must be defined in each model, so a basic model looks like...

```python
mydb = Mysql('localhost', 'root', 'your-passwd', 'your-database')
class ModelName(mydb.Model):
    __table__ = 'mytable'

    id = mydb.PrimaryKeyField()
    # Other fields...
```