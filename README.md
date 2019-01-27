## pmorm.py - a simple mysql orm for python3 users

#### usage

```python
from pmorm import Mysql, Base, PrimaryKeyField, VarcharField

class User(Base):
    class Meta:
        db = Mysql('localhost', 'root', 'xuri', 'test1db')
        table = 'user'

    id = PrimaryKeyField()
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)

User.drop_table()
User.create_table()

user1 = User(username='user1', password='password1')
user2 = User(username='user2', password='password2')

# 插入
print(user1.inserted())
user1.insert()
print(user1.inserted())
user2.insert()

print('===========SPLIT==============')

# 查询
# 无条件查询:返回所有对象
users = User.search().all()
for user in users:
    print(user.username)
# 有条件查询:返回符合条件的对象
user = User.search(
    (User.username=='user1') & (User.password=='password1')
).first()
print(user.username)
# 允许排序
users = User.search(
    (User.username!='It is impossible to be the username'),
    [-User.username]
).all()
for user in users:
    print(user.username)

print('===========SPLIT==============')

# 修改
user1.username = 'editedusername'
user1.update()
users = User.search().all()
for user in users:
    print(user.username)

print('===========SPLIT==============')

# 删除
user1.delete()
users = User.search().all()
for user in users:
    print(user.username)
```
