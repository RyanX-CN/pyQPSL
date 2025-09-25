from Tool import *

def load_params(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    ##=============== old version ===============
    main_window = QPSLMainWindow()
    main_window.show()
    ##=============== pre-configuration dialog version ===============
    # config_dialog = QPSLInitialConfigDialog()
    # if config_dialog.exec_() == QDialog.Accepted:
    #     mode = config_dialog.mode_combo.currentText()
    #     devices = [item.text() for item in config_dialog.device_list.selectedItems()]
    #     params_file = getattr(config_dialog, "params_file", None)
        
    #     params = load_params(params_file) if params_file else {}
        
    #     main_window = QPSLMainWindow()
    #     main_window.load_plugins(devices, config_dialog.conf_data ,params)
    #     main_window.show()
    sys.exit(app.exec())