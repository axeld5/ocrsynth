import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

def create_blank_pdf(pdf_path, pagesize=letter):
    """
    Create a blank PDF canvas.
    
    Args:
        pdf_path (str): Path to the output PDF file
        pagesize (tuple): Size of the PDF page
    
    Returns:
        tuple: Canvas object and page dimensions (width, height)
    """
    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    width, height = pagesize
    return c, (width, height)

def place_image_in_pdf(canvas_obj, image, x_centroid, y_centroid):
    """
    Place an image on a PDF canvas at the specified centroid coordinates.
    
    Args:
        canvas_obj (canvas.Canvas): The PDF canvas object
        image (PIL.Image): The image to place in the PDF
        x_centroid (float): X-coordinate for the image centroid
        y_centroid (float): Y-coordinate for the image centroid
    
    Returns:
        dict: Information about the image position in the PDF
    """
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    img_width, img_height = image.size
    x_pos = x_centroid - (img_width / 2)
    y_pos = y_centroid - (img_height / 2)
    
    img_reader = ImageReader(img_bytes)
    canvas_obj.drawImage(img_reader, x_pos, y_pos, width=img_width, height=img_height)
    
    return {
        'x0': x_pos,
        'y0': y_pos,
        'x1': x_pos + img_width,
        'y1': y_pos + img_height,
        'width': img_width,
        'height': img_height,
        'centroid_x': x_centroid,
        'centroid_y': y_centroid
    }

def save_pdf(canvas_obj):
    """
    Save the PDF canvas.
    
    Args:
        canvas_obj (canvas.Canvas): The PDF canvas object
    """
    canvas_obj.save()