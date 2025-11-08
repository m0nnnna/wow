import json
import os
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
import base64

class ConnectionDialog(QDialog):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("Database Connection")
        self.setModal(True)
        layout = QVBoxLayout()
        
        self.host_edit = QLineEdit()
        self.user_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_edit = QLineEdit()
        
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_edit)
        layout.addWidget(QLabel("User:"))
        layout.addWidget(self.user_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_edit)
        layout.addWidget(QLabel("Database:"))
        layout.addWidget(self.db_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        if config:
            self.host_edit.setText(config.get('host', 'localhost'))
            self.user_edit.setText(config.get('user', 'root'))
            self.db_edit.setText(config.get('database', 'acore_world'))
    
    def get_config(self):
        return {
            'host': self.host_edit.text(),
            'user': self.user_edit.text(),
            'password': self.password_edit.text(),
            'database': self.db_edit.text()
        }

class DBManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.config_file = 'db_config.enc.json'
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)
        
        self.conn = None
        self.cursor = None
        
        self.config = self._load_config()
        if not self.config:
            self._setup_connection()
        else:
            self._connect_db()
    
    def _get_or_create_key(self):
        key_file = 'encryption.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _encrypt_password(self, password):
        encrypted = self.fernet.encrypt(password.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt_password(self, encrypted_str):
        encrypted = base64.urlsafe_b64decode(encrypted_str.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode()
    
    def _load_config(self):
        if not os.path.exists(self.config_file):
            return None
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                decrypted_pass = self._decrypt_password(data['encrypted_password'])
                data['password'] = decrypted_pass
                del data['encrypted_password']
                return data
        except Exception as e:
            QMessageBox.warning(self.parent, "Warning", f"Failed to load config: {e}")
            return None
    
    def _save_config(self, config):
        temp_config = config.copy()
        encrypted_pass = self._encrypt_password(temp_config['password'])
        temp_config['encrypted_password'] = encrypted_pass
        del temp_config['password']
        with open(self.config_file, 'w') as f:
            json.dump(temp_config, f)
    
    def _setup_connection(self):
        dialog = ConnectionDialog(self.parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            self._save_config(config)
            self.config = config
            self._connect_db()
        else:
            raise SystemExit("Connection setup required.")
    
    def _connect_db(self):
        try:
            connect_kwargs = self.config.copy()
            connect_kwargs['auth_plugin'] = 'caching_sha2_password'
            self.conn = mysql.connector.connect(**connect_kwargs)
            self.cursor = self.conn.cursor()
            QMessageBox.information(self.parent, "Success", "Connected to database!")
        except Error as e:
            error_msg = str(e)
            if "caching_sha2_password" in error_msg:
                QMessageBox.critical(self.parent, "Error", 
                    f"Authentication plugin error: {error_msg}\n\n"
                    "Solutions:\n"
                    "1. Upgrade mysql-connector-python: pip install --upgrade mysql-connector-python\n"
                    "2. On MySQL server (as root): ALTER USER '{self.config['user']}'@'{self.config['host']}' "
                    "IDENTIFIED WITH mysql_native_password BY '{self.config['password']}'; FLUSH PRIVILEGES;\n"
                    "3. Try changing connection again.")
            else:
                QMessageBox.critical(self.parent, "Error", f"Database connection failed: {error_msg}")
            self._setup_connection()
    
    def change_connection(self, config):
        dialog = ConnectionDialog(self.parent, self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config = dialog.get_config()
            self._save_config(new_config)
            self.config = new_config
            if self.conn:
                self.conn.close()
            self._connect_db()
    
    def close(self):
        if self.conn:
            self.conn.close()