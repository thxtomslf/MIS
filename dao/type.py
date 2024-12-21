import sqlite3


class ExtraWorkTypeDAO:
    def __init__(self, db_name='prod'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """Создает таблицу extra_work_type, если она не существует."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS extra_work_type (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                payment REAL,
                type TEXT
            )
        ''')
        self.connection.commit()

    def create_extra_work_type(self, description, payment, type):
        """Создает новую запись типа дополнительной работы."""
        self.cursor.execute('''
            INSERT INTO extra_work_type (description, payment, type)
            VALUES (?, ?, ?)
        ''', (description, payment, type))
        self.connection.commit()

    def get_extra_work_type(self, extra_work_type_id):
        """Возвращает запись типа дополнительной работы по ID."""
        self.cursor.execute('SELECT * FROM extra_work_type WHERE id = ?', (extra_work_type_id,))
        return self.cursor.fetchone()

    def get_all_extra_work_types(self):
        """Возвращает все записи типов дополнительной работы."""
        self.cursor.execute('SELECT * FROM extra_work_type')
        return self.cursor.fetchall()

    def update_extra_work_type(self, extra_work_type_id, description=None, payment=None, type=None):
        """Обновляет запись типа дополнительной работы по ID."""
        updates = []
        values = []

        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if payment is not None:
            updates.append("payment = ?")
            values.append(payment)
        if type is not None:
            updates.append("type = ?")
            values.append(type)

        values.append(extra_work_type_id)

        if updates:
            self.cursor.execute(f'''
                UPDATE extra_work_type
                SET {', '.join(updates)}
                WHERE id = ?
            ''', values)
            self.connection.commit()

    def delete_extra_work_type(self, extra_work_type_id):
        """Удаляет запись типа дополнительной работы по ID."""
        self.cursor.execute('DELETE FROM extra_work_type WHERE id = ?', (extra_work_type_id,))
        self.connection.commit()

    def drop_table(self):
        self.cursor.execute('DELETE FROM extra_work_type')

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()