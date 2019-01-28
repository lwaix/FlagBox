import unittest
import pymysql
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
    def test_a_create_table(self):
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
    
    def test_b_insert_one(self):
        User1 = User(username='user1', password='passwd', salary=3000.0)
        User1.insert()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM {}'.format(User.Meta.table))
        id = cursor.fetchone()[0]
        self.assertEqual(id, 1)
        cursor.close()
    
    def test_c_search(self):
        User1 = User.search(User.salary==3000.0).first()
        self.assertEqual(User1.username, 'user1')
    
    def test_d_update(self):
        User1 = User.search(User.salary==3000).first()
        User1.username = 'edit'
        User1.update()
        User1 = User.search(User.username=='edit').first()
        self.assertEqual(User1.username, 'edit')
    
    def test_e_delect(self):
        User1 = User.search(User.id==1).first()
        User1.delete()
        cursor = db.cursor()
        num = cursor.execute('SELECT id FROM {}'.format(User.Meta.table))
        self.assertEqual(num, 0)

if __name__ == '__main__':
    unittest.main()