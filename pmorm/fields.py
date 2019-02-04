from .tools import safe, Query

# 对应Mysql的TEXT字段
class TextField:
    def __init__(self, nullable=True, unique=False):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique

    # 每个字段都实现这个方法:返回这个字段的单独建表语句比如username VARCHAR(255) NOT NULL UNIQUE
    def _make_element(self):
        sentence = '{} TEXT'.format(self.fieldname)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    # 每个字段都实现这个方法:检查值是否符合要求
    def _check(self, value):
        # 当类型匹配或值为None且nullable为True时返回True
        if isinstance(value, str) or (value is None and self.nullable):
            return True
        return False
    
    # 每个字段都实现这个方法:获取这个字段值的表达方式比如INT:1,FLOAT:1.0,而TEXT,VARCHAR:'1',并将值安全转义
    def _value(self, value):
        if value is not None:
            return "'{}'".format(safe(value))
        else:
            return 'NULL'

    # ==运算符比较,返回一个Query对象
    def __eq__(self, value):
        if value is None:
            return Query('{} IS NULL'.format(self.fieldname))
        return Query('{}={}'.format(self.fieldname, self._value(value)))

    # !=
    def __ne__(self, value):
        if value is None:
            return Query('{} IS NOT NULL'.format(self.fieldname))
        return Query('{}!={}'.format(self.fieldname, self._value(value)))

    # +:用于search降序排列
    def __pos__(self):
        return '{}'.format(self.fieldname)

    # -:用于search升序排列
    def __neg__(self):
        return '{} DESC'.format(self.fieldname)

# 对于Mysql字段VARCHAR
class VarcharField:
    def __init__(self, max_length=256, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.max_length = max_length
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '{} VARCHAR({})'.format(self.fieldname, self.max_length)
        if self.default is not None:
            sentence += " DEFAULT '{}'".format(safe(self.default))
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        if isinstance(value, str) or (value is None and self.nullable):
            return True
        return False
    
    def _value(self, value):
        if value is not None:
            return "'{}'".format(safe(value))
        else:
            return 'NULL'
    
    def __eq__(self, value):
        if value is None:
            return Query('{} IS NULL'.format(self.fieldname))
        return Query('{}={}'.format(self.fieldname, self._value(value)))
    
    def __ne__(self, value):
        if value is None:
            return Query('{} IS NOT NULL'.format(self.fieldname))
        return Query('{}!={}'.format(self.fieldname, self._value(value)))
    
    def __pos__(self):
        return '{}'.format(self.fieldname)

    def __neg__(self):
        return '{} DESC'.format(self.fieldname)

# 对应Mysql字段INT
class IntField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '{} INT'.format(self.fieldname)
        if self.default is not None:
            sentence += " DEFAULT {}".format(safe(self.default))
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def _check(self, value):
        if isinstance(value, int) or (value is None and self.nullable):
            return True
        return False
    
    def _value(self, value):
        if value is not None:
            return "{}".format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('{} IS NULL'.format(self.fieldname))
        return Query('{}={}'.format(self.fieldname, self._value(value)))
    
    def __ne__(self, value):
        if value is None:
            return Query('{} IS NOT NULL'.format(self.fieldname))
        return Query('{}!={}'.format(self.fieldname, self._value(value)))
    
    def __gt__(self, value):
        return Query('{}>{}'.format(self.fieldname, self._value(value)))
    
    def __lt__(self, value):
        return Query('{}<{}'.format(self.fieldname, self._value(value)))
    
    def __ge__(self, value):
        return Query('{}>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('{}<={}'.format(self.fieldname, self._value(value)))

    def __pos__(self):
        return '{}'.format(self.fieldname)

    def __neg__(self):
        return '{} DESC'.format(self.fieldname)

# 对应Mysql字段FLOAT
class FloatField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '{} FLOAT'.format(self.fieldname)
        if self.default is not None:
            sentence += " DEFAULT {}".format(safe(self.default))
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def _check(self, value):
        # FLOAT同样支持INT
        if isinstance(value, (float, int)) or (value is None and self.nullable):
            return True
        return False
    
    def _value(self, value):
        if value is not None:
            return "{}".format(safe(value))
        else:
            return 'NULL'
    
    def __eq__(self, value):
        if value is None:
            return Query('{} IS NULL'.format(self.fieldname))
        return Query('{}={}'.format(self.fieldname, self._value(value)))
    
    def __ne__(self, value):
        if value is None:
            return Query('{} IS NOT NULL'.format(self.fieldname))
        return Query('{}!={}'.format(self.fieldname, self._value(value)))
    
    def __gt__(self, value):
        return Query('{}>{}'.format(self.fieldname, self._value(value)))
    
    def __lt__(self, value):
        return Query('{}<{}'.format(self.fieldname, self._value(value)))
    
    def __ge__(self, value):
        return Query('{}>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('{}<={}'.format(self.fieldname, self._value(value)))

    def __pos__(self):
        return '{}'.format(self.fieldname)

    def __neg__(self):
        return '{} DESC'.format(self.fieldname)

# id字段,是这个orm得以正常运作的前提,每个Model都必须包含这个字段: id = PrimaryKeyField()
class PrimaryKeyField():
    def __init__(self):
        self.fieldname = 'id'
    
    def _check(self, value):
        if isinstance(value, int) or value is None:
            return True
        return False
    
    def _value(self, value):
        if value is not None:
            return "{}".format(safe(value))
        else:
            return 'NULL'
    
    def _make_element(self):
        return '{} INT NOT NULL AUTO_INCREMENT PRIMARY KEY'.format(self.fieldname)
    
    def __eq__(self, value):
        if value is None:
            return Query('{} IS NULL'.format(self.fieldname))
        return Query('{}={}'.format(self.fieldname, self._value(value)))
    
    def __ne__(self, value):
        if value is None:
            return Query('{} IS NOT NULL'.format(self.fieldname))
        return Query('{}!={}'.format(self.fieldname, self._value(value)))
    
    def __gt__(self, value):
        return Query('{}>{}'.format(self.fieldname, self._value(value)))
    
    def __lt__(self, value):
        return Query('{}<{}'.format(self.fieldname, self._value(value)))
    
    def __ge__(self, value):
        return Query('{}>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('{}<={}'.format(self.fieldname, self._value(value)))

    def __pos__(self):
        return '{}'.format(self.fieldname)

    def __neg__(self):
        return '{} DESC'.format(self.fieldname)

field_types = (TextField, VarcharField, IntField, FloatField, PrimaryKeyField)
defaultable = (VarcharField, IntField, FloatField)