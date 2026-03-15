from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem, MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, StringProperty
from kivymd.toast import toast
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivy.lang import Builder
from data import crud, database
import os

class InvoiceListItem(TwoLineAvatarIconListItem):
    invoice_id = NumericProperty(0)

class InvoicesScreen(MDScreen):
    creation_mode = StringProperty("manual") # "manual" or "sale"
    selected_client_id = None
    selected_sale_id = None
    manual_items = [] # list of dicts

    client_dialog = None
    sale_dialog = None

    def on_enter(self):
        self.load_invoices()
        self.set_mode("manual") # This will trigger clear_form inside the mode setup

    def set_mode(self, mode):
        self.creation_mode = mode
        self.build_dynamic_ui()
        self.clear_form() # Reset selections when switching mode

    def build_dynamic_ui(self):
        container = self.ids.dynamic_container
        container.clear_widgets()
        
        if self.creation_mode == "manual":
            # Build Manual UI
            input_row = MDBoxLayout(orientation='horizontal', adaptive_height=True, spacing="5dp")
            
            self.item_desc = MDTextField(hint_text="Description", size_hint_x=0.5)
            self.item_qty = MDTextField(hint_text="Qté", input_filter="int", text="1", size_hint_x=0.2)
            self.item_price = MDTextField(hint_text="Prix Unitaire", input_filter="float", size_hint_x=0.2)
            btn_add = MDIconButton(icon="plus-circle", on_release=lambda x: self.add_manual_item(), size_hint_x=0.1)
            
            input_row.add_widget(self.item_desc)
            input_row.add_widget(self.item_qty)
            input_row.add_widget(self.item_price)
            input_row.add_widget(btn_add)
            
            list_box = MDBoxLayout(orientation='vertical')
            lbl = MDLabel(text="Articles ajoutés:", size_hint_y=None, height="30dp")
            scroll = ScrollView()
            self.manual_items_list = MDList()
            scroll.add_widget(self.manual_items_list)
            
            list_box.add_widget(lbl)
            list_box.add_widget(scroll)
            
            container.add_widget(input_row)
            container.add_widget(list_box)

        elif self.creation_mode == "sale":
            # Build Sale UI
            sale_row = MDBoxLayout(orientation='horizontal', adaptive_height=True, spacing="10dp")
            self.lbl_selected_sale = MDLabel(text="Vente: Aucune")
            btn_sale = MDFillRoundFlatButton(text="Sélectionner Vente", on_release=lambda x: self.show_sale_dialog())
            
            sale_row.add_widget(self.lbl_selected_sale)
            sale_row.add_widget(btn_sale)
            
            container.add_widget(sale_row)

    def load_invoices(self):
        db = database.SessionLocal()
        invoices = crud.get_invoices(db)
        db.close()
        
        data = []
        for inv in invoices:
            client_name = inv.client.name if inv.client else "Client inconnu"
            data.append({
                "text": f"Facture #{inv.id} - {client_name}",
                "secondary_text": f"Total: {inv.total_amount} GNF",
                "invoice_id": inv.id
            })
        self.ids.invoices_rv.data = data

    def clear_form(self):
        self.selected_client_id = None
        self.selected_sale_id = None
        self.manual_items = []
        
        self.ids.lbl_selected_client.text = "Client: Aucun"
        
        if self.creation_mode == "manual":
            self.item_desc.text = ""
            self.item_qty.text = "1"
            self.item_price.text = ""
            self.manual_items_list.clear_widgets()
        elif self.creation_mode == "sale":
            self.lbl_selected_sale.text = "Vente: Aucune"
            
        self.update_total()

    def add_manual_item(self):
        desc = self.item_desc.text
        qty_str = self.item_qty.text
        price_str = self.item_price.text
        
        if not desc or not qty_str or not price_str:
            toast("Veuillez remplir tous les champs")
            return
            
        try:
            qty = int(qty_str)
            price = float(price_str)
        except ValueError:
            toast("Quantité et Prix doivent être des nombres")
            return
            
        self.manual_items.append({
            "description": desc,
            "quantity": qty,
            "unit_price": price
        })
        
        item_ui = OneLineListItem(text=f"{desc} (x{qty}) - {price} GNF")
        self.manual_items_list.add_widget(item_ui)
        
        self.item_desc.text = ""
        self.item_qty.text = "1"
        self.item_price.text = ""
        self.update_total()

    def update_total(self):
        total = 0
        if self.creation_mode == "manual":
            for item in self.manual_items:
                total += item['quantity'] * item['unit_price']
        elif self.creation_mode == "sale" and self.selected_sale_id:
            db = database.SessionLocal()
            from data import models
            sale = db.query(models.Sale).filter(models.Sale.id == self.selected_sale_id).first()
            if sale:
                total = sale.total_amount
            db.close()
            
        self.ids.lbl_total.text = f"Total: {total} GNF"

    def show_client_dialog(self):
        db = database.SessionLocal()
        clients = crud.get_clients(db)
        db.close()
        
        list_container = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
        scroll = ScrollView()
        md_list = MDList()
        
        for c in clients:
            item = OneLineListItem(text=c.name)
            item.bind(on_release=lambda x, cid=c.id, name=c.name: self.pick_client(cid, name))
            md_list.add_widget(item)
            
        scroll.add_widget(md_list)
        list_container.add_widget(scroll)
            
        self.client_dialog = MDDialog(
            title="Sélectionner un Client",
            type="custom",
            content_cls=list_container,
            buttons=[MDFlatButton(text="ANNULER", on_release=lambda x: self.client_dialog.dismiss())]
        )
        self.client_dialog.open()

    def pick_client(self, client_id, name):
        self.selected_client_id = client_id
        self.ids.lbl_selected_client.text = f"Client: {name}"
        if self.client_dialog:
            self.client_dialog.dismiss()

    def show_sale_dialog(self):
        db = database.SessionLocal()
        sales = crud.get_sales_history(db)
        db.close()
        
        list_container = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
        scroll = ScrollView()
        md_list = MDList()
        
        for s in sales[:20]: # Top 20 recent
            dt = s.timestamp.strftime("%Y-%m-%d %H:%M")
            item = OneLineListItem(text=f"Sale #{s.id} - {dt} - {s.total_amount} GNF")
            item.bind(on_release=lambda x, sid=s.id, amount=s.total_amount: self.pick_sale(sid, amount))
            md_list.add_widget(item)
            
        scroll.add_widget(md_list)
        list_container.add_widget(scroll)
            
        self.sale_dialog = MDDialog(
            title="Sélectionner une Vente",
            type="custom",
            content_cls=list_container,
            buttons=[MDFlatButton(text="ANNULER", on_release=lambda x: self.sale_dialog.dismiss())]
        )
        self.sale_dialog.open()

    def pick_sale(self, sale_id, amount):
        self.selected_sale_id = sale_id
        if self.creation_mode == "sale":
            self.lbl_selected_sale.text = f"Vente: #{sale_id} ({amount} GNF)"
        self.update_total()
        if self.sale_dialog:
            self.sale_dialog.dismiss()

    def generate_invoice(self):
        if not self.selected_client_id:
            toast("Veuillez sélectionner un client")
            return
            
        db = database.SessionLocal()
        new_invoice = None
        
        if self.creation_mode == "manual":
            if not self.manual_items:
                toast("Ajoutez au moins un article")
                db.close()
                return
            new_invoice = crud.create_invoice(db, self.selected_client_id, self.manual_items, None)
            
        elif self.creation_mode == "sale":
            if not self.selected_sale_id:
                toast("Veuillez sélectionner une vente")
                db.close()
                return
            
            from data import models
            sale_items = db.query(models.SaleItem).filter(models.SaleItem.sale_id == self.selected_sale_id).all()
            inv_items = []
            for si in sale_items:
                product = db.query(models.Product).filter(models.Product.id == si.product_id).first()
                product_name = product.name if product else "Produit inconnu"
                inv_items.append({
                    "description": product_name,
                    "quantity": si.quantity,
                    "unit_price": si.unit_price
                })
            new_invoice = crud.create_invoice(db, self.selected_client_id, inv_items, self.selected_sale_id)
            
        # Refresh the loaded model to make it usable by PDF generator before closing connection
        from data.models import Invoice
        db.refresh(new_invoice)
        # SQLAlchemy may detach the object when closing, generating the PDF first:
        
        try:
            from utils.pdf_generator import create_invoice_pdf
            app_dir = os.path.expanduser("~/.smartgestion")
            pdf_path = create_invoice_pdf(new_invoice, app_dir)
            toast(f"Facture générée: {pdf_path}")
        except Exception as e:
            toast(f"Erreur PDF: {e}")
            
        db.close()
        self.clear_form()
        self.load_invoices()

    def select_invoice(self, invoice_id):
        toast(f"Facture #{invoice_id} sélectionnée (Affichage détails à venir)")
