from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from data import crud, database

class SalesHistoryScreen(MDScreen):
    data_table = None

    def on_enter(self):
        self.load_table()

    def load_table(self):
        layout = self.ids.table_box
        layout.clear_widgets()

        db = database.SessionLocal()
        sales = crud.get_sales_history(db)
        db.close()

        table_data = []
        for s in sales:
            # Format: ID, Date, Vendeur, Montant Total
            formatted_date = s.timestamp.strftime("%Y-%m-%d %H:%M")
            username = s.user.username if s.user else "Unknown"
            table_data.append((
                str(s.id),
                formatted_date,
                username,
                f"{s.total_amount} GNF"
            ))

        self.data_table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(1, 1),
            use_pagination=True,
            column_data=[
                ("ID", dp(10)),
                ("Date", dp(40)),
                ("Vendeur", dp(30)),
                ("Total", dp(20)),
            ],
            row_data=table_data,
        )
        layout.add_widget(self.data_table)
