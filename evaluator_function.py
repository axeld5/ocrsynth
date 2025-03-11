from difflib import SequenceMatcher

def word_accuracy(ground_truth: str, ocr_text: str) -> float:
    """
    Calculate the word accuracy of OCR output compared to ground truth.
    
    :param ground_truth: The correct text.
    :param ocr_text: The OCR-generated text.
    :return: Accuracy as a percentage (0-100).
    """
    gt_words = ground_truth.replace("\n", " ").replace("  ", " ").lower().split()
    ocr_words = ocr_text.replace("\n", " ").replace("  ", " ").lower().split()
    
    matcher = SequenceMatcher(None, gt_words, ocr_words)
    correct_words = sum(block.size for block in matcher.get_matching_blocks())
    
    if len(gt_words) == 0:
        return 100.0 if len(ocr_words) == 0 else 0.0
    
    return (correct_words / len(gt_words)) * 100.0