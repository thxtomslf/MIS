import sqlite3
from typing import Optional, List

from entity.post import Post
from entity.worker import Worker


class WorkerDAO:
    def __init__(self, db_name='prod'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Создает таблицы worker, post, duties и post_duties, если они не существуют."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS duties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_duties (
                post_id INTEGER,
                duty_id INTEGER,
                PRIMARY KEY (post_id, duty_id),
                FOREIGN KEY (post_id) REFERENCES post(id),
                FOREIGN KEY (duty_id) REFERENCES duties(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS worker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                sex TEXT,
                phone_number TEXT,
                passport_number TEXT,
                passport_series TEXT,
                post_id INTEGER,
                balance REAL DEFAULT 0.0,
                FOREIGN KEY (post_id) REFERENCES post(id)
            )
        ''')
        self.connection.commit()

    def get_worker(self, worker_id: int) -> Optional[Worker]:
        """Возвращает объект Worker с информацией о должности и обязанностях."""
        self.cursor.execute('''
            SELECT w.id, w.full_name, w.sex, w.phone_number, w.passport_number, w.passport_series, w.balance, p.id, p.title
            FROM worker w
            JOIN post p ON w.post_id = p.id
            WHERE w.id = ?
        ''', (worker_id,))
        worker_row = self.cursor.fetchone()

        if worker_row:
            worker_id, full_name, sex, phone_number, passport_number, passport_series, balance, post_id, post_title = worker_row

            # Получаем обязанности для должности
            self.cursor.execute('''
                SELECT d.description
                FROM duties d
                JOIN post_duties pd ON d.id = pd.duty_id
                WHERE pd.post_id = ?
            ''', (post_id,))
            duties = [row[0] for row in self.cursor.fetchall()]

            post = Post(id=post_id, title=post_title, duties=duties)
            worker = Worker(
                id=worker_id,
                full_name=full_name,
                sex=sex,
                phone_number=phone_number,
                passport_number=passport_number,
                passport_series=passport_series,
                post=post,
                balance=balance
            )
            return worker
        return None

    def get_worker_by_name(self, full_name: str) -> Optional[Worker]:
        """Возвращает объект Worker по полному имени."""
        self.cursor.execute('''
            SELECT w.id, w.full_name, w.sex, w.phone_number, w.passport_number, w.passport_series, w.balance, p.id, p.title
            FROM worker w
            JOIN post p ON w.post_id = p.id
            WHERE w.full_name = ?
        ''', (full_name,))
        worker_row = self.cursor.fetchone()

        if worker_row:
            worker_id, full_name, sex, phone_number, passport_number, passport_series, balance, post_id, post_title = worker_row

            # Получаем обязанности для должности
            self.cursor.execute('''
                SELECT d.description
                FROM duties d
                JOIN post_duties pd ON d.id = pd.duty_id
                WHERE pd.post_id = ?
            ''', (post_id,))
            duties = [row[0] for row in self.cursor.fetchall()]

            post = Post(id=post_id, title=post_title, duties=duties)
            worker = Worker(
                id=worker_id,
                full_name=full_name,
                sex=sex,
                phone_number=phone_number,
                passport_number=passport_number,
                passport_series=passport_series,
                post=post,
                balance=balance
            )
            return worker
        return None

    def get_all_workers(self) -> List[Worker]:
        """Возвращает список всех работников с информацией о должности и обязанностях."""
        self.cursor.execute('''
            SELECT w.id, w.full_name, w.sex, w.phone_number, w.passport_number, w.passport_series, w.balance, p.id, p.title
            FROM worker w
            JOIN post p ON w.post_id = p.id
        ''')
        workers = []
        for worker_row in self.cursor.fetchall():
            worker_id, full_name, sex, phone_number, passport_number, passport_series, balance, post_id, post_title = worker_row

            # Получаем обязанности для должности
            self.cursor.execute('''
                SELECT d.description
                FROM duties d
                JOIN post_duties pd ON d.id = pd.duty_id
                WHERE pd.post_id = ?
            ''', (post_id,))
            duties = [row[0] for row in self.cursor.fetchall()]

            post = Post(id=post_id, title=post_title, duties=duties)
            worker = Worker(
                id=worker_id,
                full_name=full_name,
                sex=sex,
                phone_number=phone_number,
                passport_number=passport_number,
                passport_series=passport_series,
                post=post,
                balance=balance
            )
            workers.append(worker)
        return workers

    def update_worker_balance(self, worker_id: int, new_balance: float):
        """Обновляет баланс работника."""
        self.cursor.execute('''
            UPDATE worker
            SET balance = ?
            WHERE id = ?
        ''', (new_balance, worker_id))
        self.connection.commit()

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()