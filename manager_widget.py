from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from datetime import datetime

from dao.extra_work import ExtraWorkDAO
from dao.type import ExtraWorkTypeDAO
from dao.worker import WorkerDAO


class ManagerWindow(QWidget):

    extra_work_dao: ExtraWorkDAO
    worker_dao: WorkerDAO
    work_type_dao: ExtraWorkTypeDAO

    def __init__(self, db_name='prod'):
        super().__init__()

        self.setWindowTitle("Менеджер")
        self.setGeometry(100, 100, 800, 600)

        # Инициализация DAO
        self.extra_work_dao = ExtraWorkDAO(db_name)
        self.worker_dao = WorkerDAO(db_name)
        self.work_type_dao = ExtraWorkTypeDAO(db_name)

        # Основной лейаут
        main_layout = QHBoxLayout()

        # Левый лейаут для списка заявок
        self.request_list = QListWidget()
        self.request_list.currentItemChanged.connect(self.display_selected_request)
        self.current_requests = []  # Хранит текущее состояние списка заявок
        self.load_requests()
        main_layout.addWidget(self.request_list)

        # Центральная панель для отображения выбранной заявки и работника
        self.selected_request_label = QLabel("Выбранная заявка: None")
        self.selected_worker_label = QLabel("Выбранный работник: None")
        self.assign_button = QPushButton("Назначить")
        self.assign_button.clicked.connect(self.assign_work)

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.selected_request_label)
        center_layout.addWidget(self.selected_worker_label)
        center_layout.addWidget(self.assign_button)
        main_layout.addLayout(center_layout)

        # Правый лейаут для списка работников
        self.worker_list = QListWidget()
        self.worker_list.currentItemChanged.connect(self.display_selected_worker)
        self.load_workers()
        main_layout.addWidget(self.worker_list)

        # Нижняя панель для отображения имени исполнителя и кнопки оплаты
        self.worker_name_field = QLineEdit()
        self.worker_name_field.setReadOnly(True)
        self.pay_button = QPushButton("Оплатить работу")
        self.pay_button.clicked.connect(self.pay_for_work)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(QLabel("Исполнитель работы:"))
        bottom_layout.addWidget(self.worker_name_field)
        bottom_layout.addWidget(self.pay_button)
        main_layout.addLayout(bottom_layout)

        # Устанавливаем основной лейаут
        self.setLayout(main_layout)

        # Устанавливаем таймер для автоматического обновления списка заявок
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_requests)
        self.timer.start(4000)  # Обновление каждые 4000 миллисекунд (4 секунды)

    def load_requests(self):
        """Загружает и отображает список всех заявок."""
        requests = self.extra_work_dao.get_all_extra_works()
        new_requests = []

        for request in requests:
            extra_work_type_id = request[5]
            work_type = self.work_type_dao.get_extra_work_type(extra_work_type_id)
            work_type_name = work_type[3] if work_type else "Неизвестно"

            item_text = f"ID: {request[0]}, Тип Работы: {work_type_name}, Статус: {request[6]}"
            new_requests.append(item_text)

        # Проверяем, изменился ли список заявок
        if new_requests != self.current_requests:
            self.current_requests = new_requests
            self.request_list.clear()
            for item_text in new_requests:
                item = QListWidgetItem(item_text)

                # Устанавливаем цвет фона в зависимости от статуса
                if "Статус: pending" in item_text:
                    item.setBackground(QColor("yellow"))
                elif "Статус: in progress" in item_text:
                    item.setBackground(QColor("orange"))  # Изменяем цвет на оранжевый
                elif "Статус: done" in item_text:
                    item.setBackground(QColor("green"))
                elif "Статус: paid" in item_text:
                    item.setBackground(QColor("grey"))  # Цвет для оплаченной работы

                self.request_list.addItem(item)

    def load_workers(self):
        """Загружает и отображает список всех работников."""
        workers = self.worker_dao.get_all_workers()
        self.worker_list.clear()
        for worker in workers:
            item_text = f"{worker.full_name} - {worker.post.title}"
            item = QListWidgetItem(item_text)
            self.worker_list.addItem(item)

    def display_selected_request(self, current, previous):
        """Отображает выбранную заявку и имя исполнителя, если работа завершена."""
        if current:
            request_text = current.text()
            if "Статус: done" not in request_text and "Статус: paid" not in request_text:
                self.selected_request_label.setText(f"Выбранная заявка: {request_text}")
            else:
                self.selected_request_label.setText("Выбранная заявка: None")

            # Проверяем статус работы
            if "Статус: done" in request_text:
                request_id = int(request_text.split(",")[0].split(":")[1].strip())
                work = self.extra_work_dao.get_extra_work(request_id)
                if work:
                    worker = self.worker_dao.get_worker(work[4])
                    if worker:
                        self.worker_name_field.setText(worker.full_name)
                    else:
                        self.worker_name_field.setText("Неизвестно")
            else:
                self.worker_name_field.clear()

    def display_selected_worker(self, current, previous):
        """Отображает выбранного работника."""
        if current:
            self.selected_worker_label.setText(f"Выбранный работник: {current.text()}")

    def assign_work(self):
        """Назначает работу выбранному работнику по выбранной заявке."""
        current_request_item = self.request_list.currentItem()
        current_worker_item = self.worker_list.currentItem()

        if current_request_item and current_worker_item:
            request_id = int(current_request_item.text().split(",")[0].split(":")[1].strip())
            worker_full_name = current_worker_item.text().split(" - ")[0]

            # Получаем объект работника
            worker = self.worker_dao.get_worker_by_name(worker_full_name)

            if worker:
                # Устанавливаем текущее время как время начала работы
                start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Обновляем статус заявки, связываем с работником и фиксируем время начала
                self.extra_work_dao.update_extra_work(
                    request_id,
                    status="in progress",
                    assignee=worker.id,
                    start_time=start_time
                )

                self.load_requests()

    def pay_for_work(self):
        """Начисляет оплату за работу исполнителю и переводит работу в статус paid."""
        current_item = self.request_list.currentItem()
        if current_item and "Статус: done" in current_item.text():
            request_id = int(current_item.text().split(",")[0].split(":")[1].strip())
            work = self.extra_work_dao.get_extra_work(request_id)
            if work:
                worker = self.worker_dao.get_worker(work[4])
                if worker:
                    work_type = self.work_type_dao.get_extra_work_type(work[5])
                    if work_type:
                        payment = work_type[2]  # Получаем сумму оплаты из поля payment
                        new_balance = getattr(worker, 'balance', 0.0) + payment
                        self.worker_dao.update_worker_balance(worker.id, new_balance)
                        self.extra_work_dao.update_extra_work(request_id, status="paid")
                        self.worker_name_field.setText(f"{worker.full_name} - Баланс обновлен")
                        self.load_requests()

    def closeEvent(self, event):
        """Закрывает соединение с базой данных при закрытии окна."""
        self.extra_work_dao.close()
        self.worker_dao.close()
        event.accept()