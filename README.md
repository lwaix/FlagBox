### 支持版本:python3

#### 基本使用

```
from orm import *

class User(Base):
    class Meta:
        # 连接数据库,连接前要手动创建数据库
        db = Mysql(host='localhost', user='root', password='your-password', database='your-database')
        # 表名
        table = 'user'
    # id字段,每个模型都必须定义此字段,才得以正常工作
    id = PrimaryKeyField()
    # 定义字段,字段名是定义的变量名称
    # 支持的字段类型:VARCHAR,Text,Int,Float
    username = VarcharField(max_length=32,nullable=False,unique=True)
    password = VarcharField(max_length=64, nullable=False, unique=False)
    comment = TextField(nullable=True, unique=False)
    salary = FloatField(nullable=False, unique=False, default=0.0)

# 如果表不存在就建表,会自动为你创建一个自增的id字段(数据库的删除查询修改都要依赖它)
User.create_table()
# 删表语句User.drop_table()

# 增
user1 = User(username='xuri', password='pass', salary=3000.0)
user1.insert()

user2 = User(username='xuri2', password='pass2', salary=80000.5)
user2.insert()

# 查
# 查询支持Query语句,IntField和FloatField支持>,<,>=,<=,==,!= StringField支持==,!=
# 注意:不能查询id,如果要根据id查询,使用User.get_by_id(id)
user = User.search(User.username == 'xuri2')[0]
print(user.id, user.username, user.password, user.salary)

# 删
user = User.search(User.username == 'xuri')[0]
user.delete()

# 改
user = User.search(User.username == 'xuri2')[0]
user.username = 'xuri2edit'
user.update()
```