# Product Safety Checker

This project provides a web interface to analyze an image of a product and get a safety and nutritional report. It uses the Gemini API to analyze the image, extract key information, and perform a safety analysis.

## Features

-   **Web Interface:** Upload a product image directly in your browser.
-   **Product Analysis:** Extracts structured information like product name, ingredients, and brand.
-   **Safety Report:** Generates a report including pros, cons, nutritional information, and regulatory status.
-   **Web Search:** Searches for recent news, recalls, and health advisories related to the product and its ingredients.

## How It Works

1.  **Upload Image:** The user uploads a product image and provides their Gemini API key through the web interface.
2.  **Backend API:** The frontend sends the image and API key to the Flask backend.
3.  **Image Analysis:** The backend uses the Gemini API to analyze the image and extract product information.
4.  **Analysis & Search:** It then performs a deeper analysis and searches the web for relevant safety information.
5.  **Display Results:** The final, compiled report is sent back to the frontend and displayed to the user.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Product_safety_checker.git
    cd Product_safety_checker
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` in your web browser.

3.  **Analyze a product:**
    -   Enter your Gemini API key in the input field.
    -   Upload an image of the product you want to analyze.
    -   Click the "Analyze" button.

The analysis report will be displayed on the page.

## Security Warning

**Important:** You are required to enter your Gemini API key directly into the browser. This is not a secure practice for a production application, as the API key is transmitted over the network and visible in the browser's request. For personal or development use, ensure you are running this on a trusted local machine. In a production environment, the API key should be stored securely on the server and not exposed to the client-side.

## Dependencies

The main dependencies for this project are:

-   `Flask`: For the web server.
-   `langchain-google-genai`: For interacting with the Gemini API.
-   `requests`: For fetching images from URLs.
-   `duckduckgo-search`: For the web search functionality.

For a full list of dependencies, see the `requirements.txt` file.
