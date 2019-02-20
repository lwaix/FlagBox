##### [中文-Chinese](https://github.com/lwaix/Pmorm/blob/master/README-zh.md "中文-Chinese")

# pmorm.py - a simple mysql orm for python3

![](https://img.shields.io/badge/python-3.5-red.svg)

![](https://img.shields.io/badge/license-MIT-green.svg)

#### Functional overview

- Model-Oriented operations
- Basic CRUD
- Operator query
- Automatic safety escape

## Installing

```
shell>pip install Pmorm
```

## Usage

### Create a database for the program before using

```
mysql>CREATE DATABASE testdb;
```

### Quick start

---

#### Create the connection

```python
from pmorm import Mysql

mydb = Mysql('localhost', 'root', 'your-passwd', 'testdb')
```

---

#### Create a model and create the table

```python
from pmorm import PrimaryKeyField, VarcharField, DoubleField

# Model class
class User(mydb.Model):
    # Config the table name
    __table__ = 'user'

    # Define fields in a model
    id = PrimaryKeyField()  # id field must be defined like this
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)
    balance = DoubleField(nullable=False, unique=True, default=0.0)

# Create table if it hasn't been created
User.create_table()
```

---

#### Insert

```python
# A easy way
user1 = User(username='user1', password='passwd1')
user1.insert()

# Another way
user2 = User()
user2.username = 'user2'
user2.password = 'passwd2'
user2.balance = 3000.0
user2.insert()

# You can modify it before inserting
user3 = User(username='userx')
user3.username = 'user3'
user3.password = 'passwd3'
user3.insert()

# Cheak if objects has been inserted
print(user1.inserted()) # True
```

---

#### Search

##### Get all

```python
users = User.search().all()

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

##### Search all by one condition

```python
users = User.search(User.username != 'unkonwn').all()

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

##### Search by combination queries

```python
# By using | and & operators
user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).first()

"""
Attention:
  - The code below is the same as the result above
  - The difference:`first()` function selects only the first,it's faster
  - But `all()[0]` gets all the first and then take the first one,it's slower

user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).all()[0]


In conclusion:
  - If you only need to get the first one, use `first()`
  - If you need to get all, use `all()`
"""

print("id:{} username:{} password:{} balance:{}".format(user1.id, user1.username, user1.password, user1.balance))
```

##### Sort by using the "orders" option

```python
users = User.search(
    (User.username!='user1') | (User.password!='passwd1'),
    orders=[-User.id] # Sort by id in reverse order
).all()

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

##### Using the limit

```python
users = User.search(User.username!='unknown').all(limit=(0,2)) # limit only returns the first two results of the query, equivalent to "LIMIT 0, 2"
# Equivalent to:`users = User.search(User.username!='unknown').all(limit=(2))`

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

---

#### Update

```python
# Get one first
user1 = User.search(
    ((User.username=='user1') | (User.password=='passwd1') & (User.id==1)) # Complex queries
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

# Edit it and update
user1.username = 'edit'
user1.update()
print("id:{} username:{} password:{} balance:{}".format(user1.id, user1.username, user1.password, user1.balance))
```

---

#### Delete

```python
# Get one first
user1 = User.search(User.username=='edit').first()
# Delete it
user1.delete()
```

---

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

#### PrimaryKeyField must be defined in each model, so a basic model looks like...

```python
mydb = Mysql('localhost', 'root', 'your-passwd', 'your-database')
class ModelName(mydb.Model):
    __table__ = 'mytable'

    id = PrimaryKeyField()
    # Other fields...
```