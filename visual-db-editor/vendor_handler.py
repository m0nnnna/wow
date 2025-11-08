from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QTextEdit, QFormLayout, QPushButton, QDialogButtonBox

class DuplicateDialog(QDialog):
    def __init__(self, parent, duplicates_info):
        super().__init__(parent)
        self.setWindowTitle("Duplicate Slots Detected")
        self.setModal(True)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"Duplicates found for NPC {parent.current_npc_entry}:"))
        text_edit = QTextEdit()
        text_edit.setPlainText(duplicates_info)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        form_layout = QFormLayout()
        self.action_var = "renumber"
        renumber_btn = QPushButton("Renumber Slots (Assign unique 1,2,3...)")
        renumber_btn.clicked.connect(lambda: self.set_action("renumber"))
        warn_btn = QPushButton("Warn Only (No Changes)")
        warn_btn.clicked.connect(lambda: self.set_action("warn"))
        form_layout.addRow(renumber_btn)
        form_layout.addRow(warn_btn)
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def set_action(self, action):
        self.action_var = action
        QMessageBox.information(self, "Action Set", f"Will {action.replace('_', ' ')} on OK.")
    
    def get_action(self):
        return self.action_var

class VendorHandler:
    def __init__(self, cursor, conn, parent):
        self.cursor = cursor
        self.conn = conn
        self.parent = parent
        self.current_npc_entry = None
    
    def load_vendor(self, npc_id):
        try:
            self.current_npc_entry = int(npc_id)
            self.cursor.execute("""
                SELECT v.slot, v.item, i.name, i.BuyPrice, v.maxcount
                FROM npc_vendor v
                LEFT JOIN item_template i ON v.item = i.entry
                WHERE v.entry = %s
                ORDER BY v.slot, v.incrtime
            """, (self.current_npc_entry,))
            
            rows = self.cursor.fetchall()
            self._silent_check_duplicates()
            return rows
        except ValueError:
            raise ValueError("Invalid NPC ID")
        except Exception as e:
            raise Exception(f"Query failed: {e}")
    
    def _silent_check_duplicates(self):
        if not self.current_npc_entry:
            return
        try:
            self.cursor.execute("""
                SELECT slot, COUNT(*) as dup_count
                FROM npc_vendor
                WHERE entry = %s
                GROUP BY slot
                HAVING COUNT(*) > 1
            """, (self.current_npc_entry,))
            dups = self.cursor.fetchall()
            if dups:
                dup_info = "\n".join([f"Slot {slot}: {count} duplicates" for slot, count in dups])
                print(f"WARNING: Duplicates detected for NPC {self.current_npc_entry}:\n{dup_info}")
        except Exception as e:
            print(f"Duplicate check failed: {e}")
    
    def check_duplicates(self):
        if not self.current_npc_entry:
            return
        try:
            self.cursor.execute("""
                SELECT slot, COUNT(*) as dup_count
                FROM npc_vendor
                WHERE entry = %s
                GROUP BY slot
                HAVING COUNT(*) > 1
            """, (self.current_npc_entry,))
            dups = self.cursor.fetchall()
            if dups:
                dup_info = "\n".join([f"Slot {slot}: {count} duplicates" for slot, count in dups])
                dialog = DuplicateDialog(self.parent, dup_info)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    action = dialog.get_action()
                    if action == "renumber":
                        self.renumber_slots()
            else:
                QMessageBox.information(self.parent, "Info", "No duplicates found.")
        except Exception as e:
            QMessageBox.warning(self.parent, "Warning", f"Duplicate check failed: {e}")
    
    def renumber_slots(self):
        if not self.current_npc_entry:
            return
        try:
            self.cursor.execute("""
                SELECT item, ExtendedCost 
                FROM npc_vendor 
                WHERE entry = %s 
                ORDER BY slot, incrtime
            """, (self.current_npc_entry,))
            rows = self.cursor.fetchall()
            
            for i, (item, ext_cost) in enumerate(rows, 1):
                self.cursor.execute(
                    "UPDATE npc_vendor SET slot = %s WHERE entry = %s AND item = %s AND ExtendedCost = %s", 
                    (i, self.current_npc_entry, item, ext_cost)
                )
            
            self.conn.commit()
            updated = len(rows)
            QMessageBox.information(self.parent, "Renumbered", f"Renumbered {updated} slots to 1-{updated}. Reload vendor.")
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self.parent, "Error", f"Renumber failed: {e}")
    
    def add_item(self, item_id):
        try:
            self.cursor.execute("SELECT COALESCE(MAX(slot), 0) + 1 FROM npc_vendor WHERE entry = %s", (self.current_npc_entry,))
            slot = self.cursor.fetchone()[0]
            
            self.cursor.execute("""
                INSERT INTO npc_vendor (entry, slot, item, maxcount, incrtime, ExtendedCost)
                VALUES (%s, %s, %s, 0, 0, 0)
            """, (self.current_npc_entry, slot, item_id))
            self.conn.commit()
            return slot
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Add failed: {e}")
    
    def remove_item(self, slot, item_id):
        try:
            self.cursor.execute("DELETE FROM npc_vendor WHERE entry = %s AND item = %s AND ExtendedCost = 0", (self.current_npc_entry, item_id))
            deleted_count = self.cursor.rowcount
            self.conn.commit()
            return deleted_count
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Remove failed: {e}")
    
    def update_maxcount(self, slot, item_id, new_max):
        try:
            self.cursor.execute("UPDATE npc_vendor SET maxcount = %s WHERE entry = %s AND item = %s AND ExtendedCost = 0", (new_max, self.current_npc_entry, item_id))
            return self.cursor.rowcount
        except Exception as e:
            raise Exception(f"Update maxcount failed: {e}")