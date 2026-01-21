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

def create_user(db: Session, username, password, role="employee"):
    hashed_password = get_password_hash(password)
    db_user = models.User(username=username, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

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
    return db.query(models.Sale).options(joinedload(models.Sale.user)).order_by(models.Sale.timestamp.desc()).all()
