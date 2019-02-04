from .fields import field_types, defaultable
from .tools import Result

"""
TODO:
    - 重构代码
    - 英文注释
"""

class Base:
    # 内置类Meta,用来定义Model的数据库与表,这两个元素都必须定义
    class Meta:
        db = None
        table = None

    # 在每个操作里面都检查是否init,仅仅执行一次_init()方法
    _init_sign = False

    # 接收本对象的各个字段值,没有赋值的默认为None
    def __init__(self, **kwargs):
        self.__class__._init()
        # 如果id为None说明该对象还未被插入
        fields = self.__class__._get_fields()
        fieldnames = fields.keys()
        keys = kwargs.keys()
        if 'id' in keys:
            raise ValueError('id不能被手动赋值')
        # 检查未知的参数
        for key in keys:
            if key not in fieldnames:
                raise ValueError('未知的参数{}'.format(key))
        # 设置对象的值
        for key in fields.keys():
            self.__setattr__(key,kwargs.get(key, None))
        # 对于某些定义的default的Model,会给它赋上default值
        for field in fields.values():
            if isinstance(field, defaultable):
                if field.default is not None and self.__getattribute__(field.fieldname) is None:
                    self.__setattr__(field.fieldname,field.default)

    # 初始化该Model,将字段名写入_fields,将字段名写入对应字段对象,并标记已初始化,只初始化一次
    @classmethod
    def _init(cla):
        # 检查是否已初始化
        if not cla._init_sign:
            cla._fields = dict()
            id_sign = False
            for key,value in cla.__dict__.items():
                if (not id_sign) and (key == 'id'):
                    id_sign = True
                # 如果类对象属于Fields,那么说明它就是被定义在Model中的字段,将它写入_fields
                # _fields的格式:{fieldname1:field_obj1, fieldname2:field_obj2,...}
                if isinstance(value, field_types):
                    # field对象也包含fieldname,需要赋值给它已保证其正常工作
                    value.fieldname = key
                    cla._fields[key] = value
            if not id_sign:
                raise AttributeError('该模型未定义id字段')
            # 标记已经初始化
            cla._init_sign = True

    # 获取_fields
    @classmethod
    def _get_fields(cla):
        return cla._fields
    
    # 获取当前对象的数据
    def _get_current_data(self):
        fields = self.__class__._get_fields()
        res = {}
        for fieldname in fields.keys():
            res[fieldname] = self.__getattribute__(fieldname)
        return res

    # 建表操作
    @classmethod
    def create_table(cla):
        # 检查是否初始化
        cla._init()
        db = cla.Meta.db
        table = cla.Meta.table
        cursor = db.cursor()
        fields = cla._get_fields()

        field_elements = []
        for value in fields.values():
            field_elements.append(value._make_element())
        
        sentence = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table, ','.join(field_elements))
        cursor.execute(sentence)
        cursor.close()
        db.commit()
    
    # 删表操作
    @classmethod
    def drop_table(cla):
        cla._init()
        db = cla.Meta.db
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()

        sentence = 'DROP TABLE IF EXISTS {}'.format(table)
        cursor.execute(sentence)
        cursor.close()
        db.commit()
    
    # 插入操作
    def insert(self):
        # 被插入过的对象无法被重复插入
        if self.inserted():
            raise RuntimeError("该对象已被插入,不可重复插入")
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
            if value._check(data.get(key)):
                # id不需要插入,值为None的也不需要插入
                if key == 'id' or data.get(key) is None:
                    continue
                fieldnames.append(key)
                values.append(value._value(((data.get(key)))))
            else:
                raise TypeError('类型不匹配')
        sentence = 'INSERT INTO {} ({}) VALUES({})'.format(table, ','.join(fieldnames), ','.join(values))
        cursor.execute(sentence)
        # 标记该对象id
        self.id = cursor.lastrowid
        cursor.close()
        db.commit()
    
    # 如果对象已被插入则返回True
    def inserted(self):
        # 检查id是否通过检查 检查id是否为None
        if self.__class__._get_fields().get('id')._check(self.id) and self.id == None:
            return False
        return True
    
    # 查询所有符合条件的结果,封装为Result对象并返回
    @classmethod
    def search(cla, query=None, orders=None):
        cla._init()
        db = cla.Meta.db
        table = cla.Meta.table
        cursor = cla.Meta.db.cursor()
        fieldnames = cla._get_fields().keys()
        
        fieldnames_str = ','.join(fieldnames)
        # 如果query为None则返回所有结果
        if query:
            sentence = 'SELECT {} FROM {} WHERE {}'.format(fieldnames_str, table, query.condition)
        else:
            sentence = 'SELECT {} FROM {}'.format(fieldnames_str, table)
        if orders:
            o = []
            for order in orders:
                if isinstance(order, field_types):
                    o.append(order.fieldname)
                if isinstance(order, str):
                    o.append(order)
            sentence = "{} ORDER BY {}".format(sentence, ','.join(o))
        # 当查询结果为0时
        cursor.execute(sentence)
        rows = cursor.fetchall()
        res = []
        # 将查询结果封装为Model对象
        for one in rows:
            one = list(one)
            obj = cla()
            index = 0
            while index <= len(fieldnames)-1:
                obj.__setattr__(list(fieldnames)[index], one[index])
                index += 1
            res.append(obj)
        cursor.close()
        db.commit()
        return Result(res)
    
    # 更新该对象
    def update(self):
        # 没有被插入的对象无法更新
        if not self.inserted():
            raise RuntimeError('该对象不可更新')
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()
        fields = self.__class__._get_fields()
        current_data = self._get_current_data()

        sets = []
        for field in fields.values():
            value = current_data.get(field.fieldname)
            if not field._check(value):
                raise TypeError('字段值类型不匹配')
            sets.append('{}={}'.format(field.fieldname,field._value(value)))
        temp = ','.join(sets)
        sentence = 'UPDATE {} SET {} WHERE id={}'.format(table, temp, str(self.id))
        cursor.execute(sentence)
        cursor.close()
        db.commit()
    
    # 删除该对象
    def delete(self):
        # 没被插入的无法被删除
        if not self.inserted():
            raise RuntimeError('该对象不可删除')
        self.__class__._init()
        db = self.__class__.Meta.db
        table = self.__class__.Meta.table
        cursor = db.cursor()

        sentence = 'DELETE FROM {} WHERE id={}'.format(table, self.id)
        cursor.execute(sentence)
        self.id = None
        cursor.close()
        db.commit()
