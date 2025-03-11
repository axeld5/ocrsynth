# OCRSYNTH

This project aims to allow the synthetic generation of OCR datasets using textual datasets. On top of that, it can be used to create a new OCR benchmark by generating PDF documents with text images and evaluating the performance of different OCR models. It uses Python, PIL, ReportLab, and OCR APIs from Mistral and Google's Gemini to generate and evaluate the benchmark.

## Features

-   **PDF Generation:**
    - Generates PDF documents with randomly placed text images.
    - Customizable text styles, fonts, and sizes.
    - Handles text placement to avoid overlaps.
    - Applies random augmentations to text images.
-   **OCR Evaluation:**
    - Utilizes Mistral and Google Gemini OCR APIs.
    - Calculates word accuracy by comparing OCR output to ground truth.
    - Generates a JSON file containing ground truth text and bounding box information.
-   **Docker Support:**
    - Provides a Dockerfile for easy setup and execution.

## File description

-   `README.md`: Project documentation.
-   `Dockerfile`: Docker configuration for building the environment.
-   `evaluator_function.py`: Contains the word accuracy evaluation function.
-   `main.py`: Main script for generating PDFs and evaluating OCR.
-   `requirements.txt`: List of Python dependencies.
-   `src/`: Directory containing source code modules.
    -   `create_text_image.py`: Functions for creating text images.
    -   `pdf_functions.py`: Functions for PDF generation and manipulation.
    -   `placement_validity.py`: Functions for validating and finding image placements.
    -   `text_augmentations.py`: Functions for applying random image augmentations.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd ocrword_bench
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the project root and add your API keys:

    ```
    GEMINI_API_KEY=your_gemini_api_key
    MISTRAL_API_KEY=your_mistral_api_key
    ```

4.  **Run the script:**

    ```bash
    python main.py
    ```

## Docker Setup

1.  **Build the Docker image:**

    ```bash
    docker build -t ocrword_bench .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run ocrword_bench
    ```

## Usage

The `main.py` script generates PDF files in the `generated_pdf/` directory and saves the ground truth data in `generated_pdf/ocr_data.json`. It then evaluates the OCR performance of Mistral and Gemini and prints the accuracy results.

## Dependencies

-   `datasets`: For loading the GSM8K dataset.
-   `google-genai`: For accessing the Google Gemini API.
-   `matplotlib`: For font handling.
-   `mistralai`: For accessing the Mistral API.
-   `numpy`: For numerical operations.
-   `pillow`: For image processing.
-   `python_dotenv`: For loading environment variables.
-   `PyMuPDF`: For PDF processing.
-   `reportlab`: For PDF generation.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bug fixes or feature requests.

## Notes

Currently, there are some fonts which have issues with generation. This should be fixed in a later version.