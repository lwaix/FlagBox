# pmorm.py - 简约的Python3 Mysql ORM

![](https://img.shields.io/badge/python-3.5-red.svg)

![](https://img.shields.io/badge/license-MIT-green.svg)

功能概述

- 面向模型操作
- 基本增删查改
- 运算符式查询
- 自动安全转义
- 死锁自动重试

## 安装

```
shell>pip install Pmorm
```

## 基本使用

```python
from pmorm import Mysql

# 建立连接,如数据库未创建则自动创建
db = Mysql('localhost', 'root', 'your-password', 'testdb1')

class Worker(db.Model):
    __table__ = 'worker'

    id = db.PrimaryKeyField()
    username = db.VarcharField(max_length=32, nullable=False, unique=True, default=None, comment="工人的用户名")
    password = db.VarcharField(max_length=32, nullable=False, unique=False, default=None, comment="工人的密码")
    salary = db.FloatField(nullable=False, unique=False, default=0.0, comment="工人的月薪")

Worker.create_table()

# 插入数据,支持以下两种方式
jack = Worker(username='Jack', password='JackSoHandsome', salary=3999.2)
jack.insert()

mary = Worker()
mary.username = 'Mary'
mary.password = 'MarySoBeautiful'
mary.insert()

# 查询数据
all_workers = Worker.select().all()
the_first_worker = Worker.select().first()

# 支持运算符查询
rich_workers = Worker.select(Worker.salary>=3000.0).all()

# 利用&和|运算符完成更复杂的查询
worker_jack = Worker.select(
	((Worker.username == 'jack') & (Worker.password == 'JackSoHandsome')) | (Worker.salary=='3999.2')
).first()

# 支持查询结果排序
the_richest_worker = Worker.select(orders=[-Worker.salary]).first()

# 使用查询的数据
for worker in all_workers:
	print('username:{} password:{} salary:{}'.format(worker.username, worker.password, worker.salary))
print('And the richest worker is {}'.format(the_richest_worker.username))

# 更新数据
worker_jack.salary = 3000.0
worker_jack.update()

# 移除数据
worker_jack.delete()
```

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

其中 PrimaryKeyField 是每个模型必须定义的,也是Pmorm工作的前提,所以一个基本的模型定义看起来像这样

```python
mydb = Mysql('localhost', 'root', 'your-passwd', 'your-database')
class ModelName(mydb.Model):
    __table__ = 'mytable'

    id = mydb.PrimaryKeyField()
    # 其他字段...
```