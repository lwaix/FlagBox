from orm import *

class User(Base):
    class Meta:
        db = Mysql(host='localhost', user='root', password='xuri', database='testdb')
        table = 'user'
    username = StringField(unique=True)
    password = StringField()
    salary = FloatField()

User.drop_table()
User.create_table()

# 增
user1 = User(username='xuri', password='pass', salary=3000.0)
user1.insert()

user2 = User(username='xuri2', password='pass2', salary=80000.5)
user2.insert()

# 删
user = User.search(User.username == 'xuri')[0]
user.delete()

# 查
user = User.search(User.username == 'xuri2')[0]
print(user.id, user.username, user.password, user.salary)

# 改
user = User.search(User.username == 'xuri2')[0]
user.username = 'xuri2edit'
user.update()