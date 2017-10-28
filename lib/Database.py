import pymysql

class Database():
    conn = None

    def __init__(self, host, user, password, db):
        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    password=password,
                                    db=db,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)

    def get_addresses(self, coin):
        with self.conn.cursor() as cursor:
            sql = 'SELECT * FROM `address` NATURAL JOIN coin WHERE `coin`.`name` = %s'
            cursor.execute(sql, (coin.__class__.__name__,))
            result = cursor.fetchall()
            print('Class: {}, addresses: {}'.format(coin.__class__.__name__, result))

            return result

    def get_last_block_hash(self, coin):
        with self.conn.cursor() as cursor:
            sql = 'SELECT last_block FROM coin WHERE name = %s'
            cursor.execute(sql, (coin.__class__.__name__,))
            result = cursor.fetchone()

            return result['last_block']

    def set_last_block_hash(self, coin, hash):
        with self.conn.cursor() as cursor:
            sql = 'UPDATE coin SET last_block = %s  WHERE name = %s'
            cursor.execute(sql, (hash, coin.__class__.__name__,))

        self.conn.commit()
        