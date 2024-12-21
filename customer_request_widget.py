from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QFormLayout, QComboBox, QScrollArea, QListWidgetItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer

from dao.extra_work import ExtraWorkDAO
from dao.type import ExtraWorkTypeDAO
from dao.worker import WorkerDAO


class CustomerRequestWidget(QWidget):

    extra_work_dao: ExtraWorkDAO
    work_type_dao: ExtraWorkTypeDAO
    worker_dao: WorkerDAO

    def __init__(self, db_name='prod'):
        super().__init__()

        self.setWindowTitle("Заявки")
        self.setGeometry(100, 100, 600, 400)

        # Инициализация DAO
        self.extra_work_dao: ExtraWorkDAO  = ExtraWorkDAO(db_name)
        self.work_type_dao: ExtraWorkTypeDAO = ExtraWorkTypeDAO(db_name)
        self.worker_dao: WorkerDAO = WorkerDAO(db_name)

        # Основной лейаут
        main_layout = QHBoxLayout()

        # Левый лейаут для списка заявок
        self.request_list = QListWidget()
        self.load_requests()
        main_layout.addWidget(self.request_list)

        # Правый лейаут для формы создания заявки
        form_layout = QFormLayout()

        # QComboBox для выбора типа работы
        self.work_type_combo = QComboBox()
        self.work_type_combo.currentIndexChanged.connect(self.display_work_type_description)

        # QScrollArea для описания
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        description_widget = QWidget()
        description_layout = QVBoxLayout()
        self.work_type_description = QLabel()
        self.work_type_description.setWordWrap(True)  # Включаем перенос текста
        description_layout.addWidget(self.work_type_description)
        description_widget.setLayout(description_layout)
        scroll_area.setWidget(description_widget)

        form_layout.addRow(QLabel("Тип работы"), self.work_type_combo)
        form_layout.addRow(QLabel("Описание"), scroll_area)

        self.send_request_button = QPushButton("Отправить запрос менеджеру")
        self.send_request_button.clicked.connect(self.send_request)

        form_layout.addWidget(self.send_request_button)

        main_layout.addLayout(form_layout)

        # Устанавливаем основной лейаут
        self.setLayout(main_layout)

        # Загружаем типы работ после инициализации всех виджетов
        self.load_work_types()

        # Устанавливаем таймер для автоматического обновления списка заявок
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_requests)
        self.timer.start(4000)  # Обновление каждые 4000 миллисекунд (4 секунды)

    def load_requests(self):
        """Загружает и отображает список всех заявок."""
        requests = self.extra_work_dao.get_all_extra_works()
        self.request_list.clear()
        for request in requests:
            extra_work_type_id = request[5]
            work_type = self.work_type_dao.get_extra_work_type(extra_work_type_id)
            work_type_name = work_type[3] if work_type else "Неизвестно"

            item_text = f"ID: {request[0]}, Клиент ID: {request[7]}, Тип Работы: {work_type_name}, Статус: {request[6]}"

            # Если работа в процессе, добавляем информацию о работнике
            if request[6] == "in progress":
                worker = self.worker_dao.get_worker(request[4])
                if worker:
                    worker_name = worker.full_name
                    worker_post = worker.post.title
                    item_text += f", Работник: {worker_name}, Квалификация: {worker_post}"

            # Если работа завершена или оплачена, добавляем время выполнения
            if request[6] in ["done", "paid"]:
                start_time = datetime.strptime(request[2], '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(request[3], '%Y-%m-%d %H:%M:%S')
                duration = end_time - start_time
                item_text += f", Время выполнения: {duration}"

            item = QListWidgetItem(item_text)

            # Устанавливаем цвет фона в зависимости от статуса
            if request[6] == "pending":
                item.setBackground(QColor("yellow"))
            elif request[6] == "in progress":
                item.setBackground(QColor("orange"))  # Изменяем цвет на оранжевый
            elif request[6] == "done":
                item.setBackground(QColor("green"))
            elif request[6] == "paid":
                item.setBackground(QColor("grey"))  # Цвет для оплаченной работы

            self.request_list.addItem(item)

    def load_work_types(self):
        """Загружает и отображает список всех типов работ."""
        work_types = self.work_type_dao.get_all_extra_work_types()
        self.work_type_combo.clear()
        self.work_type_map = {}
        for work_type in work_types:
            # Используем поле type для отображения в QComboBox
            work_type_display = work_type[3]  # Предполагаем, что поле type находится в work_type[3]
            self.work_type_combo.addItem(work_type_display)
            self.work_type_map[work_type_display] = work_type

        # Отобразить описание для первого элемента
        if work_types:
            self.display_work_type_description(0)

    def display_work_type_description(self, index):
        """Отображает описание выбранного типа работы."""
        work_type_display = self.work_type_combo.itemText(index)
        work_type = self.work_type_map.get(work_type_display)
        if work_type:
            self.work_type_description.setText(work_type[1])  # Отображаем описание

    def send_request(self):
        """Создает новую заявку и сохраняет ее в базе данных."""
        client_id = 0  # Фиксированный ID клиента
        work_type_display = self.work_type_combo.currentText()
        work_type = self.work_type_map.get(work_type_display)
        if work_type:
            extra_work_type_id = work_type[0]
            status = "pending"
            self.extra_work_dao.create_extra_work(
                type=work_type_display,
                start_time=None,
                end_time=None,
                assignee=None,
                extra_work_type_id=extra_work_type_id,
                status=status,
                client_id=client_id
            )
            self.load_requests()