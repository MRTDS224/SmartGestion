from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.properties import StringProperty, NumericProperty
from kivymd.toast import toast
from data import crud, database

class UserItem(OneLineAvatarIconListItem):
    user_id = NumericProperty(0)
    icon_name = StringProperty("account")

class UsersScreen(MDScreen):
    dialog = None
    selected_user_id = None

    def on_enter(self):
        app = MDApp.get_running_app()
        if not app.user_session.user or app.user_session.user.role != "admin":
            toast("Accès réservé aux administrateurs")
            app.root.get_screen("main").ids.inner_screen_manager.current = "dashboard"
            return
            
        self.load_users()
        self.clear_form()

    def load_users(self):
        db = database.SessionLocal()
        users = crud.get_users(db)
        db.close()

        data = []
        for u in users:
            icon = "account"
            if u.role == "admin":
                icon = "shield-account"
            if u.password_reset_requested:
                icon = "alert"
            
            data.append({
                "text": u.username,
                "user_id": u.id,
                "icon_name": icon
            })
        
        self.ids.users_rv.data = data

    def select_user(self, user_id):
        self.selected_user_id = user_id
        db = database.SessionLocal()
        # We need a get_user_by_id or just query
        # Since we have get_users, we can query.
        # Ideally crud should have get_user(id)
        # Using a raw query here for speed of implementation since crud.get_users returns list
        from data import models
        user = db.query(models.User).filter(models.User.id == user_id).first()
        db.close()

        if user:
            self.ids.detail_username.text = user.username
            self.ids.detail_role.text = user.role
            
            status_text = "Actif"
            if user.password_reset_requested:
                status_text = "Demande de reset MDP"
            elif user.must_change_password:
                status_text = "Doit changer MDP"
            
            self.ids.detail_status.text = f"Statut: {status_text}"
            
            # Enable buttons
            self.ids.btn_reset_pwd.disabled = False
            self.ids.btn_change_role.disabled = False
            self.ids.btn_delete.disabled = False

    def clear_form(self):
        self.selected_user_id = None
        self.ids.detail_username.text = ""
        self.ids.detail_role.text = ""
        self.ids.detail_status.text = "Statut: --"
        self.ids.btn_reset_pwd.disabled = True
        self.ids.btn_change_role.disabled = True
        self.ids.btn_delete.disabled = True

    def reset_password(self):
        if not self.selected_user_id: 
            return
            
        db = database.SessionLocal()
        if crud.admin_reset_password(db, self.selected_user_id):
            toast("Mot de passe réinitialisé à '123456'")
            self.load_users() # Update icon if it was alert
            self.select_user(self.selected_user_id) # Refresh details
        else:
            toast("Erreur reset")
        db.close()

    def toggle_role(self):
        if not self.selected_user_id: 
            return
            
        current_role = self.ids.detail_role.text
        new_role = "admin" if current_role == "employee" else "employee"
        
        db = database.SessionLocal()
        if crud.change_user_role(db, self.selected_user_id, new_role):
            toast(f"Rôle changé en {new_role}")
            self.load_users()
            self.select_user(self.selected_user_id)
        db.close()

    def delete_user(self):
        if not self.selected_user_id: 
            return
            
        db = database.SessionLocal()
        if crud.delete_user(db, self.selected_user_id):
            toast("Utilisateur supprimé")
            self.load_users()
            self.clear_form()
        else:
            toast("Erreur suppression")
        db.close()

    def show_add_user_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Ajouter Utilisateur",
                type="custom",
                content_cls=AddUserContent(),
                buttons=[
                    MDFlatButton(
                        text="ANNULER",
                        on_release=self.close_dialog
                    ),
                    MDFillRoundFlatButton(
                        text="AJOUTER",
                        on_release=self.save_user
                    ),
                ],
            )
        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()

    def save_user(self, *args):
        content = self.dialog.content_cls
        username = content.ids.username.text
        
        if not username:
            return

        db = database.SessionLocal()
        if crud.get_user_by_username(db, username):
            toast("Cet utilisateur existe déjà")
            db.close()
            return

        crud.create_user(db, username, "123456", role="employee", must_change_password=True)
        db.close()
        
        self.close_dialog()
        content.ids.username.text = ""
        self.load_users()

class AddUserContent(MDBoxLayout):
    pass
