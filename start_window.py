from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox
from customer_request_widget import CustomerRequestWidget
from dao.worker import WorkerDAO
from manager_widget import ManagerWindow
from worker_window import WorkerWindow


class StartWindow(QMainWindow):
    manager_window: ManagerWindow
    customer_request_widget: CustomerRequestWidget
    worker_window: WorkerWindow

    def __init__(self, db_name='prod'):
        super().__init__()

        self.setWindowTitle("Выбор роли")
        self.setGeometry(100, 100, 300, 200)

        self.db_name = db_name

        # Создаем центральный виджет и устанавливаем его
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Создаем вертикальный лейаут
        layout = QVBoxLayout()

        # Создаем кнопки для выбора роли
        self.manager_button = QPushButton("Менеджер", self)
        self.customer_button = QPushButton("Заказчик", self)

        # Создаем комбобокс для выбора работника
        self.worker_combo = QComboBox(self)
        self.load_workers()

        # Кнопка для входа в окно работника
        self.worker_button = QPushButton("Работник", self)

        # Добавляем элементы в лейаут
        layout.addWidget(self.manager_button)
        layout.addWidget(self.customer_button)
        layout.addWidget(self.worker_combo)
        layout.addWidget(self.worker_button)

        # Устанавливаем лейаут для центрального виджета
        central_widget.setLayout(layout)

        # Подключаем кнопки к методам
        self.manager_button.clicked.connect(self.open_manager_window)
        self.customer_button.clicked.connect(self.open_customer_request_widget)
        self.worker_button.clicked.connect(self.open_worker_window)

    def load_workers(self):
        """Загружает список всех работников в комбобокс."""
        worker_dao = WorkerDAO(self.db_name)
        workers = worker_dao.get_all_workers()
        self.worker_map = {worker.full_name: worker.id for worker in workers}
        self.worker_combo.addItems(self.worker_map.keys())
        worker_dao.close()

    def open_manager_window(self):
        self.manager_window = ManagerWindow(self.db_name)
        self.manager_window.show()
        self.close()

    def open_customer_request_widget(self):
        self.customer_request_widget = CustomerRequestWidget(self.db_name)
        self.customer_request_widget.show()
        self.close()

    def open_worker_window(self):
        selected_worker_name = self.worker_combo.currentText()
        worker_id = self.worker_map.get(selected_worker_name)
        if worker_id is not None:
            self.worker_window = WorkerWindow(worker_id, self.db_name)
            self.worker_window.show()
            self.close()
