import os
import json
import easyocr
from glob import glob
from tqdm import tqdm
from thefuzz import fuzz

def load_json_data(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def find_fuzzy_matching_values(ocr_text, json_data, threshold=70):
    matching_key_values = []
    ocr_text_lower = [text.lower() for text in ocr_text]  # Convert each element of the OCR text list to lowercase
    for key, value in json_data.items():
        if isinstance(value, list):
            for item in value:
                item_lower = item.lower()  # Convert JSON data value to lowercase
                for text in ocr_text_lower:
                    similarity_ratio = fuzz.partial_ratio(text, item_lower)
                    if similarity_ratio >= threshold:
                        matching_key_values.append((key, item))
                        break  # Break the loop if a match is found
        else:
            value_lower = value.lower()  # Convert JSON data value to lowercase
            for text in ocr_text_lower:
                similarity_ratio = fuzz.partial_ratio(text, value_lower)
                if similarity_ratio >= threshold:
                    matching_key_values.append((key, value))
                    break  # Break the loop if a match is found
    return matching_key_values

def perform_ocr(image):
    reader = easyocr.Reader(['en'], gpu=True)  # Set gpu to True or False if GPU is available
    detected_texts = []  # List to store the detected texts
    result = reader.readtext(image)
    detected_texts.append([text for bbox, text, conf in result])
    return detected_texts[0]  # Return the list of detected texts (extracted from the nested list)

if __name__ == "__main__":
    json_file_path = "OCR fuzzy.json"
    image_folder = "images/*"

    json_data = load_json_data(json_file_path)

    # Initialize a dictionary to store the matching results for each image
    matching_results = {}

    for img in tqdm(glob(image_folder)):
        detected_texts = perform_ocr(img)
        matching_key_values = find_fuzzy_matching_values(detected_texts, json_data)
        matching_results[img] = matching_key_values

    # Output the matching results for each image
    for img, matches in matching_results.items():
        print(f"Matching key-value pairs found in {os.path.basename(img)}: {matches}")
