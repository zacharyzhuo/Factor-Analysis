import pymysql
from utils.config import Config


class DBMgr:

    CONN_FAIL_CODE = '0000'
    CONN_FAIL_MSG = '無法建立連線'

    def __init__(self, db='stock'):
        self._state = False
        self._connection = None
        self._cfg = Config()
        self._db_data = self._cfg.get_database()
        self._db_data['db'] = db
        self._conn()

    def _mysql_error(self):
        return pymysql.MySQLError

    def _conn(self):
        try:
            self._connection = pymysql.connections.Connection(
                host=self._db_data['host'],
                user=self._db_data['user'],
                passwd=self._db_data['passwd'],
                db=self._db_data['db'],
                charset=self._db_data['charset'],
                cursorclass=pymysql.cursors.DictCursor)
            self._state = True
            return self._connection

        except self._mysql_error() as e:
            self._state = False
            print('[DBMgr] 【{}】{!r}'.format(e.args[0], e.args[1]))
            self._conn()

    def _cursor(self):
        try:
            self._connection
        except:
            self._conn()
        return self._connection.cursor()

    def _commit(self):
        try:
            self._connection
        except:
            self._conn()
        return self._connection.commit()

    def _close(self):
        try:
            self._connection
        except:
            self._conn()
        else:
            self._cursor().close()
            self._connection.close()
            self._connection = None

    def insert(self, sql, args, multiple=False):
        row = -1

        if self._conn():
            try:
                with self._cursor() as cursor:
                    if not multiple:
                        row = cursor.execute(sql, args)
                    else:
                        row = cursor.executemany(sql, args)
                    self._commit()

                    result_id = cursor.lastrowid if not multiple else [cursor.lastrowid + i for i in range(row)]
            except self._mysql_error() as e:
                print('[DBMgr] 【{}】{!r}'.format(e.args[0], e.args[1]))
                return False, row, (e.args[0], e.args[1])
        else:
            print("[DBMgr] Fails to connect to MySQL Server!!")
            return False, row, (DBMgr.CONN_FAIL_CODE, DBMgr.CONN_FAIL_MSG)
        self._close()
        return True, row, result_id

    def update(self, sql, args, multiple=False):
        row = -1
        result = -1

        if self._conn():
            try:
                with self._cursor() as cursor:
                    if not multiple:
                        row = cursor.execute(sql, args)
                    else:
                        row = cursor.executemany(sql, args)
                    self._commit()
            except self._mysql_error() as e:
                print('[DBMgr] 【{}】{!r}'.format(e.args[0], e.args[1]))
                return False, row, (e.args[0], e.args[1])
        else:
            print("[DBMgr] Fails to connect to MySQL Server!!")
            return False, row, (DBMgr.CONN_FAIL_CODE, DBMgr.CONN_FAIL_MSG)
        self._close()
        return True, row, result

    def query(self, sql, args, fetch='all'):
        row = -1
        result = list()

        if self._conn():
            try:
                with self._cursor() as cursor:
                    row = cursor.execute(sql, args)
                    result = cursor.fetchone() if fetch != 'all' else cursor.fetchall()
                    self._commit()
            except self._mysql_error() as e:
                print('[DBMgr] 【{}】{!r}'.format(e.args[0], e.args[1]))
                return False, row, (e.args[0], e.args[1])
        else:
            print("[DBMgr] Fails to connect to MySQL Server!!")
            return False, row, (DBMgr.CONN_FAIL_CODE, DBMgr.CONN_FAIL_MSG)
        self._close()
        return True, row, result

    def delete(self, sql, args):
        row = -1
        result = list()
        if self._conn():
            try:
                with self._cursor() as cursor:
                    row = cursor.execute(sql, args)
                    self._commit()

            except self._mysql_error() as e:
                print('[DBMgr] 【{}】{!r}'.format(e.args[0], e.args[1]))
                return False, row, (e.args[0], e.args[1])
        else:
            print("[DBMgr] Fails to connect to MySQL Server!!")
            return False, row, (DBMgr.CONN_FAIL_CODE, DBMgr.CONN_FAIL_MSG)
        self._close()
        return True, row, result

    def get_db_column(self, db, table):
        if self._conn():
            try:
                with self._cursor() as cursor:
                    sql = " SELECT `COLUMN_NAME` AS `name` \
                            FROM `INFORMATION_SCHEMA`.`COLUMNS` \
                            WHERE `TABLE_SCHEMA` = %(db)s AND `TABLE_NAME` = %(table)s"
                    args = {
                        'db': db,
                        'table': table
                    }

                    num_of_rows = int(cursor.execute(sql, args))
                    result = cursor.fetchall()
                    self._commit()

            except self._mysql_error() as e:
                print('[DBMgr] 【{}】{!r}'.format(e.args[0], e.args[1]))
        else:
            print("[DBMgr] Fails to connect to MySQL Server!!")
        self._close()
        return result

    def insert_sql(self, table, column_dict, have_id):
        if have_id:
            col_dict = column_dict
        else:
            col_dict = column_dict[1:]

        query_columns = list()
        query_placeholders = list()

        for each in col_dict:
            query_columns.append('`' + each['name'] + '`')
            query_placeholders.append('%(' + each['name'] + ')s')

        query_columns = ', '.join(query_columns)
        query_placeholders = ', '.join(query_placeholders)
        insert_query = "INSERT INTO `%s` (%s) VALUES (%s)" % (table, query_columns, query_placeholders)
        return insert_query

    def query_sql(self, table, column_dict, have_id):
        if have_id:
            col_dict = column_dict
        else:
            col_dict = column_dict[1:]

        query = list()

        for each in col_dict:
            query.append('`' + each['name'] + '`' + '=' + '%(' + each['name'] + ')s')

        query = ' AND '.join(query)
        query_sql = "SELECT * FROM %s WHERE %s" % (table, query)
        return query_sql
