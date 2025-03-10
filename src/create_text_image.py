import random
from PIL import ImageFont, Image, ImageDraw

def create_text_image(
        text, 
        words_per_line=3, 
        font_path=None, 
        font_size=24, 
        bg_color=(255, 255, 255), 
        text_color=(0, 0, 0), 
        padding=20, 
        line_spacing=1.2
    ):
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
            regular_font = ImageFont.truetype(font_path, font_size, encoding="latin-1")
            bold_font = regular_font
        else:
            regular_font = ImageFont.load_default()
            bold_font = regular_font
    except Exception as e:
        print(f"Font loading error: {e}, using default font")
        regular_font = ImageFont.load_default()
        bold_font = regular_font
    words = text.split()
    word_groups = [words[i:i + words_per_line] for i in range(0, len(words), words_per_line)]
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
    temp_img = Image.new('RGB', (1, 1), bg_color)
    temp_draw = ImageDraw.Draw(temp_img)
    def get_text_dimensions(text, font):
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height
    line_widths = []
    for styled_words in styled_word_groups:
        line_width = 0
        for word, style in styled_words:
            font = bold_font if style == 'bold' else regular_font
            word_width, _ = get_text_dimensions(word + ' ', font)
            line_width += word_width
        if line_width > 0:
            space_width, _ = get_text_dimensions(' ', regular_font)
            line_width -= space_width
        line_widths.append(line_width)
    img_width = max(line_widths) + (padding * 2) if line_widths else padding * 2
    line_height = int(font_size * line_spacing)
    img_height = (len(styled_word_groups) * line_height) + (padding * 2)
    img = Image.new('RGB', (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)
    lines_info = []
    for i, (styled_words, line_width) in enumerate(zip(styled_word_groups, line_widths)):
        x_pos = padding + (img_width - 2 * padding - line_width) // 2
        y_pos = padding + (i * line_height)
        current_x = x_pos
        word_positions = []
        rendered_text = ''
        for word, style in styled_words:
            font = bold_font if style == 'bold' else regular_font
            word_width, word_height = get_text_dimensions(word, font)
            draw.text((current_x, y_pos), word, fill=text_color, font=font)
            if style == 'strikethrough':
                strike_y = y_pos + (word_height // 2)
                draw.line([(current_x, strike_y), (current_x + word_width, strike_y)], 
                          fill=text_color, width=max(1, font_size // 15))
            word_positions.append({
                'word': word,
                'x': current_x,
                'y': y_pos,
                'width': word_width,
                'height': word_height,
                'style': style
            })
            space_width, _ = get_text_dimensions(' ', font)
            current_x += word_width + space_width
            rendered_text += word + ' '
        if rendered_text:
            rendered_text = rendered_text[:-1]
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
