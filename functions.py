from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import fitz
import random
import io

def create_text_image(text, words_per_line=3, font_path=None, font_size=24, bg_color=(255, 255, 255), 
                     text_color=(0, 0, 0), padding=20, line_spacing=1.2):
    """
    Create an image with styled text.
    
    Args:
        text (str): The text to place in the image
        words_per_line (int): Number of words per line
        font_path (str): Path to TTF font (or None for default)
        font_size (int): Font size for the image
        bg_color (tuple): Background color in RGB
        text_color (tuple): Text color in RGB
        padding (int): Padding around the text
        line_spacing (float): Line spacing multiplier
    
    Returns:
        PIL.Image: Image with the styled text
        dict: Information about the text positioning
    """
    # Load fonts
    try:
        if font_path:
            regular_font = ImageFont.truetype(font_path, font_size)
            bold_font = regular_font
        else:
            regular_font = ImageFont.load_default()
            bold_font = regular_font
    except Exception as e:
        print(f"Font loading error: {e}, using default font")
        regular_font = ImageFont.load_default()
        bold_font = regular_font
    
    # Split text into words and group them
    words = text.split()
    word_groups = [words[i:i + words_per_line] for i in range(0, len(words), words_per_line)]
    
    # Apply random styling to words
    styled_word_groups = []
    for group in word_groups:
        styled_words = []
        for word in group:
            style_choice = random.randint(1, 100)
            if style_choice <= 1:
                styled_words.append((word, 'strikethrough'))
            elif style_choice <= 2:
                styled_words.append((word, 'bold'))
            elif style_choice <= 5:
                styled_words.append((word.upper(), 'normal'))
            else:
                styled_words.append((word, 'normal'))
        styled_word_groups.append(styled_words)
    
    # Create a temporary image to measure text dimensions
    temp_img = Image.new('RGB', (1, 1), bg_color)
    temp_draw = ImageDraw.Draw(temp_img)
    
    def get_text_dimensions(text, font):
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height
    
    # Calculate line widths
    line_widths = []
    for styled_words in styled_word_groups:
        line_width = 0
        for word, style in styled_words:
            font = bold_font if style == 'bold' else regular_font
            word_width, _ = get_text_dimensions(word + ' ', font)
            line_width += word_width
        
        # Remove trailing space width
        if line_width > 0:
            space_width, _ = get_text_dimensions(' ', regular_font)
            line_width -= space_width
        
        line_widths.append(line_width)
    
    # Calculate image dimensions
    img_width = max(line_widths) + (padding * 2) if line_widths else padding * 2
    line_height = int(font_size * line_spacing)
    img_height = (len(styled_word_groups) * line_height) + (padding * 2)
    
    # Create the actual image
    img = Image.new('RGB', (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text lines
    lines_info = []
    for i, (styled_words, line_width) in enumerate(zip(styled_word_groups, line_widths)):
        # Center text horizontally
        x_pos = padding + (img_width - 2 * padding - line_width) // 2
        y_pos = padding + (i * line_height)
        current_x = x_pos
        
        word_positions = []
        rendered_text = ''
        
        for word, style in styled_words:
            font = bold_font if style == 'bold' else regular_font
            word_width, word_height = get_text_dimensions(word, font)
            
            # Draw the word
            draw.text((current_x, y_pos), word, fill=text_color, font=font)
            
            # Add strikethrough if needed
            if style == 'strikethrough':
                strike_y = y_pos + (word_height // 2)
                draw.line([(current_x, strike_y), (current_x + word_width, strike_y)], 
                          fill=text_color, width=max(1, font_size // 15))
            
            # Track word position
            word_positions.append({
                'word': word,
                'x': current_x,
                'y': y_pos,
                'width': word_width,
                'height': word_height,
                'style': style
            })
            
            # Add space after word
            space_width, _ = get_text_dimensions(' ', font)
            current_x += word_width + space_width
            rendered_text += word + ' '
        
        # Remove trailing space
        if rendered_text:
            rendered_text = rendered_text[:-1]
        
        # Add line info
        lines_info.append({
            'text': rendered_text,
            'x_pos': x_pos,
            'y_pos': y_pos,
            'width': line_width,
            'height': line_height,
            'words': word_positions
        })
    
    return img, {
        'lines': lines_info,
        'image_width': img_width,
        'image_height': img_height,
        'centroid_x': img_width // 2,
        'centroid_y': img_height // 2
    }

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
        'x_pos': x_pos,
        'y_pos': y_pos,
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

def get_all_image_bounding_boxes(pdf_path):
    """
    Extract the bounding box information for all images in the first page of a PDF.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        list: A list of dictionaries containing bounding box info for each image, or an empty list if no images are found.
    """
    doc = fitz.open(pdf_path)
    page = doc[0]  # First page
    image_list = page.get_images(full=True)

    if not image_list:
        doc.close()
        return []

    all_bounding_boxes = []

    for image in image_list:
        xref = image[0]  # Extract image xref number
        rect_list = page.get_image_rects(xref)  # Get bounding boxes for the image
        
        for bbox in rect_list:
            bbox_info = {
                'x0': bbox.x0,
                'y0': bbox.y0,
                'x1': bbox.x1,
                'y1': bbox.y1,
                'width': bbox.width,
                'height': bbox.height,
                'centroid_x': (bbox.x0 + bbox.x1) / 2,
                'centroid_y': (bbox.y0 + bbox.y1) / 2
            }
            all_bounding_boxes.append(bbox_info)

    doc.close()
    return all_bounding_boxes

def is_overlapping(bbox1, bbox2):
    """
    Check if two bounding boxes overlap.
    
    Args:
        bbox1 (dict): First bounding box
        bbox2 (dict): Second bounding box
        
    Returns:
        bool: True if overlapping, False otherwise
    """
    return not (bbox1['x1'] < bbox2['x0'] or bbox1['x0'] > bbox2['x1'] or
                bbox1['y1'] < bbox2['y0'] or bbox1['y0'] > bbox2['y1'])

def is_within_page_bounds(bbox, page_width, page_height):
    """
    Check if a bounding box is completely within page boundaries.
    
    Args:
        bbox (dict): Bounding box to check
        page_width (float): Width of the page
        page_height (float): Height of the page
        
    Returns:
        bool: True if within bounds, False otherwise
    """
    return (bbox['x0'] >= 0 and bbox['y0'] >= 0 and
            bbox['x1'] <= page_width and bbox['y1'] <= page_height)

def test_image_placement(image, x_centroid, y_centroid):
    """
    Simulate placing an image and return its bounding box.
    
    Args:
        image (PIL.Image): The image to place
        x_centroid (float): X-coordinate for the image centroid
        y_centroid (float): Y-coordinate for the image centroid
        
    Returns:
        dict: Simulated bounding box for the image
    """
    img_width, img_height = image.size
    x_pos = x_centroid - (img_width / 2)
    y_pos = y_centroid - (img_height / 2)
    
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

def can_place_image(image, x_centroid, y_centroid, existing_boxes, page_width, page_height):
    """
    Check if an image can be placed at the specified position without overlapping existing boxes
    and without going outside page boundaries.
    
    Args:
        image (PIL.Image): The image to place
        x_centroid (float): X-coordinate for the image centroid
        y_centroid (float): Y-coordinate for the image centroid
        existing_boxes (list): List of existing bounding boxes
        page_width (float): Width of the page
        page_height (float): Height of the page
        
    Returns:
        bool: True if the image can be placed, False otherwise
    """
    new_bbox = test_image_placement(image, x_centroid, y_centroid)
    
    # Check if image is within page boundaries
    if not is_within_page_bounds(new_bbox, page_width, page_height):
        return False
    
    # Check if image overlaps with any existing boxes
    for existing_box in existing_boxes:
        if is_overlapping(new_bbox, existing_box):
            return False
    
    return True

def append_image_to_pdf(pdf_path, image, x_centroid, y_centroid):
    """
    Append an image to an existing PDF without overwriting previous content.
    
    Args:
        pdf_path (str): Path to the PDF file
        image (PIL.Image): The image to append
        x_centroid (float): X-coordinate for the image centroid
        y_centroid (float): Y-coordinate for the image centroid
        
    Returns:
        dict: Information about the image position in the PDF
    """
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    img_width, img_height = image.size
    x_pos = x_centroid - (img_width / 2)
    y_pos = y_centroid - (img_height / 2)
    
    page.insert_image((x_pos, y_pos, x_pos + img_width, y_pos + img_height), stream=img_bytes.getvalue())
    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    doc.close()
    
    return {
        'x_pos': x_pos,
        'y_pos': y_pos,
        'width': img_width,
        'height': img_height,
        'centroid_x': x_centroid,
        'centroid_y': y_centroid
    }

def find_optimal_placement(image, existing_boxes, page_width, page_height, 
                         margin=20, step=50):
    """
    Find an optimal placement for an image that doesn't overlap with existing boxes
    and stays within page boundaries.
    
    Args:
        image (PIL.Image): The image to place
        existing_boxes (list): List of existing bounding boxes
        page_width (float): Width of the page
        page_height (float): Height of the page
        margin (int): Margin from page edges
        step (int): Step size for searching positions
        
    Returns:
        tuple: (x_centroid, y_centroid) if a position is found, None otherwise
    """
    img_width, img_height = image.size
    
    # Define search area
    x_min = margin + (img_width / 2)
    y_min = margin + (img_height / 2)
    x_max = page_width - margin - (img_width / 2)
    y_max = page_height - margin - (img_height / 2)
    
    # Try positions in a grid pattern
    for x in range(int(x_min), int(x_max), step):
        for y in range(int(y_min), int(y_max), step):
            if can_place_image(image, x, y, existing_boxes, page_width, page_height):
                return x, y
    
    # Try with smaller steps if no position found
    if step > 10:
        return find_optimal_placement(image, existing_boxes, page_width, page_height, 
                                   margin, step // 2)
    
    return None