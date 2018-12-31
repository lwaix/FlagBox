import pymysql

"""
LIKE THIS:

class User(Base):
    class Meta:
        db = Mysql(host='127.0.0.1', port=3306, user='root', password='xuri')
        table = 'user'
    username = StringField()
    password = StringField()

user1 = User(username='userxuri', password='xuripass')
user1.insert()

user2 = User(username='userxuri2', password='xuripass2')
xuri2.username = 'userxuri2'
xuri2.insert()

users = User.select(User.username == 'xuri')
"""

"""
如果string类型为空?
是否检查nullable?
"""

def Mysql(host, user, password, database):
    return pymysql.connect(host, user, password, database)

# ===Fields===
class StringField:
    def __init__(self, max_length=256, nullable=True, unique=False, default=None):
        self.max_length = max_length
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def make_sentence(self, fieldname):
        sentence = '{} VARCHAR({})'.format(fieldname, self.max_length)
        if self.default != None:
            sentence += " DEFAULT '{}'".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    def check(self, value):
        if isinstance(value, str) or value == None:
            return True
        return False
    
    def add(self, value):
        return "'{}'".format(value)
        
class IntField:
    def __init__(self, nullable=True, unique=False, default=None):
        self.nullable = nullable
        self.unique = unique
        self.default = default

    def make_sentence(self, fieldname):
        sentence = '{} INT'.format(fieldname)
        if self.default != None:
            sentence += " DEFAULT {}".format(self.default)
        if not self.nullable:
            sentence += ' NOT NULL'
        if self.unique:
            sentence += ' UNIQUE'
        return sentence
    
    def check(self, value):
        if isinstance(value, int) or value == None:
            return True
        return False

class FloatField:
    pass

field_types = (StringField, IntField, FloatField)
# ============

class Base:
    class Meta:
        db = None
        table = None

    # 接收值,如果属于某字段就__setattr__
    def __init__(self, **kwargs):
        # 靠id来判断该对象是否已经被插入进数据库了,如果为0则还未被插入
        self.id = 0
        fields = self._get_fields()
        for name in kwargs.keys():
            if name not in fields.keys():
                raise Exception('未知的参数{}'.format(name))
        for key,value in fields.items():
            if kwargs.get(key) != None:
                self.__setattr__(key,kwargs.get(key))

    # 识别所有field类变量
    @classmethod
    def _get_fields(cla):
        res = {}
        # 遍历所有静态成员,如果对象属于Fields的类就说明为字段
        for key,value in cla.__dict__.items():
            if isinstance(value, field_types):
                res[key] = value
        return res
    
    def get_current_data(self):
        fields = self._get_fields()
        res = {}
        for fieldname in fields.keys():
            value = self.__getattribute__(fieldname)
            if not isinstance(value,field_types):
                res[fieldname] = self.__getattribute__(fieldname)
            else:
                res[fieldname] = None
        return res

    @classmethod
    def create_table(cla):
        db = cla.Meta.db
        table = cla.Meta.table
        cursor = db.cursor()

        fields = cla._get_fields()

        field_str = 'id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,'

        for key,value in fields.items():
            field_str += value.make_sentence(key) + ','
        if field_str.endswith(','):
            field_str = field_str[:-1]

        sentence = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table, field_str)
        cursor.execute(sentence)
    
    @classmethod
    def drop_table(cla):
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()

        sentence = 'DROP TABLE IF EXISTS {}'.format(table)
        cursor.execute(sentence)
    
    def insert(self):
        db = self.Meta.db
        table = self.Meta.table
        cursor = db.cursor()
        data = self.get_current_data()
        fields = self.__class__._get_fields()

        temp1 = ''
        temp2 = ''
        # 类型检查
        for key,value in fields.items():
            if value.check(data.get(key)):
                temp1 += key + ','
                temp2 += value.add(data.get(key)) + ','
            else:
                raise TypeError

        sentence = 'INSERT INTO {} ({}) VALUES({})'.format(table, temp1, temp2)


class User(Base):
    class Meta:
        db = Mysql('localhost', 'root', 'xuri', 'testdb')
        table = 'user'
    username = StringField()
    password = StringField()

user1 = User(username='xuri')
user1.insert()