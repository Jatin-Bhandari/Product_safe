# Product Safety Checker

This project uses the Gemini API to analyze an image of a product and extract key information, such as the product name, ingredients, brand, and safety warnings. This tool can be used to quickly get details about a product from its packaging.

## Features

-   Analyzes product images from a local file path or a URL.
-   Extracts structured information including:
    -   Product Name
    -   Product Type
    -   Ingredients
    -   Brand
    -   Certifications and Warnings
-   Uses the power of the Gemini large language model for image analysis.

## How It Works

The script takes an image of a product as input and performs the following steps:

1.  **Load Image**: The script loads the image from either a local file path or a URL.
2.  **Prepare Prompt**: It prepares a prompt for the Gemini API, instructing it to analyze the image and extract specific information in a structured format.
3.  **API Call**: The script sends the image and the prompt to the Gemini API using the `langchain` library.
4.  **Display Results**: The structured information returned by the API is then displayed to the user.

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

4.  **Set up your environment variables:**
    Create a `.env` file in the root of the project and add your Google API key:
    ```
    GOOGLE_API_KEY="your_google_api_key"
    ```

## Usage

You can run the project from the `Product_safety_checker.ipynb` notebook.

1.  Open the notebook in a Jupyter environment.
2.  Run the cells in the notebook.
3.  When prompted, enter the local file path or URL of the product image you want to analyze.

The script will then output the extracted information from the product image.

## Dependencies

The main dependencies for this project are:

-   `langchain-google-genai`: For interacting with the Gemini API.
-   `requests`: For fetching images from URLs.
-   `python-dotenv`: For managing environment variables.
-   `Pillow`: For image manipulation.

For a full list of dependencies, see the `requirements.txt` file.

## Example

Here is an example of the output for an image of a "Kurkure" snack packet:

```
--- Product Identification Results ---
Here's the structured information extracted from the product image:

1.  **Product Name:** Kurkure
2.  **Product Type:** Snack (Namkeen), Food
3.  **Extracted Information:**
    *   **Brand Statement:** "Kurkure is a Registered Trade Mark of PepsiCo, Inc."
    *   **Manufacturer Details:** "MFD. BY: For manufacturer's details, see first two characters of batch no. and see below."
        *   N1 - PepsiCo India Holdings Pvt. Ltd., Lic. No. 10012063000110.
        *   N2 - PepsiCo India Holdings Pvt. Ltd., Lic. No. 10012022000339.
...
4.  **Brand:** Kurkure (a trademark of PepsiCo, Inc.)
5.  **Summary:** Kurkure is a 36g pack of proprietary savory namkeen snack, a trademark of PepsiCo, Inc., made from cereal products, spices, and seasonings, containing onion and garlic, and marketed by PepsiCo India Holdings Pvt. Ltd.

------------------------------------
```
