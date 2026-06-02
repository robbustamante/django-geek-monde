from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io

def generate_invoice_pdf(order):
    """
    Generates a PDF invoice for a given order using xhtml2pdf.
    Returns the PDF content as bytes, or None if there was an error.
    """
    # Render HTML template with order context
    context = {'order': order}
    html_string = render_to_string('invoice_template.html', context)
    
    # Create a file-like buffer to receive PDF data
    result_buffer = io.BytesIO()
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(
        html_string, 
        dest=result_buffer
    )
    
    # Return PDF bytes if successful
    if not pisa_status.err:
        return result_buffer.getvalue()
    
    return None
