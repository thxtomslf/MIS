import sqlite3
from typing import List, Tuple, Optional


class ExtraWorkDAO:
    def __init__(self, db_name='prod'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """Создает таблицу extra_work, если она не существует."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS extra_work (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                start_time DATETIME,
                end_time DATETIME,
                assignee INTEGER REFERENCES worker(id),
                extra_work_type_id INTEGER REFERENCES extra_work_type(id),
                status TEXT,
                client_id INTEGER REFERENCES client(id)
            )
        ''')
        self.connection.commit()

    def create_extra_work(self, type: str, start_time: Optional[str], end_time: Optional[str], assignee: Optional[int], extra_work_type_id: int, status: str, client_id: int):
        """Создает новую запись о дополнительной работе."""
        self.cursor.execute('''
            INSERT INTO extra_work (type, start_time, end_time, assignee, extra_work_type_id, status, client_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (type, start_time, end_time, assignee, extra_work_type_id, status, client_id))
        self.connection.commit()

    def get_extra_work(self, work_id: int) -> Optional[Tuple]:
        """Возвращает запись о дополнительной работе по ID."""
        self.cursor.execute('SELECT * FROM extra_work WHERE id = ?', (work_id,))
        return self.cursor.fetchone()

    def get_all_extra_works(self) -> List[Tuple]:
        """Возвращает все записи о дополнительной работе."""
        self.cursor.execute('SELECT * FROM extra_work')
        return self.cursor.fetchall()

    def update_extra_work(self, work_id: int, **kwargs):
        """Обновляет запись о дополнительной работе по ID."""
        updates = []
        values = []

        if 'type' in kwargs:
            updates.append("type = ?")
            values.append(kwargs['type'])
        if 'start_time' in kwargs:
            updates.append("start_time = ?")
            values.append(kwargs['start_time'])
        if 'end_time' in kwargs:
            updates.append("end_time = ?")
            values.append(kwargs['end_time'])
        if 'assignee' in kwargs:
            updates.append("assignee = ?")
            values.append(kwargs['assignee'])
        if 'extra_work_type_id' in kwargs:
            updates.append("extra_work_type_id = ?")
            values.append(kwargs['extra_work_type_id'])
        if 'status' in kwargs:
            updates.append("status = ?")
            values.append(kwargs['status'])
        if 'client_id' in kwargs:
            updates.append("client_id = ?")
            values.append(kwargs['client_id'])

        values.append(work_id)

        if updates:
            self.cursor.execute(f'''
                UPDATE extra_work
                SET {', '.join(updates)}
                WHERE id = ?
            ''', values)
            self.connection.commit()

    def delete_extra_work(self, work_id: int):
        """Удаляет запись о дополнительной работе по ID."""
        self.cursor.execute('DELETE FROM extra_work WHERE id = ?', (work_id,))
        self.connection.commit()

    def get_last_inserted_id(self) -> int:
        """Возвращает ID последней вставленной записи."""
        return self.cursor.execute('SELECT last_insert_rowid()').fetchone()[0]

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()