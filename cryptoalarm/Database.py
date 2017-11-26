import psycopg2
import psycopg2.extras


class Database():
    conn = None
    cursor = None

    def __init__(self, url):
        self.conn = psycopg2.connect(url)
        self.cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    def get_coins(self):
        sql = '''
            SELECT
                name,
                explorer_url
            FROM
                coins
        '''

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_setting(self, key):
        sql = '''
            SELECT 
                value
            FROM 
                settings
            WHERE
                key = %s
        '''

        self.cursor.execute(sql, (key,))
        return self.cursor.fetchone()['value']

    def get_addresses(self):
        sql = '''
            SELECT 
                a.id "address_id", 
                a.hash "hash", 
                c.name "coin" 
            FROM 
                addresses a 
            NATURAL JOIN 
                coins c
        '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_address_users(self, id, type):
        sql = '''
            SELECT 
                w.type "type", 
                w.name "watchlist_name", 
                w.notify "notify", 
                w.id "watchlist_id",
                u.id "user_id", 
                u.email "email",
                u.email_template "email_template"
            FROM 
                watchlists w 
            JOIN 
                users u
            ON u.id = w.user_id
            WHERE w.address_id = %s AND w.type = %s
        '''
        self.cursor.execute(sql, (id, type))
        return self.cursor.fetchall()

    def get_last_block_number(self, coin):
        sql = '''
            SELECT 
                last_block 
            FROM 
                coins
            WHERE 
                name = %s
        '''
        self.cursor.execute(sql, (str(coin),))
        result = self.cursor.fetchone()

        return result['last_block']

    def set_last_block_number(self, coin, number):
        sql = '''
            UPDATE 
                coins
            SET 
                last_block = %s  
            WHERE 
                name = %s
        '''
        self.cursor.execute(sql, (number, str(coin),))
        self.conn.commit()
        