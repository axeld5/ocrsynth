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
    if not is_within_page_bounds(new_bbox, page_width, page_height):
        return False
    for existing_box in existing_boxes:
        if is_overlapping(new_bbox, existing_box):
            return False
    return True

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
    x_min = margin + (img_width / 2)
    y_min = margin + (img_height / 2)
    x_max = page_width - margin - (img_width / 2)
    y_max = page_height - margin - (img_height / 2)
    for x in range(int(x_min), int(x_max), step):
        for y in range(int(y_min), int(y_max), step):
            if can_place_image(image, x, y, existing_boxes, page_width, page_height):
                return x, y
    if step > 10:
        return find_optimal_placement(image, existing_boxes, page_width, page_height, 
                                   margin, step // 2)
    return None