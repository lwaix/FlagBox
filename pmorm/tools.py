import pymysql

# 返回一个pymysql.Connection对象
def Mysql(host, user, password, database):
    return pymysql.connect(host, user, password, database)

# 将值转安全转意,防止注入
def safe(value):
    # 仅仅转义str类型的值
    if isinstance(value, str):
        return pymysql.escape_string(value)
    else:
        return value

# 查询条件对象,用于拼接查询条件部分的语句(WHERE之后)
class Query:
    def __init__(self, condition):
        self.condition = '{}'.format(condition)
    
    # &&运算符拼接两个Query对象
    def __and__(self, obj):
        self.condition = '({})'.format(self.condition + ' AND ' + obj.condition)
        return self

    # ||运算符拼接两个Query对象
    def __or__(self, obj):
        self.condition = '({})'.format(self.condition + ' OR ' + obj.condition)
        return self

# 封装查询结果
class Result:
    def __init__(self, results):
        self.results = results
    
    def first(self):
        return self.results[0]

    def last(self):
        return self.results[-1]
    
    def all(self):
        return self.results
