from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.toast import toast
from data import crud, database

class ProfileScreen(MDScreen):
    def on_enter(self):
        self.load_profile()

    def load_profile(self):
        app = MDApp.get_running_app()
        user = app.user_session.user
        if user:
            self.ids.profile_info.text = f"Rôle: {user.role}"
            self.ids.username.text = user.username
            self.ids.old_password.text = ""
            self.ids.new_password.text = ""
            self.ids.confirm_password.text = ""

    def update_profile(self):
        new_username = self.ids.username.text
        old_pass = self.ids.old_password.text
        new_pass = self.ids.new_password.text
        confirm_pass = self.ids.confirm_password.text
        
        if not new_username:
             toast("Nom d'utilisateur requis")
             return

        # Prepare update arguments
        app = MDApp.get_running_app()
        user = app.user_session.user
        
        if not user:
            return

        db = database.SessionLocal()
        
        # Check if password change is requested
        pwd_to_update = None
        if new_pass:
            if new_pass != confirm_pass:
                toast("Les nouveaux mots de passe ne correspondent pas")
                db.close()
                return
            if not old_pass:
                toast("Ancien mot de passe requis pour changer de mot de passe")
                db.close()
                return
            pwd_to_update = new_pass
        
        # Determine if only username is changing or both
        # Actually crud.update_user_profile handles this logic
        success, message = crud.update_user_profile(
            db, 
            user.id, 
            username=new_username, 
            old_password=old_pass if pwd_to_update else None, 
            new_password=pwd_to_update
        )
        
        if success:
            toast(message)
            # Update local session user
            # Re-fetch user to get updated fields
            updated_user = crud.get_user_by_username(db, new_username)
            app.user_session.user = updated_user
            
            # Update Navigation Info
            app.root.get_screen("main").ids.nav_username.text = f"{updated_user.username} ({updated_user.role})"
            
            self.load_profile()
        else:
            toast(message)
            
        db.close()
