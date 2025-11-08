from PyQt6.QtWidgets import QMessageBox

class ItemHandler:
    def __init__(self, cursor, conn, parent):
        self.cursor = cursor
        self.conn = conn
        self.parent = parent
    
    def update_buy_price(self, item_id, new_price):
        try:
            self.cursor.execute("UPDATE item_template SET BuyPrice = %s WHERE entry = %s", (new_price, item_id))
            return self.cursor.rowcount
        except Exception as e:
            raise Exception(f"Update buy price failed: {e}")
    
    def get_item_info(self, item_id):
        try:
            self.cursor.execute("SELECT name, BuyPrice FROM item_template WHERE entry = %s", (item_id,))
            return self.cursor.fetchone()
        except Exception as e:
            raise Exception(f"Get item info failed: {e}")