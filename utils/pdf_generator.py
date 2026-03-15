import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_invoice_pdf(invoice, app_dir):
    """
    Generates a PDF invoice for the given invoice object.
    
    Args:
        invoice: The invoice database model object (with client and items loaded).
        app_dir: Directory where the PDF should be saved.
    
    Returns:
        The absolute path to the generated PDF.
    """
    # Ensure a "Factures" subfolder exists in the app directory
    invoices_dir = os.path.join(app_dir, "Factures")
    os.makedirs(invoices_dir, exist_ok=True)
    
    filename = f"Facture_{invoice.id}_{invoice.client.name.replace(' ', '_')}.pdf"
    filepath = os.path.join(invoices_dir, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 80, "SMARTGESTION - FACTURE")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 110, f"Numéro: #{invoice.id}")
    c.drawString(100, height - 130, f"Date: {invoice.timestamp.strftime('%Y-%m-%d %H:%M')}")
    
    # Client Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, height - 110, "Client:")
    c.setFont("Helvetica", 12)
    c.drawString(400, height - 130, invoice.client.name)
    c.drawString(400, height - 150, f"Tél: {invoice.client.phone or 'N/A'}")
    c.drawString(400, height - 170, f"Email: {invoice.client.email or 'N/A'}")
    c.drawString(400, height - 190, f"Adr: {invoice.client.address or 'N/A'}")
    
    # Line Items Header
    y = height - 240
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Description")
    c.drawString(300, y, "Quantité")
    c.drawString(400, y, "PU (GNF)")
    c.drawString(500, y, "Total (GNF)")
    c.line(100, y - 5, 580, y - 5)
    
    # Line Items
    y -= 25
    c.setFont("Helvetica", 12)
    for item in invoice.items:
        c.drawString(100, y, item.description[:30]) # Truncate long descriptions
        c.drawString(300, y, str(item.quantity))
        c.drawString(400, y, f"{item.unit_price:,.0f}")
        c.drawString(500, y, f"{item.total_price:,.0f}")
        y -= 20
        
        # New page if needed
        if y < 100:
            c.showPage()
            y = height - 80
            c.setFont("Helvetica", 12)
            
    # Total
    c.line(100, y, 580, y)
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, y, "TOTAL:")
    c.drawString(500, y, f"{invoice.total_amount:,.0f} GNF")
    
    c.save()
    return filepath
