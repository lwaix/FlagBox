## pmorm.py - a simple mysql orm for python3

### Usage

#### Create a mysql database connection

```python
from pmorm import mysql

mydb = Mysql('localhost', 'root', 'xuri', 'test1db')
```

#### Create a model

```python
from pmorm import Base, PrimaryKeyField, VarcharField

# Inheriting the Base class is a must
class User(Base):
    # Built-in class Meta parameters for configuring the database and table
    class Meta:
        db = mydb
        table = 'user'

    # You need to define fields in the class like this
    id = PrimaryKeyField()  # The id field must be defined in a model so that pmorm can work properly
    username = VarcherField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcherField(max_length=64, nullable=False, unique=False, default=None)
```

#### Insert one row

```python
# A easy way to insert
user1 = User(username='user1', password='passwd')
user1.insert()

# You can also insert like this
user2 = User()
print(user2.inserted()) # You can cheak if the object has been inserted into the database
user2.username = 'user2'
user2.password = 'passwd'
user2.insert()
print(user2.inserted())
```

#### Search rows

```python
user = User.search(User.username == 'user1').first()
# rows = User.search(User.username != 'user').all()[0]
# rows = User.search(User.id <= 2).last()
print(user.id, user.username, user.password)
```

#### Edit rows

```python
user.username = 'edit'
user.update()
```

#### Delete rows

```python
user.delete()
```

### A full example

```python
from pmorm import Mysql, Base, PrimaryKeyField, VarcharField

mydb = Mysql('localhost', 'root', 'xuri', 'test1db')

class User(Base):
    class Meta:
        db = mydb
        table = 'user'

    id = PrimaryKeyField()
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)

User.drop_table()
User.create_table()

user1 = User(username='user1', password='password1')
user2 = User(username='user2', password='password2')

# Insert
print(user1.inserted())
user1.insert()
print(user1.inserted())
user2.insert()

print('===========SPLIT==============')

# Search
# Unconditional query: Returns all
users = User.search().all()
for user in users:
    print(user.username)
# Conditional query
user = User.search(
    (User.username=='user1') & (User.password=='password1')
).first()
print(user.username)
# Order by...
users = User.search(
    (User.username!='It is impossible to be the username'),
    [-User.username]
).all()
for user in users:
    print(user.username)

print('===========SPLIT==============')

# Edit
user1.username = 'editedusername'
user1.update()
users = User.search().all()
for user in users:
    print(user.username)

print('===========SPLIT==============')

# Delete
user1.delete()
users = User.search().all()
for user in users:
    print(user.username)
```