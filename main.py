from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
import os

from data.database import SessionLocal, init_db
from data import crud

# Import Screens
from ui.screens.inventory import InventoryScreen
from ui.screens.pos import POSScreen

# Global user session
class UserSession:
    user = None

session = UserSession()

KV = '''
<LoginScreen>:
    name: "login"
    MDCard:
        size_hint: None, None
        size: "300dp", "400dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 10
        padding: "25dp"
        spacing: "25dp"
        orientation: 'vertical'

        MDLabel:
            id: welcome_label
            text: "Madina Stock"
            font_size: "40sp"
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1]
            padding_y: "15dp"

        MDTextField:
            id: user
            hint_text: "Utilisateur"
            icon_right: "account"
            size_hint_x: None
            width: "200dp"
            font_size: "18sp"
            pos_hint: {"center_x": 0.5}

        MDTextField:
            id: password
            hint_text: "Mot de passe"
            icon_right: "eye-off"
            size_hint_x: None
            width: "200dp"
            font_size: "18sp"
            password: True
            pos_hint: {"center_x": 0.5}

        MDFillRoundFlatButton:
            text: "CONNEXION"
            font_size: "12sp"
            pos_hint: {"center_x": 0.5}
            on_release: root.do_login()

<DashboardScreen>:
    name: "dashboard"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Tableau de Bord"
            left_action_items: [["menu", lambda x: app.root.get_screen("main").ids.nav_drawer.set_state("open")]]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "20dp"
            
            MDLabel:
                text: "Bienvenue sur Madina Stock"
                halign: "center"
                font_style: "H4"

            MDGridLayout:
                cols: 2
                spacing: "10dp"
                padding: "10dp"
                
                MDCard:
                    orientation: 'vertical'
                    padding: "10dp"
                    size_hint_y: None
                    height: "150dp"
                    MDLabel:
                        text: "Total Produits"
                        halign: "center"
                    MDLabel:
                        id: total_products
                        text: "--"
                        halign: "center"
                        font_style: "H3"
                
                MDCard:
                    orientation: 'vertical'
                    padding: "10dp"
                    size_hint_y: None
                    height: "150dp"
                    MDLabel:
                        text: "Ventes du Jour"
                        halign: "center"
                    MDLabel:
                        id: daily_sales
                        text: "-- GNF"
                        halign: "center"
                        font_style: "H3"

<MainScreen>:
    name: "main"
    
    MDNavigationLayout:
        
        MDScreenManager:
            id: inner_screen_manager
        
        MDNavigationDrawer:
            id: nav_drawer
            
            MDBoxLayout:
                orientation: 'vertical'
                padding: "8dp"
                spacing: "8dp"
                
                MDLabel:
                    text: "Madina Stock"
                    font_style: "Button"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    id: nav_username
                    text: "Utilisateur"
                    font_style: "Caption"
                    size_hint_y: None
                    height: self.texture_size[1]

                ScrollView:
                    MDList:
                        OneLineIconListItem:
                            text: "Tableau de Bord"
                            on_release: 
                                inner_screen_manager.current = "dashboard"
                                nav_drawer.set_state("close")
                            IconLeftWidget:
                                icon: "view-dashboard"

                        OneLineIconListItem:
                            text: "Inventaire"
                            on_release: 
                                inner_screen_manager.current = "inventory"
                                nav_drawer.set_state("close")
                            IconLeftWidget:
                                icon: "package-variant"

                        OneLineIconListItem:
                            text: "Vente (POS)"
                            on_release: 
                                inner_screen_manager.current = "pos"
                                nav_drawer.set_state("close")
                            IconLeftWidget:
                                icon: "point-of-sale"

                        OneLineIconListItem:
                            text: "Déconnexion"
                            on_release: 
                                app.logout()
                            IconLeftWidget:
                                icon: "logout"

MDScreenManager:
    LoginScreen:
    MainScreen:
'''

class LoginScreen(MDScreen):
    def do_login(self):
        username = self.ids.user.text
        password = self.ids.password.text
        
        db = SessionLocal()
        user = crud.get_user_by_username(db, username)
        db.close()

        if user and crud.verify_password(password, user.hashed_password):
            session.user = user
            self.manager.current = "main"
            self.manager.get_screen("main").ids.nav_username.text = f"{user.username} ({user.role})"
            MDApp.get_running_app().refresh_dashboard()
        else:
            self.show_error("Nom d'utilisateur ou mot de passe incorrect")

    def show_error(self, message):
        self.ids.welcome_label.text = message

class DashboardScreen(MDScreen):
    pass

class MainScreen(MDScreen):
    pass

class MadinaStockApp(MDApp):
    user_session = session

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        Window.size = (360, 640) # Mobile-like size for testing
        
        # Load external KVs
        Builder.load_file("ui/screens/inventory.kv")
        Builder.load_file("ui/screens/pos.kv")
        
        return Builder.load_string(KV)
    
    def on_start(self):        
        # Add screens to the nested ScreenManager inside MainScreen
        # Access the inner screen manager via MainScreen's ids
        main_screen = self.root.get_screen("main")
        inner_sm = main_screen.ids.inner_screen_manager
        
        inner_sm.add_widget(DashboardScreen(name="dashboard"))
        inner_sm.add_widget(InventoryScreen(name="inventory"))
        inner_sm.add_widget(POSScreen(name="pos"))
        
        # Set default screen
        inner_sm.current = "dashboard"

    def refresh_dashboard(self):
        # Update dashboard numbers
        db = SessionLocal()
        # Ensure database is initialized/tables exist if crud assumes it
        products_count = 0
        total_daily_sales = 0.0
        
        try:
            products_count = len(crud.get_products(db))
            
            # Calculate daily sales
            # In a real app, filter by today's date. For MVP, we sum all sales or implement get_daily_sales in crud
            # Let's do a quick calculation here or better yet, add a method in crud
            sales = crud.get_sales_history(db)
            # Filter for today (simplified)
            from datetime import datetime
            today = datetime.now().date()
            for sale in sales:
                if sale.timestamp.date() == today:
                    total_daily_sales += sale.total_amount
                    
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
        db.close()
        
        # Locate dashboard screen
        try:
            main_screen = self.root.get_screen("main")
            inner_sm = main_screen.ids.inner_screen_manager
            dashboard = inner_sm.get_screen("dashboard")
            dashboard.ids.total_products.text = str(products_count)
            dashboard.ids.daily_sales.text = f"{total_daily_sales:,.0f} GNF"
        except Exception as e:
             print(f"Error updating dashboard: {e}")

    def logout(self):
        self.user_session.user = None
        self.root.current = "login"

    def show_add_product_dialog(self):
        # Proxy to inventory screen
        main_screen = self.root.get_screen("main")
        inner_sm = main_screen.ids.inner_screen_manager
        inner_sm.get_screen("inventory").show_add_product_dialog()

if __name__ == "__main__":
    MadinaStockApp().run()