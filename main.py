import base64
import io
import json
import random
import time
import os

import fitz
import numpy as np
import matplotlib.font_manager
from PIL import Image
from mistralai import Mistral
from google import genai

from evaluator_function import word_accuracy
from datasets import load_dataset
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from evaluator_function import word_accuracy
from src.create_text_image import create_text_image
from src.placement_validity import can_place_image, find_optimal_placement
from src.pdf_functions import create_blank_pdf, save_pdf, place_image_in_pdf
from src.text_augmentations import random_augment

if __name__ == "__main__":
    load_dotenv()
    system_fonts = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    ds = load_dataset("openai/gsm8k", "main")
    text_list = [elem for elem in ds["test"]["question"]]
    width, height = int(letter[0]), int(letter[1])
    text_list = text_list[:100]
    cnt = 0
    change_page = True
    existing_boxes = []
    page_data = []  
    current_page_data = {} 
    while text_list:
        if change_page:
            if current_page_data:
                page_data.append(current_page_data)
                current_page_data = {} 
            pdf_path = f"generated_pdf/ocr_{cnt}.pdf"
            canvas_obj, (page_width, page_height) = create_blank_pdf(pdf_path)
            current_page_data = {
                "page_number": cnt,
                "page_path": pdf_path,
                "page_width": page_width,
                "page_height": page_height,
                "full_text": "",
                "text_elements": []
            }
            change_page = False
        text = text_list[0]
        is_placed = False
        for _ in range(15):
            words_per_line = np.random.binomial(n=10, p=0.5, size=1)[0]+3
            font_path = random.choice(system_fonts)
            font_size = np.random.binomial(n=22,p=0.5,size=1)[0]+4
            img, img_info = create_text_image(text, words_per_line=words_per_line, font_path=font_path, font_size=font_size)
            img = random_augment(img)
            x_centroid = random.randint(0, width)
            y_centroid = random.randint(0, height)
            if can_place_image(img, x_centroid, y_centroid, existing_boxes, page_width, page_height):
                new_box = place_image_in_pdf(canvas_obj, img, x_centroid, y_centroid)
                existing_boxes.append(new_box)
                current_page_data["full_text"] += text + " "
                current_page_data["text_elements"].append({
                    "bbox": new_box,
                    "text": text
                })
                text_list.remove(text)
                is_placed = True
                break
            else:
                position = find_optimal_placement(img, existing_boxes, page_width, page_height)
                if position:
                    x_center, y_center = position
                    new_box = place_image_in_pdf(canvas_obj, img, x_center, y_center)
                    existing_boxes.append(new_box)
                    current_page_data["full_text"] += text + " "
                    current_page_data["text_elements"].append({
                        "bbox": new_box,
                        "text": text
                    })
                    text_list.remove(text)
                    is_placed = True
                    break
        if not is_placed:
            save_pdf(canvas_obj)
            if current_page_data:
                page_data.append(current_page_data)
                current_page_data = {}
            cnt += 1
            change_page = True
            existing_boxes = []
    save_pdf(canvas_obj)
    if current_page_data:
        page_data.append(current_page_data)
    os.makedirs("generated_pdf", exist_ok=True)
    json_path = "generated_pdf/ocr_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)
    print(f"JSON data saved to {json_path}")
    page_count = len(page_data)
    print(f"{page_count} files generated")

    gemini_api_key = os.environ["GEMINI_API_KEY"]
    gemini_client = genai.Client(api_key=gemini_api_key)

    mistral_api_key = os.environ["MISTRAL_API_KEY"]
    mistral_client = Mistral(api_key=mistral_api_key)

    mistral_total = 0
    gemini_total = 0

    for elem in page_data:
        number = elem["page_number"]
        pdf_document = fitz.open(f"generated_pdf/ocr_{number}.pdf")
        first_page = pdf_document[0]
        pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        b64_string = base64.b64encode(buffer.read()).decode()
        ocr_response = mistral_client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{b64_string}" 
            }
        )
        mistral_answer = ocr_response.pages[0].markdown
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=["Extract all text within this image. <OCR>:", img])
        gemini_answer = response.text
        ground_truth = elem["full_text"]
        mistral_accuracy = word_accuracy(ground_truth, mistral_answer)
        mistral_total += mistral_accuracy/page_count
        gemini_accuracy = word_accuracy(ground_truth, gemini_answer)
        gemini_total += gemini_accuracy/page_count
        time.sleep(2)
    print(f"Mistral Accuracy: {mistral_total:.2f}%")
    print(f"Gemini Accuracy: {gemini_total:.2f}%")