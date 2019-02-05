# pmorm.py - a simple mysql orm for python3

## Install pmorm

```
python3 .\setup.py install --user
```

## Usage

### Before using

#### Create a database for the program

```
mysql>CREATE DATABASE testdb;
```

### Quick start

#### Create a mysql database connection

```python
from pmorm import Mysql

mydb = Mysql('localhost', 'root', 'your-passwd', 'testdb')
```

#### Create a model and create the table

```python
from pmorm import Base, PrimaryKeyField, VarcharField

# Model class
class User(Base):
    # Built-in class Meta for configuring database and table
    class Meta:
        db = mydb
        table = 'user'

    # Define fields in a model
    id = PrimaryKeyField()  # ID field must be defined like this
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)

# Create table if it hasn't been created
User.create_table()
```

#### Insert one row

```python
# A easy way to insert
user1 = User(username='user1', password='passwd1')
user1.insert()

# You can also insert like this
user2 = User()
user2.username = 'user2'
user2.password = 'passwd2'
user2.insert()

# You can modify it before inserting
user3 = User(username='userx')
user3.username = 'user3'
user3.password = 'passwd3'
user3.insert()

# Cheak if objects has been inserted
print(user1.inserted()) # True
```

#### Search rows

```python
# Get all rows
users = User.search().all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

# Search by one condition
users = User.search(User.username != 'unkonw').all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

# Search by conditions of the combination
user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

# Sort by using the "orders" option
users = User.search(
    (User.username!='user1') | (User.password!='passwd1'),
    orders=[User.id]
).all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))
```

##### Attention: search() return a "Result" object, you can get specific data by its methods all() and first()

#### Edit rows

```python
# Get one user
user1 = User.search(
    ((User.username=='user1') | (User.password=='passwd1') & (User.id==1)) # Complex queries
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))
# Edit it and update
user1.username = 'edit'
user1.update()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))
```

#### Delete rows

```python
user1.delete()
```

### A full example

```python
from pmorm import Mysql

mydb = Mysql('localhost', 'root', 'your-passwd', 'your-database')

from pmorm import Base, PrimaryKeyField, VarcharField

class User(Base):
    class Meta:
        db = mydb
        table = 'user'

    id = PrimaryKeyField()
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)

User.drop_table()
User.create_table()

user1 = User(username='user1', password='passwd1')
user1.insert()

user2 = User()
user2.username = 'user2'
user2.password = 'passwd2'
user2.insert()

user3 = User(username='userx')
user3.username = 'user3'
user3.password = 'passwd3'
user3.insert()

print("===SIGN1===")

print(user1.inserted())

print("===SIGN2===")

users = User.search().all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

print("===SIGN3===")

users = User.search(User.username != 'unkonw').all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

print("===SIGN4===")

user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

print("===SIGN5===")

users = User.search(
    (User.username!='user1') | (User.password!='passwd1'),
    orders=[-User.id]
).all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

print("===SIGN6===")

user1 = User.search(
    ((User.username=='user1') | (User.password=='passwd1') & (User.id==1))
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))
user1.username = 'edituser1'
user1.update()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

user1.delete()
```