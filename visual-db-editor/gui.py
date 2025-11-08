import sys
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QDialogButtonBox, QMessageBox, 
                             QInputDialog, QAbstractItemView)
from PyQt6.QtCore import Qt
from db_config import DBManager
from vendor_handler import VendorHandler
from item_handler import ItemHandler

class WoWVendorEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WoW Vendor Editor")
        self.setGeometry(100, 100, 900, 700)
        
        self.db_manager = DBManager(self)
        self.vendor_handler = VendorHandler(self.db_manager.cursor, self.db_manager.conn, self)
        self.item_handler = ItemHandler(self.db_manager.cursor, self.db_manager.conn, self)
        
        self.current_npc_entry = None
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Connection frame
        conn_frame = QHBoxLayout()
        self.conn_btn = QPushButton("Change Connection")
        self.conn_btn.clicked.connect(self.change_connection)
        conn_frame.addWidget(self.conn_btn)
        conn_frame.addStretch()
        layout.addLayout(conn_frame)
        
        # NPC Entry Frame
        npc_frame = QHBoxLayout()
        npc_frame.addWidget(QLabel("NPC Entry ID:"))
        self.npc_entry = QLineEdit()
        self.npc_entry.returnPressed.connect(self.load_vendor)
        npc_frame.addWidget(self.npc_entry)
        load_btn = QPushButton("Load Vendor")
        load_btn.clicked.connect(self.load_vendor)
        npc_frame.addWidget(load_btn)
        npc_frame.addStretch()
        layout.addLayout(npc_frame)
        
        # Table for vendor items
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Slot', 'Item ID', 'Name', 'Buy Price', 'Max Count'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)
        
        # Buttons Frame
        btn_frame = QHBoxLayout()
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        btn_frame.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Item")
        remove_btn.clicked.connect(self.remove_item)
        btn_frame.addWidget(remove_btn)
        
        clean_btn = QPushButton("Clean Duplicates")
        clean_btn.clicked.connect(self.clean_duplicates)
        btn_frame.addWidget(clean_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        btn_frame.addWidget(save_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_vendor)
        btn_frame.addWidget(refresh_btn)
        
        btn_frame.addStretch()
        layout.addLayout(btn_frame)
    
    def change_connection(self):
        self.db_manager.change_connection(self.config)
    
    def load_vendor(self):
        npc_id = self.npc_entry.text().strip()
        if not npc_id:
            QMessageBox.warning(self, "Error", "Enter NPC Entry ID")
            return
        
        try:
            rows = self.vendor_handler.load_vendor(npc_id)
            self.table.setRowCount(0)
            self.table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val) if val is not None else "")
                    self.table.setItem(i, j, item)
            
            self.current_npc_entry = self.vendor_handler.current_npc_entry
            QMessageBox.information(self, "Success", f"Loaded {len(rows)} items for NPC {npc_id}")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def clean_duplicates(self):
        self.vendor_handler.check_duplicates()
    
    def add_item(self):
        if not self.current_npc_entry:
            QMessageBox.warning(self, "Error", "Load a vendor first")
            return
        
        item_id, ok = QInputDialog.getInt(self, "Add Item", "Item ID:", 0, 0, 999999)
        if ok and item_id:
            try:
                slot = self.vendor_handler.add_item(item_id)
                self.load_vendor()
                QMessageBox.information(self, "Success", f"Added item {item_id} at slot {slot}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def remove_item(self):
        if not self.current_npc_entry:
            QMessageBox.warning(self, "Error", "Load a vendor first")
            return
        
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Error", "Select an item to remove")
            return
        
        row = sel[0].row()
        slot_item = self.table.item(row, 0)
        item_id_item = self.table.item(row, 1)
        if not (slot_item and item_id_item):
            QMessageBox.warning(self, "Error", "Invalid selection")
            return
        
        try:
            slot = int(slot_item.text())
            item_id = int(item_id_item.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid slot or item ID")
            return
        
        if QMessageBox.question(self, "Confirm", f"Remove item {item_id} (slot {slot}) from vendor {self.current_npc_entry}?") == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = self.vendor_handler.remove_item(slot, item_id)
                if deleted_count == 0:
                    QMessageBox.warning(self, "Warning", "No matching row found. Possible data inconsistency or non-zero ExtendedCost.")
                elif deleted_count > 1:
                    QMessageBox.warning(self, "Warning", f"Deleted {deleted_count} rows (duplicates exist). Use 'Clean Duplicates' to fix.")
                else:
                    QMessageBox.information(self, "Success", "Item removed.")
                
                self.load_vendor()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def on_double_click(self, index):
        if not self.current_npc_entry:
            QMessageBox.warning(self, "Error", "Load a vendor first")
            return
        
        row = index.row()
        slot_item = self.table.item(row, 0)
        item_id_item = self.table.item(row, 1)
        buy_price_item = self.table.item(row, 3)
        max_count_item = self.table.item(row, 4)
        
        if not all([slot_item, item_id_item]):
            QMessageBox.warning(self, "Error", "Invalid selection")
            return
        
        try:
            slot = int(slot_item.text())
            item_id = int(item_id_item.text())
            current_price = int(buy_price_item.text()) if buy_price_item and buy_price_item.text().strip() else 0
            current_max = int(max_count_item.text()) if max_count_item and max_count_item.text().strip() else 0
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid numbers in row")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Item {item_id}")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Max Count:"))
        max_edit = QLineEdit(str(current_max))
        layout.addWidget(max_edit)
        
        layout.addWidget(QLabel("Buy Price:"))
        price_edit = QLineEdit(str(current_price))
        layout.addWidget(price_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                new_max = int(max_edit.text())
                new_price = int(price_edit.text())
                
                updated_vendor = self.vendor_handler.update_maxcount(slot, item_id, new_max)
                updated_item = self.item_handler.update_buy_price(item_id, new_price)
                
                self.db_manager.conn.commit()
                
                if updated_vendor != 1:
                    QMessageBox.warning(self, "Warning", f"Updated {updated_vendor} vendor rows. Check duplicates or ExtendedCost.")
                if updated_item != 1:
                    QMessageBox.warning(self, "Warning", f"Updated {updated_item} item templates. Item may not exist.")
                
                self.load_vendor()
                QMessageBox.information(self, "Success", "Changes saved")
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid numbers")
            except Exception as e:
                self.db_manager.conn.rollback()
                QMessageBox.critical(self, "Error", str(e))
    
    def save_changes(self):
        QMessageBox.information(self, "Info", "Changes are saved immediately on edit. Use Refresh to reload.")
    
    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()