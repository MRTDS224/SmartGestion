from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.toast import toast
from data import crud, database

class ProfileScreen(MDScreen):
    def on_enter(self):
        app = MDApp.get_running_app()
        user = app.user_session.user
        if user:
            self.ids.profile_info.text = f"Utilisateur: {user.username} | Rôle: {user.role}"

    def change_password(self):
        new_pass = self.ids.new_password.text
        confirm_pass = self.ids.confirm_password.text
        
        if not new_pass:
             toast("Veuillez entrer un mot de passe")
             return

        if new_pass != confirm_pass:
            toast("Les mots de passe ne correspondent pas")
            return
            
        app = MDApp.get_running_app()
        user = app.user_session.user
        
        if user:
            db = database.SessionLocal()
            if crud.update_user_password(db, user.id, new_pass):
                toast("Mot de passe mis à jour")
                # Update local session user object to reflect change (must_change_password=False)
                # But querying a fresh object is better.
                # For now let's manually toggle it in session if we can't re-fetch easily
                user.must_change_password = False
                
                self.ids.new_password.text = ""
                self.ids.confirm_password.text = ""
                
                # Navigate to dashboard if they were forced here?
                # For now, just stay.
            else:
                toast("Erreur lors de la mise à jour")
            db.close()
