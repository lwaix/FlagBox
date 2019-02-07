# pmorm.py - 简约的Python3 Mysql ORM

## 安装

```
shell>git clone https://github.com/lwaix/Pmorm.git
shell>cd .\Pmorm\
shell>python3 .\setup.py install --user
```

## 使用教程

### 使用前

#### 为程序创建数据库

```
mysql>CREATE DATABASE testdb;
```

### 快速开始

##### 建立Mysql连接

```python
from pmorm import Mysql

mydb = Mysql('localhost', 'root', 'your-passwd', 'testdb')
```

#### 编写模型并建表

```python
from pmorm import Base, PrimaryKeyField, VarcharField

# 定义模型类User
class User(Base):
    # 内置类Meta被用来配置数据库与表名
    class Meta:
        db = mydb
        table = 'user'

    # 编写模型的字段
    id = PrimaryKeyField()  # id字段是必须的
    username = VarcharField(max_length=32, nullable=False, unique=True, default=None)
    password = VarcharField(max_length=64, nullable=False, unique=False, default=None)

# 如果表未被创建,则创建该表
User.create_table()
```

#### 插入

```python
# 简单插入
user1 = User(username='user1', password='passwd1')
user1.insert()

# 也可以这样
user2 = User()
user2.username = 'user2'
user2.password = 'passwd2'
user2.insert()

# 插入前可修改
user3 = User(username='userx')
user3.username = 'user3'
user3.password = 'passwd3'
user3.insert()

# inserted() 方法检查对象是否被插入(被插入的对象无法被重复插入)
print(user1.inserted()) # True
```

#### 搜索

```python
# 获取所有内容并逐个遍历
users = User.search().all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

# 条件查询
users = User.search(User.username != 'unkonw').all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))

# 组合条件查询(利用|和&运算符)
user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

# 将搜索结果根据字段排序
users = User.search(
    (User.username!='user1') | (User.password!='passwd1'),
    orders=[User.id] # 按id倒叙排列
).all()
for user in users:
    print("id:{} username:{} password:{}".format(user.id, user.username, user.password))
```

##### 注意: search()方法返回一个 Result 对象, 可以使用它的方法 all() 获取所有对象(返回list), 与 first() 得到第一个

#### 更新

```python
# 首先获取对象
user1 = User.search(
    ((User.username=='user1') | (User.password=='passwd1') & (User.id==1)) # 复杂查询
).first()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))

# 修改并提交
user1.username = 'edit'
user1.update()
print("id:{} username:{} password:{}".format(user1.id, user1.username, user1.password))
```

#### 删除

```python
# 首先获取对象
user1 = User.search(User.username=='edit').first()
# 删除
user1.delete()
```

---

### 关于 Mysql() 函数

#### Mysql() 函数代码

```python
def Mysql(*args, **kwargs):
    return pymysql.connect(*args, **kwargs)
```

#### Mysql() 函数实际是 pymysql.connect() 函数的封装,它的更多的参数,请参见pymysql文档

### 目前支持的字段类型

Pmorm|Mysql
--|:--:
PrimaryKeyField|无
IntField|INT
FloatField|FLOAT
VarcharField|VARCHAR
TextField|TEXT

#### 其中 PrimaryKeyField 是每个模型必须定义的,也是Pmorm工作的前提,所以一个基本的模型定义看起来像这样

```python
mydb = Mysql('localhost', 'root', 'your-passwd', 'your-database')
class ModelName(Base):
    class Meta:
        db = mydb
        table = 'mytable'
    id = PrimaryKeyField()
    # 其他字段...
```
