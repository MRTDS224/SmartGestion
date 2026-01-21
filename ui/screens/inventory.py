from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from data import crud, database

class InventoryScreen(MDScreen):
    dialog = None
    data_table = None
    selected_product_id = None
    dialog_mode = "add"

    def on_enter(self):
        self.load_table()

    def load_table(self):
        layout = self.ids.inventory_box
        layout.clear_widgets()
        
        main_box = MDBoxLayout(orientation="vertical", spacing=dp(10))
        
        # Actions Row
        action_box = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=dp(10))
        
        edit_btn = MDFillRoundFlatButton(text="MODIFIER", on_release=self.edit_selected)
        delete_btn = MDFillRoundFlatButton(text="SUPPRIMER", on_release=self.delete_selected, md_bg_color=(1, 0, 0, 1))
        
        action_box.add_widget(edit_btn)
        action_box.add_widget(delete_btn)
        
        main_box.add_widget(action_box)

        db = database.SessionLocal()
        products = crud.get_products(db)
        db.close()

        table_data = []
        for p in products:
            table_data.append((
                str(p.id),
                p.name,
                f"{p.stock_quantity}",
                f"{p.selling_price} GNF",
                p.category.name if p.category else "N/A"
            ))

        self.data_table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(1, 1),
            use_pagination=True,
            check=True,
            column_data=[
                ("ID", dp(10)),
                ("Nom", dp(30)),
                ("Stock", dp(15)),
                ("Prix", dp(20)),
                ("Catégorie", dp(20)),
            ],
            row_data=table_data,
        )
        self.data_table.bind(on_check_press=self.on_check_press)
        main_box.add_widget(self.data_table)
        
        layout.add_widget(main_box)

    def on_check_press(self, instance_table, current_row):
        if current_row:
             self.selected_product_id = int(current_row[0])
        else:
             self.selected_product_id = None

    def edit_selected(self, instance):
        if not self.selected_product_id:
            return
        
        db = database.SessionLocal()
        p = crud.get_product(db, self.selected_product_id)
        db.close()
        
        if not p:
            return

        self.show_add_product_dialog()
        content = self.dialog.content_cls
        content.ids.name.text = p.name
        content.ids.price.text = str(p.selling_price)
        content.ids.stock.text = str(p.stock_quantity)
        
        self.dialog_mode = "edit"
        self.dialog.title = "Modifier Produit"
        self.dialog.buttons[1].text = "SAUVEGARDER"

    def delete_selected(self, instance):
        if not self.selected_product_id:
            return
            
        db = database.SessionLocal()
        crud.delete_product(db, self.selected_product_id)
        db.close()
        self.selected_product_id = None
        self.load_table()

    def show_add_product_dialog(self):
        self.dialog_mode = "add"
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="Ajouter un Produit",
                type="custom",
                content_cls=AddProductContent(),
                buttons=[
                    MDFlatButton(
                        text="ANNULER",
                        on_release=self.close_dialog
                    ),
                    MDFillRoundFlatButton(
                        text="AJOUTER",
                        on_release=self.save_product
                    ),
                ],
            )
        else:
            self.dialog.title = "Ajouter un Produit"
            self.dialog.buttons[1].text = "AJOUTER"
            self.dialog.content_cls.ids.name.text = ""
            self.dialog.content_cls.ids.price.text = ""
            self.dialog.content_cls.ids.stock.text = ""
            
        self.dialog.open()

    def close_dialog(self, *args):
        try:
             self.dialog.dismiss()
        except:
             pass

    def save_product(self, *args):
        content = self.dialog.content_cls
        name = content.ids.name.text
        price = content.ids.price.text
        stock = content.ids.stock.text
        
        if not name or not price or not stock:
            return

        db = database.SessionLocal()
        
        try:
            if self.dialog_mode == "add":
                categories = crud.get_categories(db)
                if not categories:
                     crud.create_category(db, "General")
                     categories = crud.get_categories(db)
                cat_id = categories[0].id if categories else None 

                crud.create_product(db, {
                    "name": name,
                    "selling_price": float(price),
                    "stock_quantity": int(stock),
                    "category_id": cat_id
                })
            elif self.dialog_mode == "edit":
                 crud.update_product(db, self.selected_product_id, {
                    "name": name,
                    "selling_price": float(price),
                    "stock_quantity": int(stock)
                 })
        except Exception as e:
            print(f"Error saving product: {e}")
        finally:
            db.close()
            
        self.close_dialog()
        self.load_table()

class AddProductContent(MDBoxLayout):
    pass
