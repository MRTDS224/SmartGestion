from data.database import init_db, SessionLocal
from data import crud, models

def main():
    print("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    
    # Check if admin exists
    admin = crud.get_user_by_username(db, "admin")
    if not admin:
        print("Creating default Admin user (admin/admin)...")
        crud.create_user(db, "admin", "admin", role=models.UserRole.ADMIN.value)
    else:
        print("Admin user already exists.")

    # Create some categories if empty
    if not crud.get_categories(db):
        print("Creating default categories...")
        crud.create_category(db, "Téléphones")
        crud.create_category(db, "Accessoires")
        crud.create_category(db, "Pièces Détachées")

    db.close()
    print("Done.")

if __name__ == "__main__":
    main()
