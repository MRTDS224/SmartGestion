from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.properties import ObjectProperty, NumericProperty
from kivy.lang import Builder
from data import crud, database

# KV is in pos.kv

class ProductListItem(TwoLineAvatarIconListItem):
    product_id = NumericProperty()
    cost = NumericProperty()
    
    
    # on_release logic moved to POSScreen.load_products to avoid fragile parent access

class CartItem(MDCard):
    product_id = NumericProperty()
    quantity = NumericProperty(1)
    price = NumericProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = "50dp"
        self.padding = "5dp"

class POSScreen(MDScreen):
    cart = {} # dict product_id -> {qty, price, name}

    def on_enter(self):
        self.load_products()

    def load_products(self, search_text=""):
        product_list = self.ids.product_list
        product_list.clear_widgets()
        
        db = database.SessionLocal()
        products = crud.get_products(db, search_text)
        db.close()

        for p in products:
            if p.stock_quantity > 0:
                item = ProductListItem(
                    text=p.name,
                    secondary_text=f"{p.selling_price} GNF | Stock: {p.stock_quantity}",
                    product_id=p.id,
                    cost=p.selling_price
                )
                item.bind(on_release=lambda x, pid=p.id, name=p.name, price=p.selling_price: self.add_to_cart(pid, name, price))
                item.add_widget(ImageLeftWidget(source="assets/product_placeholder.png")) # Placeholder
                product_list.add_widget(item)

    def add_to_cart(self, product_id, name, price):
        if product_id in self.cart:
            self.cart[product_id]['qty'] += 1
        else:
            self.cart[product_id] = {'qty': 1, 'price': price, 'name': name}
        self.update_cart_ui()

    def update_cart_ui(self):
        cart_box = self.ids.cart_box
        cart_box.clear_widgets()
        
        total = 0
        for pid, item in self.cart.items():
            total += item['qty'] * item['price']
            
            # Simple UI for Cart Item
            item_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="40dp")
            item_box.add_widget(MDLabel(text=f"{item['name']} x{item['qty']}", size_hint_x=0.7))
            item_box.add_widget(MDLabel(text=f"{item['qty'] * item['price']}", size_hint_x=0.3))
            
            # Remove button
            btn = MDIconButton(icon="minus-circle", on_release=lambda x, pid=pid: self.remove_from_cart(pid))
            item_box.add_widget(btn)
            
            cart_box.add_widget(item_box)

        self.ids.total_label.text = f"Total: {total} GNF"

    def remove_from_cart(self, product_id):
        if product_id in self.cart:
            if self.cart[product_id]['qty'] > 1:
                self.cart[product_id]['qty'] -= 1
            else:
                del self.cart[product_id]
            self.update_cart_ui()

    def validate_sale(self):
        if not self.cart:
            toast("Panier vide")
            return
            
        items = []
        for pid, item in self.cart.items():
            items.append({'product_id': pid, 'quantity': item['qty']})
            
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            # Get user from session
            user_id = app.user_session.user.id if app.user_session.user else 1
            
            db = database.SessionLocal()
            crud.process_sale(db, user_id, items)
            toast("Vente validée!")
            
            self.cart = {}
            self.update_cart_ui()
            self.load_products() # Refresh stock
            
            # Refresh Dashboard
            app.refresh_dashboard()
            
            db.close()
        except Exception as e:
            toast(f"Erreur: {str(e)}")

