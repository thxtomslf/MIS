import sqlite3


class ClientDAO:
    def __init__(self, db_name="prod"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """Создает таблицу client, если она не существует."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS client (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT
            )
        ''')
        self.connection.commit()

    def create_client(self, first_name, last_name, phone_number):
        """Создает новую запись клиента в таблице."""
        self.cursor.execute('''
            INSERT INTO client (first_name, last_name, phone_number)
            VALUES (?, ?, ?)
        ''', (first_name, last_name, phone_number))
        self.connection.commit()

    def create_client_with_id(self, id, first_name, last_name, phone_number):
        """Создает новую запись клиента в таблице."""
        self.cursor.execute('''
            INSERT INTO client (id, first_name, last_name, phone_number)
            VALUES (?, ?, ?, ?)
        ''', (id ,first_name, last_name, phone_number))
        self.connection.commit()

    def get_client(self, client_id):
        """Возвращает запись клиента по ID."""
        self.cursor.execute('SELECT * FROM client WHERE id = ?', (client_id,))
        return self.cursor.fetchone()

    def get_all_clients(self):
        """Возвращает все записи клиентов."""
        self.cursor.execute('SELECT * FROM client')
        return self.cursor.fetchall()

    def update_client(self, client_id, first_name=None, last_name=None, phone_number=None):
        """Обновляет запись клиента по ID."""
        updates = []
        values = []

        if first_name is not None:
            updates.append("first_name = ?")
            values.append(first_name)
        if last_name is not None:
            updates.append("last_name = ?")
            values.append(last_name)
        if phone_number is not None:
            updates.append("phone_number = ?")
            values.append(phone_number)

        values.append(client_id)

        if updates:
            self.cursor.execute(f'''
                UPDATE client
                SET {', '.join(updates)}
                WHERE id = ?
            ''', values)
            self.connection.commit()

    def delete_client(self, client_id):
        """Удаляет запись клиента по ID."""
        self.cursor.execute('DELETE FROM client WHERE id = ?', (client_id,))
        self.connection.commit()

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()
