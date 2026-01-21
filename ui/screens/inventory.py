from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from data import crud, database
from kivymd.toast import toast

class InventoryListItem(TwoLineAvatarIconListItem):
    product_id = NumericProperty()
    screen = ObjectProperty()
    # text and secondary_text are inherited

class InventoryScreen(MDScreen):
    selected_product_id = None

    def on_enter(self):
        self.load_products()

    def load_products(self, search_text=""):
        db = database.SessionLocal()
        products = crud.get_products(db, search_text)
        db.close()
        
        data = []
        for p in products:
            data.append({
                "text": p.name,
                "secondary_text": f"Stock: {p.stock_quantity} | Prix: {p.selling_price} GNF",
                "product_id": p.id,
                "screen": self
            })
        
        self.ids.rv.data = data

    def on_select_product(self, product_id):
        self.selected_product_id = product_id
        
        db = database.SessionLocal()
        p = crud.get_product(db, product_id)
        db.close()
        
        if p:
            self.ids.form_title.text = f"Modifier: {p.name}"
            self.ids.form_name.text = p.name
            self.ids.form_price.text = str(p.selling_price)
            self.ids.form_stock.text = str(p.stock_quantity)
            self.ids.form_category.text = p.category.name if p.category else "N/A"
            self.ids.form_category.disabled = False # In full app, this would be a dropdown

    def clear_form(self):
        self.selected_product_id = None
        self.ids.form_title.text = "Nouveau Produit"
        self.ids.form_name.text = ""
        self.ids.form_price.text = ""
        self.ids.form_stock.text = ""
        self.ids.form_category.text = ""
        # self.ids.form_category.disabled = True # Maybe enable if we support adding categories

    def save_product(self):
        name = self.ids.form_name.text
        price = self.ids.form_price.text
        stock = self.ids.form_stock.text
        
        if not name or not price or not stock:
            toast("Veuillez remplir tous les champs")
            return

        try:
            db = database.SessionLocal()
            
            if self.selected_product_id:
                # UPDATE
                crud.update_product(db, self.selected_product_id, {
                    "name": name,
                    "selling_price": float(price),
                    "stock_quantity": int(stock)
                })
                toast("Produit modifié")
            else:
                # CREATE
                # Ensure category exists or use default
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
                toast("Produit créé")
            
            db.close()
            self.clear_form()
            self.load_products(self.ids.search_field.text) # Refresh list
            
        except Exception as e:
            toast(f"Erreur: {str(e)}")

    def delete_product(self):
        if not self.selected_product_id:
            return

        db = database.SessionLocal()
        crud.delete_product(db, self.selected_product_id)
        db.close()
        
        toast("Produit supprimé")
        self.clear_form()
        self.load_products(self.ids.search_field.text)
