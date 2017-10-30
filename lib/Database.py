import pymysql
import logging

class Database():
    conn = None

    def __init__(self, host, user, password, db):
        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    password=password,
                                    db=db,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)

    def get_addresses(self):
        with self.conn.cursor() as cursor:
            sql = 'SELECT a.address_id, a.hash, c.name coin FROM `address` a NATURAL JOIN coin c'
            cursor.execute(sql)
            return cursor.fetchall()

    def get_address_users(self, id, type):
        with self.conn.cursor() as cursor:
            sql = 'SELECT w.type type, w.notify, u.user_id user_id, u.email email, notify FROM watchlist w NATURAL JOIN user u WHERE w.address_id = %s AND w.type = %s'
            cursor.execute(sql, (id, type))
            return cursor.fetchall()

    def get_last_block_hash(self, coin):
        with self.conn.cursor() as cursor:
            sql = 'SELECT last_block FROM coin WHERE name = %s'
            cursor.execute(sql, (str(coin),))
            result = cursor.fetchone()

            return result['last_block']

    def set_last_block_hash(self, coin, hash):
        with self.conn.cursor() as cursor:
            sql = 'UPDATE coin SET last_block = %s  WHERE name = %s'
            cursor.execute(sql, (hash, str(coin),))

        self.conn.commit()
        