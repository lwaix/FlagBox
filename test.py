import unittest
import pmorm

db = pmorm.Mysql('localhost', 'root', 'xuri', 'testdb')

class User(pmorm.Base):
    class Meta:
        db = db
        table = 'user'
    
    id = pmorm.PrimaryKeyField()
    username = pmorm.VarcharField(32, False, True)
    password = pmorm.VarcharField(64, False, False)
    salary = pmorm.FloatField(True, False)
    comment = pmorm.TextField(True, False)

class Test(unittest.TestCase):
    # 基础组件
    def test_a_prime(self):
        i1 = pmorm.IntField(nullable=True, unique=False)
        i1.fieldname = 'i1'
        i2 = pmorm.IntField(nullable=True, unique=True)
        i2.fieldname = 'i2'
        i3 = pmorm.IntField(nullable=False, unique=False)
        i3.fieldname = 'i3'
        i4 = pmorm.IntField(nullable=False, unique=True)
        i4.fieldname = 'i4'
        i5 = pmorm.IntField(nullable=False, unique=True, default=32)
        i5.fieldname = 'i5'
        self.assertEqual(i1._make_element(), "i1 INT")
        self.assertEqual(i2._make_element(), 'i2 INT UNIQUE')
        self.assertEqual(i3._make_element(), 'i3 INT NOT NULL')
        self.assertEqual(i4._make_element(), 'i4 INT NOT NULL UNIQUE')
        self.assertEqual(i5._make_element(), "i5 INT DEFAULT 32 NOT NULL UNIQUE")
        self.assertEqual(i1._check(None), True)
        self.assertEqual(i1._check(32), True)
        self.assertEqual(i3._check("1"), False)
        self.assertEqual(i3._check(None), False)
        self.assertEqual(i3._check(32), True)
        self.assertEqual(i1._value(32), '32')
        self.assertEqual(i1._value(None), 'NULL')

        f1 = pmorm.FloatField(nullable=True, unique=False)
        f1.fieldname = 'f1'
        f2 = pmorm.FloatField(nullable=True, unique=True)
        f2.fieldname = 'f2'
        f3 = pmorm.FloatField(nullable=False, unique=False)
        f3.fieldname = 'f3'
        f4 = pmorm.FloatField(nullable=False, unique=True)
        f4.fieldname = 'f4'
        f5 = pmorm.FloatField(nullable=False, unique=True, default=32)
        f5.fieldname = 'f5'
        f6 = pmorm.FloatField(nullable=False, unique=True, default=32.1)
        f6.fieldname = 'f6'
        self.assertEqual(f1._make_element(), "f1 FLOAT")
        self.assertEqual(f2._make_element(), 'f2 FLOAT UNIQUE')
        self.assertEqual(f3._make_element(), 'f3 FLOAT NOT NULL')
        self.assertEqual(f4._make_element(), 'f4 FLOAT NOT NULL UNIQUE')
        self.assertEqual(f5._make_element(), "f5 FLOAT DEFAULT 32 NOT NULL UNIQUE")
        self.assertEqual(f6._make_element(), "f6 FLOAT DEFAULT 32.1 NOT NULL UNIQUE")
        self.assertEqual(f1._check(None), True)
        self.assertEqual(f1._check(32), True)
        self.assertEqual(f3._check("1"), False)
        self.assertEqual(f3._check(None), False)
        self.assertEqual(f3._check(32), True)
        self.assertEqual(f3._check(32.1), True)
        self.assertEqual(f1._value(32), '32')
        self.assertEqual(f1._value(32.1), '32.1')
        self.assertEqual(f1._value(None), 'NULL')

        v1 = pmorm.VarcharField(max_length=256, nullable=True, unique=False)
        v1.fieldname = 'v1'
        v2 = pmorm.VarcharField(max_length=512, nullable=True, unique=True)
        v2.fieldname = 'v2'
        v3 = pmorm.VarcharField(max_length=1024, nullable=False, unique=False)
        v3.fieldname = 'v3'
        v4 = pmorm.VarcharField(max_length=2048, nullable=False, unique=True)
        v4.fieldname = 'v4'
        v5 = pmorm.VarcharField(max_length=4096, nullable=False, unique=True, default='"I am oj8k"')
        v5.fieldname = 'v5'
        self.assertEqual(v1._make_element(), "v1 VARCHAR(256)")
        self.assertEqual(v2._make_element(), 'v2 VARCHAR(512) UNIQUE')
        self.assertEqual(v3._make_element(), 'v3 VARCHAR(1024) NOT NULL')
        self.assertEqual(v4._make_element(), 'v4 VARCHAR(2048) NOT NULL UNIQUE')
        self.assertEqual(v5._make_element(), "v5 VARCHAR(4096) DEFAULT '{}' NOT NULL UNIQUE".format('\\"I am oj8k\\"'))
        self.assertEqual(v1._check(None), True)
        self.assertEqual(v1._check('DEMO'), True)
        self.assertEqual(v3._check(1), False)
        self.assertEqual(v3._check(None), False)
        self.assertEqual(v1._value('"I am oj8k"'), '\'\\"I am oj8k\\"\'')
        self.assertEqual(v1._value(None), 'NULL')

        t1 = pmorm.TextField(nullable=True, unique=False)
        t1.fieldname = 't1'
        t2 = pmorm.TextField(nullable=True, unique=True)
        t2.fieldname = 't2'
        t3 = pmorm.TextField(nullable=False, unique=False)
        t3.fieldname = 't3'
        t4 = pmorm.TextField(nullable=False, unique=True)
        t4.fieldname = 't4'
        self.assertEqual(t1._make_element(), "t1 TEXT")
        self.assertEqual(t2._make_element(), 't2 TEXT UNIQUE')
        self.assertEqual(t3._make_element(), 't3 TEXT NOT NULL')
        self.assertEqual(t4._make_element(), 't4 TEXT NOT NULL UNIQUE')
        self.assertEqual(t1._check(None), True)
        self.assertEqual(t1._check('DEMO'), True)
        self.assertEqual(t3._check(None), False)
        self.assertEqual(t3._check('DEMO'), True)
        self.assertEqual(t1._value('"I am oj8k"'), '\'\\"I am oj8k\\"\'')
        self.assertEqual(t1._value(None), 'NULL')

    def test_b_create_table(self):
        User.create_table()
        cursor = db.cursor()
        # 如果无异常,说明表已经创建,sign为1,否则为0
        try:
            cursor.execute('SELECT 1 FROM {} LIMIT 1'.format(User.Meta.table))
            sign = 1
        except Exception:
            sign = 0
        self.assertEqual(sign, 1)
        cursor.close()
    
    def test_c_insert_one(self):
        User1 = User(username='user1', password='passwd', salary=3000.0)
        User1.insert()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM {}'.format(User.Meta.table))
        id = cursor.fetchone()[0]
        self.assertEqual(id, 1)
        cursor.close()
    
    def test_d_search(self):
        User1 = User.search(User.salary==3000.0).first()
        self.assertEqual(User1.username, 'user1')
    
    def test_e_update(self):
        User1 = User.search(User.salary==3000).first()
        User1.username = 'edit'
        User1.update()
        User1 = User.search(User.username=='edit').first()
        self.assertEqual(User1.username, 'edit')
    
    def test_f_delete(self):
        User1 = User.search(User.id==1).first()
        User1.delete()
        cursor = db.cursor()
        num = cursor.execute('SELECT id FROM {}'.format(User.Meta.table))
        self.assertEqual(num, 0)
    
    def test_g_drop_table(self):
        User.drop_table()
        try:
            cursor.execute('SELECT id FROM {}'.format(User.Meta.table))
            sign = 0
        except:
            sign = 1
        self.assertEqual(sign, 1)

if __name__ == '__main__':
    unittest.main()
