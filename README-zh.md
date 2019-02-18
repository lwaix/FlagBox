# pmorm.py - 简约的Python3 Mysql ORM

![py35][py35]

#### 功能概述

- 面向模型操作
- 基本增删查改
- Query查询
- 自动安全转义

## 安装

```
shell>pip install Pmorm
```

## 使用教程

### 使用前为程序创建数据库

```
mysql>CREATE DATABASE testdb;
```

### 快速开始

---

#### 建立Mysql连接

```python
from pmorm import Mysql

mydb = Mysql('localhost', 'root', 'your-passwd', 'testdb')
```

---

#### 编写模型并建表

```python
from pmorm import Base, PrimaryKeyField, VarcharField, DoubleField

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
    balance = DoubleField(nullable=False, unique=True, default=0.0)

# 如果表未被创建,则创建该表
User.create_table()
```

---

#### 插入

```python
# 简单插入
user1 = User(username='user1', password='passwd1')
user1.insert()

# 这样也行
user2 = User()
user2.username = 'user2'
user2.password = 'passwd2'
user2.insert()

# 插入前可修改
user3 = User(username='userx')
user3.username = 'user3'
user3.password = 'passwd3'
user3.insert()

# 检查对象是否被插入
print(user1.inserted()) # True
```

---

#### 搜索

##### 获取所有用户

```python
users = User.search().all()

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

##### 根据条件筛选

```python
users = User.search(User.username != 'unkonwn').all()

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

##### 组合条件筛选

```python
# 利用 | 和 & 运算符组合条件
user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).first()

"""
# 下面代码与上面代码结果相同
# 但不同点是用first()方法获取第一个元素更快

user1 = User.search(
    (User.username=='user1') & (User.password=='passwd1')
).all()[0]
"""

print("id:{} username:{} password:{} balance:{}".format(user1.id, user1.username, user1.password, user1.balance))
```

##### 排序查询结果

```python
users = User.search(
    (User.username!='user1') | (User.password!='passwd1'),
    orders=[-User.id] # 按id倒叙排列
).all()

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

##### 使用limit

```python
users = User.search(User.username!='unknown').all(limit=(0,2)) # 限制只返回查询结果前两个,相当于"LIMIT 0, 2"

for user in users:
    print("id:{} username:{} password:{} balance:{}".format(user.id, user.username, user.password, user.balance))
```

---

#### 更新

```python
# 首先获取对象
user1 = User.search(
    ((User.username=='user1') | (User.password=='passwd1') & (User.id==1)) # 复杂查询
).first()
print("id:{} username:{} password:{} balance:{}".format(user1.id, user1.username, user1.password, user1.balance))

# 修改并提交
user1.username = 'edit'
user1.update()
print("id:{} username:{} password:{} balance:{}".format(user1.id, user1.username, user1.password, user1.balance))
```

---

#### 删除

```python
# 首先获取对象
user1 = User.search(User.username=='edit').first()
# 删除
user1.delete()
```

---

## 其他

### 目前支持的字段类型

Pmorm|Mysql
--|:--:
PrimaryKeyField|无
BooleanField|BOOLEAN
IntField|INT
BigIntField|BIGINT
FloatField|FLOAT
DoubleField|DOUBLE
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