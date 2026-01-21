from sqlalchemy.orm import Session, joinedload
from . import models
from datetime import datetime
import hashlib
import os

# --- Authentication & User ---

def get_password_hash(password: str) -> str:
    # ROI: Simple SHA256 for MVP. Production should use bcrypt/Argon2.
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_user(db: Session, username, password, role="employee", must_change_password=True):
    hashed_password = get_password_hash(password)
    db_user = models.User(
        username=username, 
        hashed_password=hashed_password, 
        role=role,
        must_change_password=must_change_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session):
    return db.query(models.User).all()

def delete_user(db: Session, user_id: int):
    # Prevent deleting the last admin is a good safety check, but for now simple delete
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # Check if user has sales?
        # If user has sales, we might want to soft delete or keep them.
        # SQLite will might complain if no cascade delete on foreign keys or set null.
        # But Sale.user_id is ForeignKey.
        db.delete(user)
        db.commit()
        return True
    return False

def update_user_profile(db: Session, user_id: int, username: str = None, old_password: str = None, new_password: str = None):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False, "Utilisateur introuvable"
    
    # Update username if provided
    if username and username != user.username:
        # Check uniqueness
        existing_user = get_user_by_username(db, username)
        if existing_user:
            return False, "Nom d'utilisateur déjà pris"
        user.username = username

    # Update password if provided
    if new_password:
        if not old_password:
             return False, "Ancien mot de passe requis"
        if not verify_password(old_password, user.hashed_password):
             return False, "Ancien mot de passe incorrect"
        
        user.hashed_password = get_password_hash(new_password)
        user.must_change_password = False
    
    db.commit()
    db.refresh(user)
    return True, "Profil mis à jour"

def admin_reset_password(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.hashed_password = get_password_hash("123456")
        user.must_change_password = True
        user.password_reset_requested = False
        db.commit()
        db.refresh(user)
        return True
    return False

def request_password_reset(db: Session, username: str):
    user = get_user_by_username(db, username)
    if user:
        user.password_reset_requested = True
        db.commit()
        return True
    return False

def change_user_role(db: Session, user_id: int, new_role: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
        return True
    return False

# --- Products & Categories ---

def create_category(db: Session, name: str):
    db_category = models.Category(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session):
    return db.query(models.Category).all()

def create_product(db: Session, product_data: dict):
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_data: dict):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        for key, value in product_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def get_products(db: Session, search_query: str = None):
    query = db.query(models.Product).options(joinedload(models.Product.category))
    if search_query:
        query = query.filter(models.Product.name.ilike(f"%{search_query}%"))
    return query.all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).options(joinedload(models.Product.category)).filter(models.Product.id == product_id).first()

# --- Sales ---

def process_sale(db: Session, user_id: int, items: list):
    """
    items: list of dicts {'product_id': int, 'quantity': int}
    """
    total_sale_amount = 0.0
    sale_items_objects = []

    # First pass: validate stock and calculate total
    for item in items:
        product = get_product(db, item['product_id'])
        if not product:
            raise ValueError(f"Product {item['product_id']} not found")
        if product.stock_quantity < item['quantity']:
            raise ValueError(f"Not enough stock for {product.name}")
        
        unit_price = product.selling_price
        total_price = unit_price * item['quantity']
        total_sale_amount += total_price
        
        # Decrement stock
        product.stock_quantity -= item['quantity']
        
        sale_items_objects.append(models.SaleItem(
            product_id=product.id,
            quantity=item['quantity'],
            unit_price=unit_price,
            total_price=total_price
        ))

    # Create Sale
    new_sale = models.Sale(user_id=user_id, total_amount=total_sale_amount)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    # Add items
    for sale_item in sale_items_objects:
        sale_item.sale_id = new_sale.id
        db.add(sale_item)
    
    db.commit()
    return new_sale

def get_sales_history(db: Session):
    return db.query(models.Sale).options(
        joinedload(models.Sale.user),
        joinedload(models.Sale.items).joinedload(models.SaleItem.product)
    ).order_by(models.Sale.timestamp.desc()).all()
