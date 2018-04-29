import psycopg2
import psycopg2.extras


class Database():
    conn = None
    cursor = None

    def __init__(self, url):
        self.conn = psycopg2.connect(url)
        self.cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    def get_coin(self, name):
        sql = '''
            SELECT
                id,
                name,
                explorer_url
            FROM
                coins
            WHERE
                name = %s
        '''

        self.cursor.execute(sql, (name,))
        return self.cursor.fetchone()

    def get_coins(self):
        sql = '''
            SELECT
                id,
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
            JOIN 
                coins c
            ON a.coin_id = c.id
            JOIN 
                watchlists w
            ON w.address_id = a.id
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
                w.email_template "email_template",
                u.id "user_id", 
                u.email "email",
                u.rest_url "rest_url"
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
                number 
            FROM 
                blocks
            WHERE 
                id = (
                    SELECT 
                        MAX(id) 
                    FROM 
                        blocks 
                    WHERE 
                        coin_id = %s
                )
        '''
        self.cursor.execute(sql, (coin.db_id,))
        result = self.cursor.fetchone()

        return result['number']

    def set_last_block_number(self, coin, number):
        sql = '''
            UPDATE 
                coins
            SET 
                last_block = %s  
            WHERE 
                id = %s
        '''
        self.cursor.execute(sql, (number, coin.db_id,))
        self.conn.commit()

    def get_block_hash(self, coin, number):
        sql = '''
            SELECT 
                hash 
            FROM 
                blocks
            WHERE 
                coin_id = %s AND number = %s
        '''
        self.cursor.execute(sql, (coin.db_id, number))
        result = self.cursor.fetchone()

        return result['hash'] if result else None

    def set_block_number(self, coin, number, block_hash):
        sql = '''
            INSERT INTO blocks
                (coin_id, number, hash)
            VALUES
                (%s, %s, %s)
            ON CONFLICT (coin_id, number) DO UPDATE SET 
                hash = EXCLUDED.hash
        '''
        self.cursor.execute(sql, (coin.db_id, number, block_hash))
        self.conn.commit()
        