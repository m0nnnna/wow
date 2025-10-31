import sys
import re
import ast
import json
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton,
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QTabWidget, QFileDialog, QMessageBox, QInputDialog, QGroupBox
)
from PyQt6.QtCore import Qt

class DatabaseConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Configuration")
        self.layout = QFormLayout(self)
        
        self.host_edit = QLineEdit("localhost")
        self.layout.addRow("Host:", self.host_edit)
        self.user_edit = QLineEdit("root")
        self.layout.addRow("User:", self.user_edit)
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addRow("Password:", self.pass_edit)
        self.db_edit = QLineEdit("acore_world")
        self.layout.addRow("Database:", self.db_edit)
        
        buttons = QHBoxLayout()
        ok = QPushButton("Connect")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        self.layout.addRow(buttons)
    
    def get_config(self):
        return {
            'host': self.host_edit.text(),
            'user': self.user_edit.text(),
            'password': self.pass_edit.text(),
            'database': self.db_edit.text()
        }

class SearchItemDialog(QDialog):
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setWindowTitle("Search Items")
        self.layout = QVBoxLayout(self)
        
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_items)
        search_layout.addWidget(QLabel("Search Name:"))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        self.layout.addLayout(search_layout)
        
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["ID", "Name", "Quality"])
        self.results_table.itemDoubleClicked.connect(self.accept_selection)
        self.layout.addWidget(self.results_table)
        
        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        self.layout.addLayout(buttons)
        
        self.selected_id = None
    
    def search_items(self):
        query = self.search_edit.text().strip()
        if not query:
            return
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT entry, name, Quality 
                FROM item_template 
                WHERE name LIKE %s
                ORDER BY name
                LIMIT 100
            """, (f"%{query}%",))
            results = cursor.fetchall()
            cursor.close()
            self.results_table.setRowCount(0)
            for item in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(str(item['entry'])))
                self.results_table.setItem(row, 1, QTableWidgetItem(item['name']))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(item['Quality'])))
        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Error", f"Search failed: {e}")
    
    def accept_selection(self, item):
        row = item.row()
        id_item = self.results_table.item(row, 0)
        if id_item:
            self.selected_id = int(id_item.text())
            self.accept()

class BossEditorDialog(QDialog):
    def __init__(self, boss=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Boss")
        self.layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        self.layout.addRow("Name:", self.name_edit)
        
        self.criteria_id_spin = QSpinBox()
        self.criteria_id_spin.setRange(0, 1000000)
        self.layout.addRow("Criteria ID:", self.criteria_id_spin)
        
        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        self.layout.addRow(buttons)
        
        if boss:
            self.name_edit.setText(boss['name'])
            self.criteria_id_spin.setValue(boss['criteria_id'])
    
    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'criteria_id': self.criteria_id_spin.value()
        }

class SetItemsDialog(QDialog):
    def __init__(self, set_items, bosses, categories, parent=None):
        super().__init__(parent)
        self.bosses = bosses
        self.categories = categories
        self.setWindowTitle("Configure Set Rewards")
        self.layout = QVBoxLayout(self)
        
        # Category selection for the whole set
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        self.category_combo.setEditable(True)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        self.layout.addLayout(category_layout)
        
        self.table = QTableWidget(len(set_items), 5)
        self.table.setHorizontalHeaderLabels(["Item Name", "Item ID", "Boss", "Criteria ID", "Req Kills", "Stack Size"])
        for i, item in enumerate(set_items):
            self.table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.table.setItem(i, 1, QTableWidgetItem(str(item['entry'])))
            # Boss dropdown
            boss_combo = QComboBox()
            boss_combo.addItem("Select a boss...")
            for boss in self.bosses:
                boss_combo.addItem(f"{boss['name']} (Criteria: {boss['criteria_id']})", boss['criteria_id'])
            boss_combo.currentIndexChanged.connect(lambda index, row=i: self.update_criteria_id(row))
            self.table.setCellWidget(i, 2, boss_combo)
            criteria_id_item = QTableWidgetItem("0")
            criteria_id_item.setFlags(criteria_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
            self.table.setItem(i, 3, criteria_id_item)
            self.table.setItem(i, 4, QTableWidgetItem("25"))
            self.table.setItem(i, 5, QTableWidgetItem("1"))
        self.layout.addWidget(self.table)
        
        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        self.layout.addLayout(buttons)
    
    def update_criteria_id(self, row):
        boss_combo = self.table.cellWidget(row, 2)
        criteria_id = boss_combo.currentData()
        criteria_id_str = str(criteria_id) if criteria_id is not None else "0"
        self.table.item(row, 3).setText(criteria_id_str)
    
    def get_selected_category(self):
        return self.category_combo.currentText()
    
    def get_items(self):
        items = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            id_item = self.table.item(row, 1)
            boss_combo = self.table.cellWidget(row, 2)
            criteria_item = self.table.item(row, 3)
            kills_item = self.table.item(row, 4)
            stack_item = self.table.item(row, 5)
            if name_item and id_item and boss_combo and kills_item and stack_item:
                criteria_id = boss_combo.currentData()
                if criteria_id is None:
                    continue  # Skip if no boss selected
                boss_name = boss_combo.currentText().split(" (Criteria:")[0]
                items.append({
                    'name': name_item.text(),
                    'item_id': int(id_item.text() or 0),
                    'boss_name': boss_name,
                    'criteria_id': criteria_id,
                    'req_kills': int(kills_item.text() or 25),
                    'stack_size': int(stack_item.text() or 1)
                })
        return items

class MainWindow(QMainWindow):
    def __init__(self, reward=None, categories=[], bosses=[], db_connection=None, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.bosses = bosses
        
        self.setWindowTitle("Edit Reward")
        self.layout = QVBoxLayout(self)
        
        self.form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.form.addRow("Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["daily_gift", "one_time_level", "boss_kill"])
        self.type_combo.currentIndexChanged.connect(self.update_fields)
        self.form.addRow("Type:", self.type_combo)
        
        self.category_combo = QComboBox()
        # Load categories from categories.json
        try:
            with open('categories.json', 'r') as f:
                categories = json.load(f).get('categories', [])
        except Exception:
            categories = ['Uncategorized']
        self.category_combo.addItems(categories)
        self.category_combo.setEditable(True)
        self.form.addRow("Category:", self.category_combo)
        
        self.type_fields = QWidget()
        self.type_layout = QVBoxLayout(self.type_fields)
        self.form.addRow(self.type_fields)
        
        self.layout.addLayout(self.form)
        
        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        self.layout.addLayout(buttons)
        
        self.reward = reward or {}
        self.load_data()
        
    def update_fields(self):
        for i in reversed(range(self.type_layout.count())): 
            child = self.type_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        reward_type = self.type_combo.currentText()
        
        if reward_type == "daily_gift":
            self.reset_time_edit = QLineEdit()
            self.type_layout.addWidget(QLabel("Reset Time:"))
            self.type_layout.addWidget(self.reset_time_edit)
            
            self.timezone_edit = QLineEdit()
            self.type_layout.addWidget(QLabel("Timezone:"))
            self.type_layout.addWidget(self.timezone_edit)
            
        elif reward_type == "one_time_level":
            self.req_level_spin = QSpinBox()
            self.req_level_spin.setRange(1, 100)
            self.type_layout.addWidget(QLabel("Required Level:"))
            self.type_layout.addWidget(self.req_level_spin)
            
            self.gold_spin = QSpinBox()
            self.gold_spin.setRange(0, 100000000)
            self.type_layout.addWidget(QLabel("Reward Gold (copper):"))
            self.type_layout.addWidget(self.gold_spin)
            
            self.items_table = QTableWidget(0, 2)
            self.items_table.setHorizontalHeaderLabels(["Item ID", "Stack Size"])
            add_item_btn = QPushButton("Add Item")
            add_item_btn.clicked.connect(self.add_item_row)
            remove_item_btn = QPushButton("Remove Item")
            remove_item_btn.clicked.connect(self.remove_item_row)
            search_item_btn = QPushButton("Search Item")
            search_item_btn.clicked.connect(self.search_for_table_item)
            items_buttons = QHBoxLayout()
            items_buttons.addWidget(add_item_btn)
            items_buttons.addWidget(remove_item_btn)
            items_buttons.addWidget(search_item_btn)
            self.type_layout.addWidget(QLabel("Reward Items:"))
            self.type_layout.addWidget(self.items_table)
            self.type_layout.addLayout(items_buttons)
            
        elif reward_type == "boss_kill":
            self.req_kills_spin = QSpinBox()
            self.req_kills_spin.setRange(1, 100000)
            self.type_layout.addWidget(QLabel("Required Kills:"))
            self.type_layout.addWidget(self.req_kills_spin)
            
            self.bosses_table = QTableWidget(0, 2)
            self.bosses_table.setHorizontalHeaderLabels(["Boss Name", "Criteria ID"])
            add_boss_btn = QPushButton("Add Boss")
            add_boss_btn.clicked.connect(self.add_boss)
            remove_boss_btn = QPushButton("Remove Boss")
            remove_boss_btn.clicked.connect(self.remove_boss)
            bosses_buttons = QHBoxLayout()
            bosses_buttons.addWidget(add_boss_btn)
            bosses_buttons.addWidget(remove_boss_btn)
            self.type_layout.addWidget(QLabel("Bosses:"))
            self.type_layout.addWidget(self.bosses_table)
            self.type_layout.addLayout(bosses_buttons)
            
            item_id_layout = QHBoxLayout()
            self.reward_item_id_spin = QSpinBox()
            self.reward_item_id_spin.setRange(0, 100000)
            item_id_layout.addWidget(self.reward_item_id_spin)
            self.search_item_btn = QPushButton("Search")
            self.search_item_btn.clicked.connect(self.search_item)
            item_id_layout.addWidget(self.search_item_btn)
            self.type_layout.addWidget(QLabel("Reward Item ID:"))
            self.type_layout.addLayout(item_id_layout)
            
            self.stack_size_spin = QSpinBox()
            self.stack_size_spin.setRange(1, 1000)
            self.stack_size_spin.setValue(1)
            self.type_layout.addWidget(QLabel("Stack Size:"))
            self.type_layout.addWidget(self.stack_size_spin)
    
    def add_boss(self):
        dialog = BossEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_boss = dialog.get_data()
            if new_boss['name'] and new_boss['criteria_id'] > 0:
                self.bosses.append(new_boss)
                self.parent().save_bosses()
                row = self.bosses_table.rowCount()
                self.bosses_table.insertRow(row)
                self.bosses_table.setItem(row, 0, QTableWidgetItem(new_boss['name']))
                self.bosses_table.setItem(row, 1, QTableWidgetItem(str(new_boss['criteria_id'])))
    
    def remove_boss(self):
        row = self.bosses_table.currentRow()
        if row >= 0:
            self.bosses_table.removeRow(row)
    
    def add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setItem(row, 0, QTableWidgetItem("0"))
        self.items_table.setItem(row, 1, QTableWidgetItem("1"))
    
    def remove_item_row(self):
        row = self.items_table.currentRow()
        if row >= 0:
            self.items_table.removeRow(row)
    
    def search_for_table_item(self):
        if not self.db_connection:
            QMessageBox.warning(self, "Error", "Database not connected.")
            return
        search_dialog = SearchItemDialog(self.db_connection, self)
        if search_dialog.exec() == QDialog.DialogCode.Accepted and search_dialog.selected_id:
            row = self.items_table.currentRow()
            if row < 0:
                row = self.items_table.rowCount()
                self.items_table.insertRow(row)
                self.items_table.setItem(row, 1, QTableWidgetItem("1"))
            self.items_table.setItem(row, 0, QTableWidgetItem(str(search_dialog.selected_id)))
    
    def search_item(self):
        if not self.db_connection:
            QMessageBox.warning(self, "Error", "Database not connected.")
            return
        search_dialog = SearchItemDialog(self.db_connection, self)
        if search_dialog.exec() == QDialog.DialogCode.Accepted and search_dialog.selected_id:
            self.reward_item_id_spin.setValue(search_dialog.selected_id)
    
    def load_data(self):
        self.name_edit.setText(self.reward.get('name', ''))
        self.type_combo.setCurrentText(self.reward.get('type', 'daily_gift'))
        self.category_combo.setCurrentText(self.reward.get('category', ''))
        self.update_fields()
        
        reward_type = self.type_combo.currentText()
        if reward_type == "daily_gift":
            self.reset_time_edit.setText(self.reward.get('reset_time', ''))
            self.timezone_edit.setText(self.reward.get('timezone', ''))
        elif reward_type == "one_time_level":
            self.req_level_spin.setValue(self.reward.get('req_level', 1))
            self.gold_spin.setValue(self.reward.get('reward_gold', 0))
            item_ids = self.reward.get('reward_item_ids', [])
            stack_sizes = self.reward.get('stack_sizes', [])
            self.items_table.setRowCount(len(item_ids))
            for i in range(len(item_ids)):
                self.items_table.setItem(i, 0, QTableWidgetItem(str(item_ids[i])))
                self.items_table.setItem(i, 1, QTableWidgetItem(str(stack_sizes[i] if i < len(stack_sizes) else 1)))
        elif reward_type == "boss_kill":
            self.req_kills_spin.setValue(self.reward.get('req_kills', 1))
            self.reward_item_id_spin.setValue(self.reward.get('reward_item_id', 0))
            self.stack_size_spin.setValue(self.reward.get('stack_size', 1))
            criteria_ids = self.reward.get('criteria_ids', [])
            boss_names = self.reward.get('boss_names', [])
            self.bosses_table.setRowCount(len(criteria_ids))
            for i, (criteria_id, boss_name) in enumerate(zip(criteria_ids, boss_names)):
                self.bosses_table.setItem(i, 0, QTableWidgetItem(boss_name))
                self.bosses_table.setItem(i, 1, QTableWidgetItem(str(criteria_id)))
    
    def get_data(self):
        data = {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'category': self.category_combo.currentText()
        }
        reward_type = data['type']
        if reward_type == "daily_gift":
            data['reset_time'] = self.reset_time_edit.text()
            data['timezone'] = self.timezone_edit.text()
        elif reward_type == "one_time_level":
            data['req_level'] = self.req_level_spin.value()
            data['reward_gold'] = self.gold_spin.value()
            item_ids = []
            stack_sizes = []
            for row in range(self.items_table.rowCount()):
                item_id_item = self.items_table.item(row, 0)
                stack_item = self.items_table.item(row, 1)
                item_id = int(item_id_item.text() if item_id_item else 0)
                stack_size = int(stack_item.text() if stack_item else 1)
                if item_id > 0:
                    item_ids.append(item_id)
                    stack_sizes.append(stack_size)
            if item_ids:
                data['reward_item_ids'] = item_ids
                data['stack_sizes'] = stack_sizes
        elif reward_type == "boss_kill":
            data['req_kills'] = self.req_kills_spin.value()
            criteria_ids = []
            boss_names = []
            for row in range(self.bosses_table.rowCount()):
                name_item = self.bosses_table.item(row, 0)
                criteria_item = self.bosses_table.item(row, 1)
                if name_item and criteria_item:
                    criteria_id = int(criteria_item.text() or 0)
                    if criteria_id > 0:
                        criteria_ids.append(criteria_id)
                        boss_names.append(name_item.text())
            data['criteria_ids'] = criteria_ids
            data['boss_names'] = boss_names
            data['reward_item_id'] = self.reward_item_id_spin.value()
            data['stack_size'] = self.stack_size_spin.value()
        return data

class TieredItemsWidget(QWidget):
    def __init__(self, items, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(title))
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Level", "Item ID"])
        self.layout.addWidget(self.table)
        buttons = QHBoxLayout()
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_row)
        remove_btn = QPushButton("Remove Row")
        remove_btn.clicked.connect(self.remove_row)
        buttons.addWidget(add_btn)
        buttons.addWidget(remove_btn)
        self.layout.addLayout(buttons)
        self.load_items(items)
    
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("1"))
        self.table.setItem(row, 1, QTableWidgetItem("0"))
    
    def remove_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
    
    def load_items(self, items):
        self.table.setRowCount(0)
        levels = sorted(items.keys())
        for level in levels:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(level)))
            self.table.setItem(row, 1, QTableWidgetItem(str(items[level])))
    
    def get_items(self):
        items = {}
        for row in range(self.table.rowCount()):
            level_item = self.table.item(row, 0)
            item_id_item = self.table.item(row, 1)
            if level_item and item_id_item:
                level = int(level_item.text() or 0)
                item_id = int(item_id_item.text() or 0)
                if level > 0 and item_id > 0:
                    items[level] = item_id
        return items

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WoW Reward Editor")
        self.resize(800, 600)
        
        self.db_config = None
        self.db_connection = None
        self.bosses = []
        self.categories = []
        self.load_bosses()
        self.load_categories()
        
        self.central = QWidget()
        self.layout = QVBoxLayout(self.central)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Rewards Tab
        self.rewards_tab = QWidget()
        self.rewards_layout = QVBoxLayout(self.rewards_tab)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Categories / Rewards"])
        self.rewards_layout.addWidget(self.tree)
        buttons = QHBoxLayout()
        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_category)
        self.add_reward_btn = QPushButton("Add Reward")
        self.add_reward_btn.clicked.connect(self.add_reward)
        self.add_set_btn = QPushButton("Add Item Set")
        self.add_set_btn.clicked.connect(self.add_item_set)
        self.edit_reward_btn = QPushButton("Edit Reward")
        self.edit_reward_btn.clicked.connect(self.edit_reward)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        buttons.addWidget(self.add_category_btn)
        buttons.addWidget(self.add_reward_btn)
        buttons.addWidget(self.add_set_btn)
        buttons.addWidget(self.edit_reward_btn)
        buttons.addWidget(self.delete_btn)
        self.rewards_layout.addLayout(buttons)
        self.tabs.addTab(self.rewards_tab, "Rewards")
        
        # Daily Gift Items Tab
        self.daily_tab = QWidget()
        self.daily_layout = QVBoxLayout(self.daily_tab)
        self.health_pots = TieredItemsWidget({}, "Health Pots")
        self.daily_layout.addWidget(self.health_pots)
        self.mana_pots = TieredItemsWidget({}, "Mana Pots")
        self.daily_layout.addWidget(self.mana_pots)
        self.foods = TieredItemsWidget({}, "Foods")
        self.daily_layout.addWidget(self.foods)
        self.tabs.addTab(self.daily_tab, "Daily Gift Items")
        
        # Bosses Tab
        self.bosses_tab = QWidget()
        self.bosses_layout = QVBoxLayout(self.bosses_tab)
        self.bosses_table = QTableWidget(0, 2)
        self.bosses_table.setHorizontalHeaderLabels(["Name", "Criteria ID"])
        self.bosses_layout.addWidget(self.bosses_table)
        bosses_buttons = QHBoxLayout()
        add_boss_btn = QPushButton("Add Boss")
        add_boss_btn.clicked.connect(self.add_boss_global)
        edit_boss_btn = QPushButton("Edit Boss")
        edit_boss_btn.clicked.connect(self.edit_boss_global)
        delete_boss_btn = QPushButton("Delete Boss")
        delete_boss_btn.clicked.connect(self.delete_boss_global)
        bosses_buttons.addWidget(add_boss_btn)
        bosses_buttons.addWidget(edit_boss_btn)
        bosses_buttons.addWidget(delete_boss_btn)
        self.bosses_layout.addLayout(bosses_buttons)
        self.tabs.addTab(self.bosses_tab, "Bosses")
        self.load_bosses_table()
        
        self.setCentralWidget(self.central)
        
        # Data
        self.rewards = {}
        self.health_pots_dict = {}
        self.mana_pots_dict = {}
        self.foods_dict = {}
        self.file_path = None
        
        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        open_action = file_menu.addAction("Open PHP File")
        open_action.triggered.connect(self.open_file)
        save_action = file_menu.addAction("Save PHP File")
        save_action.triggered.connect(self.save_file)
        db_action = file_menu.addAction("Configure Database")
        db_action.triggered.connect(self.configure_db)
    
    def load_categories(self):
        try:
            with open('categories.json', 'r') as f:
                data = json.load(f)
                self.categories = data.get('categories', ['Uncategorized'])
        except Exception:
            self.categories = ['Uncategorized']
            self.save_categories()
    
    def save_categories(self):
        try:
            with open('categories.json', 'w') as f:
                json.dump({'categories': self.categories}, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save categories.json: {e}")
    
    def load_bosses(self):
        try:
            with open('bosses.json', 'r') as f:
                data = json.load(f)
                self.bosses = data['bosses']
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load bosses.json: {e}")
            self.bosses = []
    
    def save_bosses(self):
        try:
            with open('bosses.json', 'w') as f:
                json.dump({'bosses': self.bosses}, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save bosses.json: {e}")
    
    def load_bosses_table(self):
        self.bosses_table.setRowCount(len(self.bosses))
        for i, boss in enumerate(self.bosses):
            self.bosses_table.setItem(i, 0, QTableWidgetItem(boss['name']))
            self.bosses_table.setItem(i, 1, QTableWidgetItem(str(boss['criteria_id'])))
    
    def add_boss_global(self):
        dialog = BossEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_boss = dialog.get_data()
            if new_boss['name'] and new_boss['criteria_id'] > 0:
                self.bosses.append(new_boss)
                self.save_bosses()
                self.load_bosses_table()
    
    def edit_boss_global(self):
        row = self.bosses_table.currentRow()
        if row < 0:
            return
        boss = self.bosses[row]
        dialog = BossEditorDialog(boss, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_boss = dialog.get_data()
            self.bosses[row] = updated_boss
            self.save_bosses()
            self.load_bosses_table()
    
    def delete_boss_global(self):
        row = self.bosses_table.currentRow()
        if row < 0:
            return
        del self.bosses[row]
        self.save_bosses()
        self.load_bosses_table()
    
    def parse_content(self, content):
        self.rewards = self.parse_php_array(content, 'rewards')
        self.health_pots_dict = self.parse_php_array(content, 'health_pots')
        self.mana_pots_dict = self.parse_php_array(content, 'mana_pots')
        self.foods_dict = self.parse_php_array(content, 'foods')
    
    def add_category(self):
        name, ok = QInputDialog.getText(self, "Add Category", "Category Name:")
        if ok and name and name not in self.categories:
            self.categories.append(name)
            self.save_categories()
            self.load_tree()
    
    def add_reward(self):
        selected = self.tree.currentItem()
        category = ''
        if selected:
            user_data = selected.data(0, Qt.ItemDataRole.UserRole)
            if user_data and user_data.get('type') == 'category':
                category = selected.text(0)
            elif selected.parent():
                category = selected.parent().text(0)
        dialog = RewardEditorDialog(reward=None, categories=self.categories, bosses=self.bosses, db_connection=self.db_connection, parent=self)
        dialog.category_combo.setCurrentText(category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Error", "Name is required.")
                return
            max_key = max(self.rewards.keys()) + 1 if self.rewards else 1
            self.rewards[max_key] = data
            if data['category'] and data['category'] not in self.categories:
                self.categories.append(data['category'])
                self.save_categories()
            self.load_tree()
    
    def edit_reward(self):
        selected = self.tree.currentItem()
        if not selected:
            return
        user_data = selected.data(0, Qt.ItemDataRole.UserRole)
        if not user_data or user_data.get('type') != 'reward':
            return
        key = user_data['key']
        dialog = RewardEditorDialog(self.rewards[key], self.categories, self.bosses, self.db_connection, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.rewards[key] = data
            if data['category'] and data['category'] not in self.categories:
                self.categories.append(data['category'])
                self.save_categories()
            self.load_tree()
    
    def load_tree(self):
        self.tree.clear()
        categories = {}
        for cat in self.categories:
            cat_item = QTreeWidgetItem([cat])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'category', 'name': cat})
            self.tree.addTopLevelItem(cat_item)
            categories[cat] = cat_item
        for key, reward in sorted(self.rewards.items(), key=lambda x: x[0]):
            cat = reward.get('category', 'Uncategorized')
            if cat not in categories:
                cat_item = QTreeWidgetItem([cat])
                cat_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'category', 'name': cat})
                self.tree.addTopLevelItem(cat_item)
                categories[cat] = cat_item
                if cat not in self.categories:
                    self.categories.append(cat)
                    self.save_categories()
            reward_item = QTreeWidgetItem([reward['name']])
            reward_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'reward', 'key': key})
            categories[cat].addChild(reward_item)
        self.tree.expandAll()
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PHP File", "", "PHP Files (*.php)")
        if file_path:
            self.file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not read file: {e}")
                    return
            self.parse_content(content)
            existing_categories = set(self.categories)
            for reward in self.rewards.values():
                cat = reward.get('category', 'Uncategorized')
                if cat and cat not in existing_categories:
                    self.categories.append(cat)
                    existing_categories.add(cat)
            self.save_categories()
            self.load_tree()
            self.health_pots.load_items(self.health_pots_dict)
            self.mana_pots.load_items(self.mana_pots_dict)
            self.foods.load_items(self.foods_dict)
    
    def configure_db(self):
        dialog = DatabaseConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.db_config = dialog.get_config()
            try:
                self.db_connection = mysql.connector.connect(**self.db_config)
                QMessageBox.information(self, "Success", "Database connected successfully.")
            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to connect to database: {e}")
                self.db_connection = None
    
    def add_item_set(self):
        if not self.db_connection:
            QMessageBox.warning(self, "Error", "Please configure and connect to the database first.")
            return
        
        set_name, ok = QInputDialog.getText(self, "Add Item Set", "Enter set name (e.g., Wildheart):")
        if not ok or not set_name:
            return
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT DISTINCT itemset 
                FROM item_template 
                WHERE name LIKE %s AND itemset > 0
                LIMIT 1
            """, (f"%{set_name}%",))
            set_id = cursor.fetchone()
            
            if not set_id:
                QMessageBox.warning(self, "Error", f"No item set found for '{set_name}'. Try a more specific name.")
                cursor.close()
                return
            
            set_id = set_id['itemset']
            
            cursor.execute("""
                SELECT entry, name 
                FROM item_template 
                WHERE itemset = %s AND quality >= 2
                ORDER BY name
            """, (set_id,))
            set_items = cursor.fetchall()
            cursor.close()
            
            if not set_items:
                QMessageBox.warning(self, "Error", f"No items found for set ID {set_id}.")
                return
            
            dialog = SetItemsDialog(set_items, self.bosses, self.categories, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                items = dialog.get_items()
                category = dialog.get_selected_category()
                if not category:
                    category = f"{set_name} Rewards"
                max_key = max(self.rewards.keys()) if self.rewards else 0
                for item in items:
                    if item['item_id'] > 0 and item['boss_name'] and item['criteria_id'] > 0:
                        max_key += 1
                        self.rewards[max_key] = {
                            'name': f"{item['name']} Reward",
                            'type': 'boss_kill',
                            'req_kills': item['req_kills'],
                            'criteria_id': item['criteria_id'],
                            'boss_name': item['boss_name'],
                            'reward_item_id': item['item_id'],
                            'stack_size': item['stack_size'],
                            'category': category
                        }
                if category not in self.categories:
                    self.categories.append(category)
                    self.save_categories()
                self.load_tree()
                QMessageBox.information(self, "Success", f"Added {len(items)} rewards to '{category}' category.")
        
        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Error", f"Database error: {e}")
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PHP File", "", "PHP Files (*.php)")
        if file_path:
            self.file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not read file: {e}")
                    return
            self.parse_content(content)
            self.load_tree()
            self.health_pots.load_items(self.health_pots_dict)
            self.mana_pots.load_items(self.mana_pots_dict)
            self.foods.load_items(self.foods_dict)
    
    def save_file(self):
        if not self.file_path:
            self.file_path, _ = QFileDialog.getSaveFileName(self, "Save PHP File", "", "PHP Files (*.php)")
        if self.file_path:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(self.file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except FileNotFoundError:
                    content = "<?php\n\n"
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not read file for saving: {e}")
                    return
            content = self.replace_array(content, 'rewards', self.rewards)
            content = self.replace_array(content, 'health_pots', self.health_pots.get_items())
            content = self.replace_array(content, 'mana_pots', self.mana_pots.get_items())
            content = self.replace_array(content, 'foods', self.foods.get_items())
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            QMessageBox.information(self, "Saved", "File saved successfully.")
    
    def parse_content(self, content):
        self.rewards = self.parse_php_array(content, 'rewards')
        self.health_pots_dict = self.parse_php_array(content, 'health_pots')
        self.mana_pots_dict = self.parse_php_array(content, 'mana_pots')
        self.foods_dict = self.parse_php_array(content, 'foods')
    
    def parse_php_array(self, content, var_name):
        pattern = re.compile(rf'\${var_name}\s*=\s*\[(.*?)\];', re.DOTALL)
        match = pattern.search(content)
        if not match:
            return {}
        
        array_str = match.group(1)
        array_str = re.sub(r'//.*?(?=\n|$)', '', array_str, flags=re.MULTILINE)
        array_str = re.sub(r'/\*.*?\*/', '', array_str, flags=re.DOTALL)
        array_str = re.sub(r',(\s*[}\]])', r'\1', array_str)
        array_str = array_str.replace('=>', ':')
        
        is_simple = var_name in ['health_pots', 'mana_pots', 'foods']
        
        if is_simple:
            array_str = '{' + array_str + '}'
            array_str = re.sub(r"(\d+):", r"\1:", array_str)
            array_str = re.sub(r":\s*(\d+),", r": \1,", array_str)
        else:
            lines = array_str.split('\n')
            python_str = '['
            current_entry = None
            for line in lines:
                line = line.strip()
                if not line or line == ',':
                    continue
                if re.match(r'^\d+\s*:\s*\[', line):
                    if current_entry is not None:
                        python_str += current_entry.rstrip(',') + '},'
                    current_entry = '{'
                    continue
                if line in [']', '],']:
                    if current_entry is not None:
                        python_str += current_entry.rstrip(',') + '},'
                        current_entry = None
                    continue
                if ':' in line:
                    try:
                        key, value = line.split(':', 1)
                        key = key.strip().strip("'")
                        value = value.strip()
                        value = value.rstrip(',')
                        if value.startswith('[') and value.endswith(']'):
                            pass
                        elif value.strip("'").isdigit():
                            value = value.strip("'")
                        else:
                            value = value.strip("'")
                            value = f"'{value.replace("'", "\\'")}'"
                        if current_entry is not None:
                            current_entry += f"'{key}': {value},"
                    except ValueError:
                        continue
            if current_entry is not None:
                python_str += current_entry.rstrip(',') + '}'
            python_str += ']'
            array_str = re.sub(r',\s*}', '}', python_str)
            array_str = re.sub(r',\s*]', ']', array_str)
        
        try:
            parsed = ast.literal_eval(array_str)
            if is_simple and isinstance(parsed, dict):
                return parsed
            elif not is_simple and isinstance(parsed, list):
                result = {}
                for i, item in enumerate(parsed, 1):
                    if isinstance(item, dict):
                        result[i] = item
                return result
            return {}
        except Exception as e:
            with open('parse_error.log', 'w', encoding='utf-8') as f:
                f.write(f"Error parsing {var_name}: {e}\n\n{array_str}")
            QMessageBox.warning(self, "Parse Error", f"Error parsing {var_name}: {e}\nTry manual edit. See parse_error.log for details.")
            return {}
    
    def replace_array(self, content, var_name, data):
        pattern = re.compile(rf'(\${var_name}\s*=\s*)\[(.*?)\];', re.DOTALL)
        match = pattern.search(content)
        php_str = self.dict_to_php(data)
        
        if match:
            # Preserve the variable declaration and replace only the array content
            return pattern.sub(r'\1[' + php_str + '];', content)
        else:
            # If the array doesn't exist, append it after the last variable or at the end of PHP code
            new_array = f"\n${var_name} = [\n{php_str}\n];"
            # Find the last variable declaration
            last_var_pattern = re.compile(r'\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*.*?;\n', re.DOTALL)
            last_match = None
            for match in last_var_pattern.finditer(content):
                last_match = match
            if last_match:
                insert_pos = last_match.end()
                return content[:insert_pos] + new_array + content[insert_pos:]
            else:
                # If no variables found, append after the opening <?php tag
                return content.rstrip() + new_array + "\n?>"
    
    def dict_to_php(self, d, indent=4):
        if not d:
            return ''
        lines = []
        space = ' ' * indent
        items = sorted(d.items(), key=lambda x: x[0])
        for k, v in items:
            key_str = str(k) if isinstance(k, (int, float)) else f"'{k}'"
            if isinstance(v, dict):
                val_str = self.dict_to_php(v, indent + 4)
                lines.append(f"{space}{key_str} => [\n{val_str}\n{space}],")
            elif isinstance(v, list):
                val_items = []
                for vi in v:
                    if isinstance(vi, str):
                        val_items.append(f"'{vi}'")
                    elif isinstance(vi, int):
                        val_items.append(str(vi))
                    else:
                        val_items.append(repr(vi))
                val_str = '[' + ', '.join(val_items) + ']'
                lines.append(f"{space}{key_str} => {val_str},")
            elif isinstance(v, str):
                val_str = f"'{v}'"
                lines.append(f"{space}{key_str} => {val_str},")
            else:
                val_str = str(v)
                lines.append(f"{space}{key_str} => {val_str},")
        return '\n'.join(lines).rstrip(',')
    
    def load_tree(self):
        self.tree.clear()
        categories = {}
        for key, reward in sorted(self.rewards.items(), key=lambda x: x[0]):
            cat = reward.get('category', 'Uncategorized')
            if cat not in categories:
                cat_item = QTreeWidgetItem([cat])
                cat_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'category', 'name': cat})
                self.tree.addTopLevelItem(cat_item)
                categories[cat] = cat_item
            reward_item = QTreeWidgetItem([reward['name']])
            reward_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'reward', 'key': key})
            categories[cat].addChild(reward_item)
        self.tree.expandAll()
    
    def add_category(self):
        name, ok = QInputDialog.getText(self, "Add Category", "Category Name:")
        if ok and name and name not in self.categories:
            self.categories.append(name)
            self.save_categories()
            self.load_tree()
    
    def add_reward(self):
        selected = self.tree.currentItem()
        category = ''
        if selected:
            user_data = selected.data(0, Qt.ItemDataRole.UserRole)
            if user_data and user_data.get('type') == 'category':
                category = selected.text(0)
            elif selected.parent():
                category = selected.parent().text(0)
        dialog = RewardEditorDialog(categories=self.categories, bosses=self.bosses, db_connection=self.db_connection, parent=self)
        dialog.category_combo.setCurrentText(category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Error", "Name is required.")
                return
            max_key = max(self.rewards.keys()) + 1 if self.rewards else 1
            self.rewards[max_key] = data
            # Add new category to categories.json if not already present
            if data['category'] and data['category'] not in self.categories:
                self.categories.append(data['category'])
                self.save_categories()
            self.load_tree()
    
    def load_tree(self):
        self.tree.clear()
        categories = {}
        # Ensure all categories from categories.json are shown, even if empty
        for cat in self.categories:
            cat_item = QTreeWidgetItem([cat])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'category', 'name': cat})
            self.tree.addTopLevelItem(cat_item)
            categories[cat] = cat_item
        # Add rewards under their respective categories
        for key, reward in sorted(self.rewards.items(), key=lambda x: x[0]):
            cat = reward.get('category', 'Uncategorized')
            if cat not in categories:
                cat_item = QTreeWidgetItem([cat])
                cat_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'category', 'name': cat})
                self.tree.addTopLevelItem(cat_item)
                categories[cat] = cat_item
                if cat not in self.categories:
                    self.categories.append(cat)
                    self.save_categories()
            reward_item = QTreeWidgetItem([reward['name']])
            reward_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'reward', 'key': key})
            categories[cat].addChild(reward_item)
        self.tree.expandAll()
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PHP File", "", "PHP Files (*.php)")
        if file_path:
            self.file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not read file: {e}")
                    return
            self.parse_content(content)
            # Update categories.json with any new categories from rewards
            existing_categories = set(self.categories)
            for reward in self.rewards.values():
                cat = reward.get('category', 'Uncategorized')
                if cat and cat not in existing_categories:
                    self.categories.append(cat)
                    existing_categories.add(cat)
            self.save_categories()
            self.load_tree()
            self.health_pots.load_items(self.health_pots_dict)
            self.mana_pots.load_items(self.mana_pots_dict)
            self.foods.load_items(self.foods_dict)
    
    def edit_reward(self):
        selected = self.tree.currentItem()
        if not selected:
            return
        user_data = selected.data(0, Qt.ItemDataRole.UserRole)
        if not user_data or user_data.get('type') != 'reward':
            return
        key = user_data['key']
        categories = list(set(r.get('category', '') for r in self.rewards.values()))
        dialog = RewardEditorDialog(self.rewards[key], categories, self.bosses, self.db_connection, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.rewards[key] = dialog.get_data()
            self.load_tree()
    
    def delete_selected(self):
        selected = self.tree.currentItem()
        if not selected:
            return
        user_data = selected.data(0, Qt.ItemDataRole.UserRole)
        if user_data and user_data.get('type') == 'reward':
            del self.rewards[user_data['key']]
        elif user_data and user_data.get('type') == 'category':
            for i in range(selected.childCount()):
                child = selected.child(i)
                child_user_data = child.data(0, Qt.ItemDataRole.UserRole)
                if child_user_data and child_user_data.get('type') == 'reward':
                    del self.rewards[child_user_data['key']]
        self.load_tree()
    
    def closeEvent(self, event):
        if self.db_connection:
            self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())