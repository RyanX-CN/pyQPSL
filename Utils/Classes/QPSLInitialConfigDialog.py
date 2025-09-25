import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QListWidget, QPushButton, QFileDialog

class QPSLInitialConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conf_data = self.load_conf_file("Conf/config.json")
        self.setup_ui()
        self.setup_logic()
    
    def setup_ui(self):
        self.setWindowTitle("QPSL Initial Configuration Dialog")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select a imaging mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Non-specific Mode","3D SCI", "ETL LSFM", "Others"])
        layout.addWidget(self.mode_combo)

        layout.addWidget(QLabel("Select the devices:"))
        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.device_list)

        self.load_params_button = QPushButton("load config file")
        self.load_params_button.clicked.connect(self.load_params_file)
        layout.addWidget(self.load_params_button)

        self.confirm_button = QPushButton("confirm")
        self.confirm_button.clicked.connect(self.accept)
        layout.addWidget(self.confirm_button)

    def setup_logic(self):
        self.mode_combo.currentIndexChanged.connect(self.update_device_list)
    
    def load_conf_file(self, file_path):
        """加载配置文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {file_path} 未找到")
            return {}
        except json.JSONDecodeError:
            print(f"配置文件 {file_path} 格式错误")
            return {}

    def update_device_list(self):
        """根据模式选择更新设备列表"""
        selected_mode = self.mode_combo.currentText()
        devices = self.conf_data.get("Image Mode").get(selected_mode, [])
        self.device_list.clear()
        self.device_list.addItems(devices)
    
    def load_params_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择参数文件", "", "JSON Files (*.json)")
        if file_path:
            self.params_file = file_path
        else:
            self.params_file = None