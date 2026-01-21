from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from data import crud, database

class UsersScreen(MDScreen):
    data_table = None
    dialog = None

    def on_enter(self):
        self.load_table()

    def load_table(self):
        layout = self.ids.users_box
        layout.clear_widgets()

        db = database.SessionLocal()
        users = crud.get_users(db)
        db.close()

        table_data = []
        for u in users:
            table_data.append((
                str(u.id),
                u.username,
                u.role,
                "Oui" if u.must_change_password else "Non"
            ))

        self.data_table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(1, 1),
            use_pagination=True,
            check=True,
            column_data=[
                ("ID", dp(10)),
                ("Utilisateur", dp(30)),
                ("Rôle", dp(20)),
                ("Reset requis", dp(20)),
            ],
            row_data=table_data,
        )
        self.data_table.bind(on_check_press=self.on_check_press)
        
        button_box = MDBoxLayout(size_hint_y=None, height=dp(50), padding=dp(10))
        delete_btn = MDFillRoundFlatButton(
            text="SUPPRIMER LA SÉLECTION", 
            on_release=self.delete_selected_users,
            md_bg_color=(1, 0, 0, 1)
        )
        button_box.add_widget(delete_btn)
        
        layout.add_widget(button_box)
        layout.add_widget(self.data_table)

    def on_check_press(self, instance_table, current_row):
        # MDDataTable returns all checked rows? No, it returns current pressed row.
        # But we can access get_row_checks() if needed?
        # Actually standard practice is to rely on table.get_row_checks() during action.
        pass

    def delete_selected_users(self, instance):
        if not self.data_table:
            return
            
        checked_rows = self.data_table.get_row_checks()
        if not checked_rows:
            return
            
        db = database.SessionLocal()
        for row in checked_rows:
            # row is just the data row?
            # MDDataTable get_row_checks returns list of [row_data, ...] ?
            # It actually returns the row data. ID is index 0.
            user_id = int(row[0])
            crud.delete_user(db, user_id)
            
        db.close()
        self.load_table()

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
        # Check if exists
        if crud.get_user_by_username(db, username):
            # Show error?
            db.close()
            return

        # Default password
        crud.create_user(db, username, "123456", role="employee", must_change_password=True)
        db.close()
        
        self.close_dialog()
        content.ids.username.text = ""
        self.load_table()

class AddUserContent(MDBoxLayout):
    pass
