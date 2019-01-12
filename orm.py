import pymysql

"""
Notes:
命名?
异常完善?
重构?
"""

def Mysql(host, user, password, database):
    return pymysql.connect(host, user, password, database)

def safe(content):
    if isinstance(content, str):
        return pymysql.escape_string(content)
    else:
        return content

class Query:
    def __init__(self, _type, obj, value):
        self.type = _type
        self.obj = obj
        self.value = value
    
    def _make_sentence(self):
        if self.obj._check(self.value):
            return '{}{}{}'.format(self.obj.fieldname, self.type, self.obj._add(safe(self.value)))
        else:
            raise TypeError('类型错误')

# ===Fields===
class TextField:
    def __init__(self, nullable=True, unique=False):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique

    def _make_sentence(self):
        sentence = '{} TEXT'.format(self.fieldname)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        if isinstance(value, str) or (value is None and self.nullable):
            return True
        return False
    
    def _add(self, value):
        return "'{}'".format(value)
    
    def __eq__(self, value):
        return Query('=', self, value)
    
    def __ne__(self, value):
        return Query('!=', self, value)

class VarcharField:
    def __init__(self, max_length=256, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.max_length = max_length
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_sentence(self):
        sentence = '{} VARCHAR({})'.format(self.fieldname, self.max_length)
        if self.default is not None:
            sentence += " DEFAULT '{}'".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence

    def _check(self, value):
        if isinstance(value, str) or (value is None and self.nullable):
            return True
        return False
    
    def _add(self, value):
        return "'{}'".format(value)
    
    def __eq__(self, value):
        return Query('=', self, value)
    
    def __ne__(self, value):
        return Query('!=', self, value)
        
class IntField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_sentence(self):
        sentence = '{} INT'.format(self.fieldname)
        if self.default is not None:
            sentence += " DEFAULT {}".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def _check(self, value):
        if isinstance(value, int) or (value is None and self.nullable):
            return True
        return False
    
    def _add(self, value):
        return "{}".format(value)

    def __eq__(self, value):
        return Query('=', self, value)
    
    def __ne__(self, value):
        return Query('!=', self, value)
    
    def __gt__(self, value):
        return Query('>', self, value)
    
    def __lt__(self, value):
        return Query('<', self, value)
    
    def __ge__(self, value):
        return Query('>=', self, value)

    def __le__(self, value):
        return Query('<=', self, value)

class FloatField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.fieldname = None
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def _make_sentence(self):
        sentence = '{} FLOAT'.format(self.fieldname)
        if self.default is not None:
            sentence += " DEFAULT {}".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def _check(self, value):
        if isinstance(value, float) or (value is None and self.nullable):
            return True
        return False
    
    def _add(self, value):
        return "{}".format(value)
    
    def __eq__(self, value):
        return Query('=', self, value)
    
    def __ne__(self, value):
        return Query('!=', self, value)
    
    def __gt__(self, value):
        return Query('>', self, value)
    
    def __lt__(self, value):
        return Query('<', self, value)
    
    def __ge__(self, value):
        return Query('>=', self, value)

    def __le__(self, value):
        return Query('<=', self, value)

class PrimaryKeyField():
    def __init__(self):
        self.fieldname = None
    
    def _check(self, value):
        if isinstance(value, int) or (value is None and self.nullable):
            return True
        return False
    
    def _add(self, value):
        return '{}'.format(value)
    
    def _make_sentence(self):
        return '{} INT NOT NULL AUTO_INCREMENT PRIMARY KEY'.format(self.fieldname)
    
    def __eq__(self, value):
        return Query('=', self, value)
    
    def __ne__(self, value):
        return Query('!=', self, value)
    
    def __gt__(self, value):
        return Query('>', self, value)
    
    def __lt__(self, value):
        return Query('<', self, value)
    
    def __ge__(self, value):
        return Query('>=', self, value)

    def __le__(self, value):
        return Query('<=', self, value)
        

field_types = (TextField, VarcharField, IntField, FloatField, PrimaryKeyField)
# ============

class Base:
    class Meta:
        db = None
        table = None

    _init_sign = False
    _fields = {}

    # 接收值,如果属于某字段就__setattr__
    def __init__(self, **kwargs):
        self.__class__._init()
        # 靠id来判断该对象是否已经被插入进数据库了,如果为None则还未被插入
        fields = self.__class__._get_fields()
        fieldnames = fields.keys()
        # 检查是否有未知的参数
        for key in kwargs.keys():
            if key not in fieldnames:
                raise Exception('未知的参数{}'.format(key))
        for key,value in fields.items():
            self.__setattr__(key,kwargs.get(key))

    # 将字段名插入field字段里面
    @classmethod
    def _init(cla):
        if not cla._init_sign:
            for key,value in cla.__dict__.items():
                if isinstance(value, field_types):
                    cla._fields[key] = value
            fields = cla._get_fields()
            for key,value in fields.items():
                value.fieldname = key
            cla._init_sign = True

    # 识别所有field类变量
    @classmethod
    def _get_fields(cla):
        return cla._fields
    
    def _get_current_data(self):
        fields = self.__class__._get_fields()
        res = {}
        for fieldname in fields.keys():
            value = self.__getattribute__(fieldname)
            # 防止被类变量覆盖
            if not isinstance(value,field_types):
                res[fieldname] = self.__getattribute__(fieldname)
            else:
                res[fieldname] = None
        return res

    @classmethod
    def create_table(cla):
        cla._init()
        db = cla.Meta.db
        table = cla.Meta.table
        cursor = db.cursor()

        fields = cla._get_fields()

        field_sentences = []
        for key,value in fields.items():
            field_sentences.append(value._make_sentence())
        
        field_str = ','.join(field_sentences)

        sentence = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table, field_str)
        cursor.execute(sentence)
    
    @classmethod
    def drop_table(cla):
        cla._init()
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()

        sentence = 'DROP TABLE IF EXISTS {}'.format(table)
        cursor.execute(sentence)
    
    def insert(self):
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()
        data = self._get_current_data()
        fields = self.__class__._get_fields()


        fieldnames = []
        values = []
        # 类型检查
        for key,value in fields.items():
            if key == 'id':
                continue
            if value._check(data.get(key)):
                fieldnames.append(key)
                values.append(value._add((safe((data.get(key))))))
            else:
                raise TypeError('类型不匹配')
        fieldnames_str = ','.join(fieldnames)
        values_str = ','.join(values)
        sentence = 'INSERT INTO {} ({}) VALUES({})'.format(table, fieldnames_str, values_str)
        cursor.execute(sentence)
        db.commit()
    
    @classmethod
    def search(cla, *querys):
        cla._init()
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()
        fieldnames = cla._get_fields().keys()
        
        conditions = []

        temp1 = ','.join(fieldnames)
        for query in querys:
            conditions.append(query._make_sentence())
        temp2 = ' and '.join(conditions)
        if querys:
            sentence = 'SELECT {} FROM {} WHERE {}'.format(temp1, table, temp2)
        else:
            sentence = 'SELECT {} FROM {}'.format(temp1, table, temp2)
        if cursor.execute(sentence) == 0:
            return []
        all_data = cursor.fetchall()
        res = []
        for one in all_data:
            one = list(one)
            obj = cla()
            index = 0
            while index <= len(fieldnames)-1:
                obj.__setattr__(list(fieldnames)[index], one[index])
                index += 1
            res.append(obj)
        return res
    
    def update(self):
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()
        if self.id == None:
            raise Exception('该对象不可更新')
        fields = self.__class__._get_fields()
        current_data = self._get_current_data()
        sets = []
        for field in fields.values():
            value = current_data.get(field.fieldname)
            if not field._check(value):
                raise TypeError('类型错误')
            sets.append('{}={}'.format(field.fieldname,field._add(safe(value))))
        temp = ','.join(sets)
        sentence = 'UPDATE {} SET {} WHERE id={}'.format(table, temp, str(self.id))
        cursor.execute(sentence)
        db.commit()
    
    def delete(self):
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()

        if self.id == None:
            raise Exception('此对象不可删除')
        
        sentence = 'DELETE FROM {} WHERE id={}'.format(table, self.id)
        cursor.execute(sentence)
        db.commit()