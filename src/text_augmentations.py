import random
from PIL import Image, ImageEnhance

def random_augment(image):
    """
    Randomly apply augmentations to an image with 50% chance of no augmentation.
    
    Args:
        image: A PIL Image object
        
    Returns:
        The augmented PIL Image object
    """
    if random.random() < 0.5:
        return image
    img = image.copy()
    augmentations = [
        'stretch_horizontal',
        'stretch_vertical',
        'compress_horizontal',
        'compress_vertical',
        'color_degradation',
        'rotation'
    ]
    num_augmentations = random.randint(1, 3)
    selected_augmentations = random.sample(augmentations, num_augmentations)
    for aug in selected_augmentations:
        if aug == 'stretch_horizontal':
            stretch_factor = random.uniform(1.1, 1.3)
            new_width = int(img.width * stretch_factor)
            img = img.resize((new_width, img.height))
        elif aug == 'stretch_vertical':
            stretch_factor = random.uniform(1.1, 1.3)
            new_height = int(img.height * stretch_factor)
            img = img.resize((img.width, new_height))
        elif aug == 'compress_horizontal':
            compress_factor = random.uniform(0.7, 0.9)
            new_width = int(img.width * compress_factor)
            img = img.resize((new_width, img.height))
        elif aug == 'compress_vertical':
            compress_factor = random.uniform(0.7, 0.9)
            new_height = int(img.height * compress_factor)
            img = img.resize((img.width, new_height))
        elif aug == 'color_degradation':
            enhancer = ImageEnhance.Color(img)
            degradation_factor = random.uniform(0.3, 0.8)
            img = enhancer.enhance(degradation_factor)
        elif aug == 'rotation':
            angle = random.uniform(-25, 25)
            img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    return img