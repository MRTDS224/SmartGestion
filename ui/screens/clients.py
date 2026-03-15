from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.properties import NumericProperty
from kivymd.toast import toast
from data import crud, database

class ClientItem(OneLineAvatarIconListItem):
    client_id = NumericProperty(0)

class ClientsScreen(MDScreen):
    selected_client_id = None

    def on_enter(self):
        self.load_clients()
        self.clear_form()

    def load_clients(self, search_text=""):
        db = database.SessionLocal()
        clients = crud.get_clients(db, search_text)
        db.close()

        data = []
        for c in clients:
            data.append({
                "text": c.name,
                "client_id": c.id,
            })
        self.ids.clients_rv.data = data

    def select_client(self, client_id):
        self.selected_client_id = client_id
        db = database.SessionLocal()
        from data import models
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        db.close()

        if client:
            self.ids.client_name.text = client.name or ""
            self.ids.client_phone.text = client.phone or ""
            self.ids.client_email.text = client.email or ""
            self.ids.client_address.text = client.address or ""
            self.ids.btn_delete.disabled = False
            self.ids.btn_save.text = "METTRE À JOUR"

    def clear_form(self):
        self.selected_client_id = None
        self.ids.client_name.text = ""
        self.ids.client_phone.text = ""
        self.ids.client_email.text = ""
        self.ids.client_address.text = ""
        self.ids.btn_delete.disabled = True
        self.ids.btn_save.text = "AJOUTER"

    def save_client(self):
        name = self.ids.client_name.text
        phone = self.ids.client_phone.text
        email = self.ids.client_email.text
        address = self.ids.client_address.text
        
        if not name:
            toast("Le nom est obligatoire")
            return
            
        data = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address
        }
        
        db = database.SessionLocal()
        if self.selected_client_id:
            crud.update_client(db, self.selected_client_id, data)
            toast("Client mis à jour")
        else:
            crud.create_client(db, data)
            toast("Client ajouté")
            
        db.close()
        self.load_clients()
        self.clear_form()

    def delete_client(self):
        if not self.selected_client_id:
            return
            
        db = database.SessionLocal()
        if crud.delete_client(db, self.selected_client_id):
            toast("Client supprimé")
            self.load_clients()
            self.clear_form()
        else:
            toast("Erreur lors de la suppression")
        db.close()
