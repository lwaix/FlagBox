import pymysql

VERSION = '0.17'

"""
TODO:
    - 优化代码
    - 完善单测
"""

class Mysql:
    def __init__(self, host, user, password, database, port=3306, charset=''):
        conn = pymysql.connect(host=host, user=user, password=password, database=database, port=port, charset=charset, autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        class MysqlModel:
            __db__ = conn
            __table__ = None

            # 在每个操作里面都检查是否init,仅仅执行一次_init()方法
            _init_sign = False

            # 初始化该Model,将字段名写入_fields,将字段名写入对应字段对象,并标记已初始化,只初始化一次
            @classmethod
            def _init(cla):
                # 检查是否已初始化
                if not cla._init_sign:
                    cla._fields_dict = dict()
                    id_sign = False
                    for key, value in cla.__dict__.items():
                        # 检查是否定义了id字段
                        if not id_sign :
                            if key == 'id' and isinstance(value, PrimaryKeyField):
                                id_sign = True
                        # 如果类对象属于Fields,那么说明它就是被定义在Model中的字段,将它写入_fields
                        # _fields的格式:{fieldname1:field_obj1, fieldname2:field_obj2,...}
                        if isinstance(value, Field):
                            # field对象也包含fieldname,需要赋值给它已保证其正常工作
                            value.fieldname = key
                            cla._fields_dict[key] = value
                    if not id_sign:
                        raise AttributeError('未定义的字段:id')
                    # 标记已经初始化
                    cla._init_sign = True

            # 获取_fields
            @classmethod
            def _get_fields_dict(cla):
                return cla._fields_dict

            # 获取当前对象的数据
            def _get_current_data(self):
                fieldnames = self.__class__._get_fields_dict().keys()
                result = dict()
                for fieldname in fieldnames:
                    # __init__时即使未赋值的字段也自动赋值为None了,所以不用担心访问到Field对象
                    result[fieldname] = self.__getattribute__(fieldname)
                return result

            # 如果对象已被插入则返回True
            def inserted(self):
                # 检查id是否通过检查 检查id是否为None
                if self.__class__._get_fields_dict().get('id')._check(self.id) and self.id is None:
                    return False
                return True

            # 接收本对象的各个字段值,没有赋值的默认为None
            def __init__(self, **kwargs):
                self.__class__._init()
                fields_dict = self.__class__._get_fields_dict()
                fieldnames = fields_dict.keys()
                fields = fields_dict.values()
                keys = kwargs.keys()

                # 检查未知的参数
                for key in keys:
                    if key not in fieldnames:
                        raise ValueError('未知的参数:{}'.format(key))

                # 设置对象的值
                for fieldname in fieldnames:
                    self.__setattr__(fieldname, kwargs.get(fieldname, None))

                # 定义了default的字段但没有赋值的,给它赋上默认值
                for field in fields:
                    if isinstance(field, DefaultAbleField):
                        if field.default is not None and self.__getattribute__(field.fieldname) is None:
                            self.__setattr__(field.fieldname,field.default)

            # 建表操作
            @classmethod
            def create_table(cla):
                cla._init()
                db = cla.__db__
                table = cla.__table__
                cursor = db.cursor()
                fields = cla._get_fields_dict().values()

                field_elements = list()
                for field in fields:
                    field_elements.append(field._make_element())

                sentence = 'CREATE TABLE IF NOT EXISTS `{}` ({})'.format(table, ','.join(field_elements))
                cursor.execute(sentence)
                cursor.close()

            # 删表操作
            @classmethod
            def drop_table(cla):
                cla._init()
                table = cla.__table__
                cursor = cla.__db__.cursor()

                sentence = 'DROP TABLE IF EXISTS `{}`'.format(table)
                cursor.execute(sentence)
                cursor.close()

            # 插入操作
            def insert(self):
                self.__class__._init()

                # 被插入过的对象无法被重复插入
                if self.inserted():
                    raise RuntimeError('该对象已被插入,不可重复插入')

                db = self.__class__.__db__
                table = self.__class__.__table__
                cursor = db.cursor()
                current_data = self._get_current_data()
                fields = self.__class__._get_fields_dict().values()
                fieldnames = list()
                values = list()

                # 类型检查并获取字段名与值
                for field in fields:
                    fieldname = field.fieldname
                    if field._check(current_data.get(fieldname)):
                        # id不需要插入 值为None的也不需要插入(所有字段没设置DEFAULT的默认都为NULL)
                        if fieldname == 'id' or current_data.get(fieldname) is None:
                            continue
                        fieldnames.append('`{}`'.format(fieldname))
                        values.append(field._value(((current_data.get(fieldname)))))
                    else:
                        raise ValueError('值{}与字段{}不匹配,可能原因:\n1.类型不匹配\n2.该值不能为None'.format(current_data.get(fieldname), field.fieldname))

                sentence = 'INSERT INTO `{}` ({}) VALUES({})'.format(table, ','.join(fieldnames), ','.join(values))
                cursor.execute(sentence)
                cursor.close()

                # 标记该对象id
                self.id = cursor.lastrowid

            # 返回Result对象
            @classmethod
            def search(cla, query=None, orders=None):
                cla._init()
                db = cla.__db__
                # cla用于封装模型,query是查询条件,orders用于排序
                return Result(db, cla, query, orders)

            # 更新该对象
            def update(self):
                self.__class__._init()
                # 没有被插入的对象无法更新
                if not self.inserted():
                    raise RuntimeError('该对象不可更新')
                db = self.__class__.__db__
                table = self.__class__.__table__
                cursor = db.cursor()
                fields = self.__class__._get_fields_dict().values()
                current_data = self._get_current_data()

                set_elements = list()
                for field in fields:
                    fieldname = field.fieldname
                    if fieldname == 'id':
                        continue
                    value = current_data.get(fieldname)
                    if not field._check(value):
                        raise ValueError('值{}与字段{}不匹配,可能原因:\n1.类型不匹配\n2.该值不能为None'.format(value, fieldname))
                    set_elements.append('`{}`={}'.format(field.fieldname,field._value(value)))
                sentence = 'UPDATE `{}` SET {} WHERE `id`={}'.format(table, ','.join(set_elements), self.id)
                cursor.execute(sentence)
                cursor.close()

            # 删除该对象
            def delete(self):
                self.__class__._init()

                # 没被插入的无法被删除
                if not self.inserted():
                    raise RuntimeError('该对象不可删除')

                db = self.__class__.__db__
                table = self.__class__.__table__
                cursor = db.cursor()

                sentence = 'DELETE FROM `{}` WHERE `id`={}'.format(table, self.id)
                cursor.execute(sentence)
                cursor.close()
                self.id = None
        self.Model = MysqlModel

# 将字符串值转安全转意(返回值不包含''符号),防注入
def safe(value):
    # 仅转str
    if isinstance(value, str):
        return pymysql.escape_string(value)
    else:
        return value

# 查询条件对象,拼接查询条件部分(WHERE之后)的语句
class Query:
    def __init__(self, condition):
        self.condition = '{}'.format(condition)

    # &运算符拼接两个Query对象
    def __and__(self, obj):
        self.condition = '({})'.format(self.condition + ' AND ' + obj.condition)
        return self

    # |运算符拼接两个Query对象
    def __or__(self, obj):
        self.condition = '({})'.format(self.condition + ' OR ' + obj.condition)
        return self

# DESC排序类
class DescOrder:
    def __init__(self, fieldname):
        self.order = '`{}` DESC'.format(fieldname)

    def _get_order(self):
        return self.order

# 查询结果类
class Result:
    def __init__(self, db, model, query, orders):
        table = model.__table__
        if query is None:
            sentence = 'SELECT * FROM `{}`'.format(table)
        else:
            sentence = 'SELECT * FROM `{}` WHERE {}'.format(table, query.condition)
        if orders is not None:
            orders_list = list()
            for order in orders:
                # 可以传过来的是字段类型,也可以是+,-处理过的Field或DescOrder类型,都可用_get_order()获取
                orders_list.append(order._get_order())
            sentence = '{} ORDER BY {}'.format(sentence, ','.join(orders_list))
        self.db = db
        self.model = model
        self.sentence = sentence
        self.fields_dict = model._get_fields_dict()

    def all(self, limit=None):
        db = self.db
        model = self.model
        sentence = self.sentence
        fields_dict = self.fields_dict

        if limit is not None:
            sentence = '{} LIMIT {},{}'.format(self.sentence, limit[0], limit[1])

        cursor = db.cursor()
        cursor.execute(sentence)
        rows = cursor.fetchall()
        cursor.close()

        objs = list()
        for row in rows:
            obj = model()
            for key, value in row.items():
                if isinstance(fields_dict.get(key) , BooleanField) and value is not None:
                    obj.__setattr__(key, bool(value))
                else:
                    obj.__setattr__(key, value)
            objs.append(obj)
        return objs

    def first(self):
        db = self.db
        model = self.model
        sentence = '{} LIMIT 1'.format(self.sentence)
        fields_dict = self.fields_dict

        cursor = db.cursor()
        cursor.execute(sentence)
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            obj = None
        else:
            obj = model()
            for key,value in row.items():
                if isinstance(fields_dict.get(key), BooleanField) and value is not None:
                    obj.__setattr__(key, bool(value))
                else:
                    obj.__setattr__(key, value)
        return obj

# ===Fields===
# 这是所有字段类型的父类,里面包含一个字段必须的元素
class Field:
    def __init__(self):
        self.fieldname = None

    def _make_element(self):
        pass

    def _check(self):
        pass

    def _value(self):
        pass

    """
    运算符中==,!=,+,-是必须的,但是可与定义其他的,例如>=,<=
    """

    # ==
    def __eq__(self, value):
        pass

    # !=
    def __ne__(self, value):
        pass

    # +
    def __pos__(self):
        return self

    # -
    def __neg__(self):
        return DescOrder(self.fieldname)

    def _get_order(self):
        return '`{}`'.format(self.fieldname)

class DefaultAbleField(Field):
    pass

class UnDefaultAbleField(Field):
    pass

# 对应Mysql字段VARCHAR
class VarcharField(DefaultAbleField):
    def __init__(self, max_length=255, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.max_length = max_length
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '`{}` VARCHAR({})'.format(self.fieldname, self.max_length)
        if self.default is not None:
            sentence += ' DEFAULT "{}"'.format(safe(self.default))
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
            return '"{}"'.format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

# 对应Mysql的TEXT字段
class TextField(UnDefaultAbleField):
    def __init__(self, nullable=True, unique=False):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique

    # 每个字段都实现这个方法:返回这个字段的单独建表语句比如username VARCHAR(255) NOT NULL UNIQUE
    def _make_element(self):
        sentence = '`{}` TEXT'.format(self.fieldname)
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
            return '"{}"'.format(safe(value))
        else:
            return 'NULL'

    # ==运算符比较,返回一个Query对象
    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    # !=
    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

# 对应Mysql的用TINYINT实现的BOOLEAN字段
class BooleanField(DefaultAbleField):
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '`{}` TINYINT'.format(self.fieldname)
        if self.default is not None:
            sentence += ' DEFAULT {}'.format(safe(int(self.default)))
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        if isinstance(value, bool) or (value is None and self.nullable):
            return True
        return False

    def _value(self, value):
        if value is not None:
            return '{}'.format(safe(int(value)))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

# 对应Mysql字段INT
class IntField(DefaultAbleField):
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '`{}` INT'.format(self.fieldname)
        if self.default is not None:
            sentence += ' DEFAULT {}'.format(safe(self.default))
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
            return '{}'.format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

    def __gt__(self, value):
        return Query('`{}`>{}'.format(self.fieldname, self._value(value)))

    def __lt__(self, value):
        return Query('`{}`<{}'.format(self.fieldname, self._value(value)))

    def __ge__(self, value):
        return Query('`{}`>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('`{}`<={}'.format(self.fieldname, self._value(value)))

# 对应Mysql字段BIGINT
class BigIntField(DefaultAbleField):
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '`{}` BIGINT'.format(self.fieldname)
        if self.default is not None:
            sentence += ' DEFAULT {}'.format(safe(self.default))
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
            return '{}'.format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

    def __gt__(self, value):
        return Query('`{}`>{}'.format(self.fieldname, self._value(value)))

    def __lt__(self, value):
        return Query('`{}`<{}'.format(self.fieldname, self._value(value)))

    def __ge__(self, value):
        return Query('`{}`>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('`{}`<={}'.format(self.fieldname, self._value(value)))

# 对应Mysql字段FLOAT
class FloatField(DefaultAbleField):
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '`{}` FLOAT'.format(self.fieldname)
        if self.default is not None:
            sentence += ' DEFAULT {}'.format(safe(self.default))
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        # FLOAT同样支持int值
        if isinstance(value, (float, int)) or (value is None and self.nullable):
            return True
        return False

    def _value(self, value):
        if value is not None:
            return '{}'.format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

    def __gt__(self, value):
        return Query('`{}`>{}'.format(self.fieldname, self._value(value)))

    def __lt__(self, value):
        return Query('`{}`<{}'.format(self.fieldname, self._value(value)))

    def __ge__(self, value):
        return Query('`{}`>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('`{}`<={}'.format(self.fieldname, self._value(value)))

# 对应Mysql字段DOUBLE
class DoubleField(DefaultAbleField):
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_element(self):
        sentence = '`{}` DOUBLE'.format(self.fieldname)
        if self.default is not None:
            sentence += ' DEFAULT {}'.format(safe(self.default))
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        # DOUBLE同样支持int值
        if isinstance(value, (float, int)) or (value is None and self.nullable):
            return True
        return False

    def _value(self, value):
        if value is not None:
            return '{}'.format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

    def __gt__(self, value):
        return Query('`{}`>{}'.format(self.fieldname, self._value(value)))

    def __lt__(self, value):
        return Query('`{}`<{}'.format(self.fieldname, self._value(value)))

    def __ge__(self, value):
        return Query('`{}`>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('`{}`<={}'.format(self.fieldname, self._value(value)))

# id字段,是这个orm得以正常运作的前提,每个Model都必须包含这个字段: id = PrimaryKeyField()
class PrimaryKeyField(UnDefaultAbleField):
    def __init__(self):
        self.fieldname = 'id'
    
    def _make_element(self):
        return '`{}` INT NOT NULL AUTO_INCREMENT PRIMARY KEY'.format(self.fieldname)

    def _check(self, value):
        if isinstance(value, int) or value is None:
            return True
        return False

    def _value(self, value):
        if value is not None:
            return '{}'.format(safe(value))
        else:
            return 'NULL'

    def __eq__(self, value):
        if value is None:
            return Query('`{}` IS NULL'.format(self.fieldname))
        return Query('`{}`={}'.format(self.fieldname, self._value(value)))

    def __ne__(self, value):
        if value is None:
            return Query('`{}` IS NOT NULL'.format(self.fieldname))
        return Query('`{}`!={}'.format(self.fieldname, self._value(value)))

    def __gt__(self, value):
        return Query('`{}`>{}'.format(self.fieldname, self._value(value)))

    def __lt__(self, value):
        return Query('`{}`<{}'.format(self.fieldname, self._value(value)))

    def __ge__(self, value):
        return Query('`{}`>={}'.format(self.fieldname, self._value(value)))

    def __le__(self, value):
        return Query('`{}`<={}'.format(self.fieldname, self._value(value)))
