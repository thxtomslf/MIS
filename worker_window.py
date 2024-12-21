from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from datetime import datetime

from dao.extra_work import ExtraWorkDAO
from dao.worker import WorkerDAO
from entity.worker import Worker


class WorkerWindow(QWidget):

    extra_work_dao: ExtraWorkDAO
    worker_dao: WorkerDAO
    worker: Worker

    def __init__(self, worker_id, db_name='prod'):
        super().__init__()

        self.setWindowTitle("Работник")
        self.setGeometry(100, 100, 600, 400)

        self.worker_id = worker_id

        # Инициализация DAO
        self.extra_work_dao = ExtraWorkDAO(db_name)
        self.worker_dao = WorkerDAO(db_name)

        # Получаем информацию о работнике
        self.worker = self.worker_dao.get_worker(worker_id)
        worker_name = self.worker.full_name if self.worker else "Неизвестно"

        # Основной лейаут
        main_layout = QVBoxLayout()

        # Отображаем имя работника
        self.worker_label = QLabel(f"Работник: {worker_name}")
        main_layout.addWidget(self.worker_label)

        # Отображаем баланс работника
        self.balance_label = QLabel(f"Счет: {self.worker.balance:.2f}")
        main_layout.addWidget(self.balance_label)

        # Лейаут для списка работ
        self.work_list = QListWidget()
        self.load_works()
        main_layout.addWidget(self.work_list)

        # Кнопка для завершения работы
        self.complete_button = QPushButton("Завершено")
        self.complete_button.clicked.connect(self.complete_work)
        main_layout.addWidget(self.complete_button)

        # Устанавливаем основной лейаут
        self.setLayout(main_layout)

        # Устанавливаем таймер для автоматического обновления списка работ и баланса
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_works)
        self.timer.timeout.connect(self.update_balance)
        self.timer.start(4000)  # Обновление каждые 4000 миллисекунд (4 секунды)

    def load_works(self):
        """Загружает и отображает список всех работ, назначенных этому работнику."""
        works = self.extra_work_dao.get_all_extra_works()
        self.work_list.clear()
        for work in works:
            if work[4] == self.worker_id:  # Проверяем, что работа назначена этому работнику
                item_text = f"ID: {work[0]}, Статус: {work[6]}"
                item = QListWidgetItem(item_text)

                # Устанавливаем цвет фона в зависимости от статуса
                if work[6] == "pending":
                    item.setBackground(QColor("yellow"))
                elif work[6] == "in progress":
                    item.setBackground(QColor("orange"))  # Цвет для работы в процессе
                elif work[6] == "done":
                    item.setBackground(QColor("green"))
                elif work[6] == "paid":
                    item.setBackground(QColor("grey"))  # Цвет для оплаченной работы

                self.work_list.addItem(item)

    def complete_work(self):
        """Завершает выбранную работу и фиксирует время окончания."""
        current_item = self.work_list.currentItem()
        if current_item:
            work_id = int(current_item.text().split(",")[0].split(":")[1].strip())
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.extra_work_dao.update_extra_work(work_id, status="done", end_time=end_time)
            self.load_works()

    def update_balance(self):
        """Обновляет отображение баланса работника."""
        self.worker = self.worker_dao.get_worker(self.worker_id)
        if self.worker:
            self.balance_label.setText(f"Счет: {self.worker.balance:.2f}")