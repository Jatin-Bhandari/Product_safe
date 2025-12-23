from flask import Flask, request, jsonify, render_template
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnableSequence
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
import base64
import os

app = Flask(__name__)

def get_template_from_image(image_bytes):
    """
    Identifies a product from image bytes using LangChain with Gemini.
    """
    try:
        prompt_text = """
        Analyze the provided image of a product and return the following information in a structured manner with clear labels without bold or italics. The information to extract includes:
        1.  Product Name: The primary name of the product.
        2.  Product Type: The category of the product (e.g., Food, Cosmetic, Cleaning Supply).
        3.  Extracted Information: All ingredients and chemicals, and warnings and certifications.
        4.  Brand: The brand name of the product.
        Provide the response in a clear and concise format. If any information is not available, indicate it as "Not Available". Do not include any additional commentary or explanations.
        """
        
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_b64}",
                },
            ]
        )
        return message
    except Exception as e:
        return f"Error loading image: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    api_key = request.form.get('api_key')

    if not api_key:
        return jsonify({'error': 'No API key provided'}), 400

    try:
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        search_tool = DuckDuckGoSearchRun()
        llm_with_tools = llm.bind_tools([search_tool])
        parser = StrOutputParser()

        image_bytes = image_file.read()
        h_msg = get_template_from_image(image_bytes)

        chat_history = [
            SystemMessage(content=(
                """You are an expert dietitian and nutritionist. Provide clear, evidence-based guidance on what foods and nutrients to consume for overall health, recommended portions, and which foods or ingredients are harmful or should be avoided. Prioritize safety, note common contraindications and allergies, and advise when to consult a healthcare professional. Be concise and practical."""
            )),
            h_msg
        ]

        prompt_2 = PromptTemplate(
            template='''Analyze the product below and return a concise, structured report with clear labels (no bold or italics). 
            Use {product_info} as the source. Include:
        - Product Summary: one-line description.
        - Pros: short bullet list of benefits.
        - Cons: short bullet list of risks/harmful aspects.
        - Nutritional & Safety Considerations: key points (fat, sodium, sugar, allergens, additives) and any special cautions.
        - Who Should Limit/Avoid: specific populations.
        - Recommended Serving/Frequency: practical guidance.
        - Regulatory Status: allowed/banned status for product and key additives in India, EU, USA, Canada, Australia (or "Not Available" if unknown).
        - Healthier Alternatives or Tips: brief suggestions.
            
        Do not add extra commentary; be concise, small and user-focused.''',
            input_variables=['product_info']
        )

        prompt_3 = PromptTemplate(
            template='''You have access to the duckduckgo_search tool. Using the information in {product_info}, perform searches for the latest news, health advisories, recalls, or bans related to:
            - the Product Name,
            - the Brand,
            - each chemical/additive listed (include both common names and numeric codes like "160c", "627", etc.).

            For each target (product/brand/chemical) run country-specific queries for: India, EU, USA, Canada, Australia (include the country name in the query). Prioritize results from the past 1 year; if none, expand to the past 5 years.

            For each relevant result return (concise, structured):
            - Target: (product/brand/chemical)
            - Country:
            - Type: (Health advisory / Ban / Recall / News)
            - Date:
            - Source URL:
            - 1-line summary.
            - DuckDuckGo Query Used:

            If no relevant results are found for a given target/country, return: "No recent advisories found".

            Be concise and only return the structured findings. Do not add extra commentary.''',
            input_variables=['product_info']
        )

        def run_searches(result):
            if not result.tool_calls:
                return result.content
            search_results = []
            for tool_call in result.tool_calls:
                search_result = search_tool.invoke(tool_call['args'])
                search_results.append(search_result)
            return ', '.join(search_results) if search_results else "No search results found."

        all_results = RunnableLambda(run_searches)

        final_prompt = PromptTemplate(
            template='''Based on the internal analysis and external search results below, create a single, well-structured, Small, and easy-to-read report for a consumer.

Use Markdown for formatting. Use headings (`###`), bold text (`**word**`), and bullet points (`- point`).

**Internal Analysis:**
{Result_1}

**External Search Results:**
{Result_2}

---

Compile all this information into a single, final report below.
''',
            input_variables=['Result_1', 'Result_2']
        )

        first_chain = llm | parser

        parallel_chain = RunnableParallel({
            'Result_1': prompt_2 | llm | parser,
            'Result_2': prompt_3 | llm_with_tools | all_results | llm | parser
        })
        
        # Correctly creating the final chain
        def format_for_final_prompt(intermediate_results):
            # This function prepares the input for the final_prompt
            return {"Result_1": intermediate_results['Result_1'], "Result_2": intermediate_results['Result_2']}

        # The overall chain
        chain = (
            first_chain
            | RunnableLambda(lambda product_info: {"product_info": product_info}) # Pass the output of first_chain as 'product_info' to the parallel chains
            | parallel_chain
            | RunnableLambda(format_for_final_prompt) # Prepare for the final prompt
            | final_prompt
            | llm
            | parser
        )
        
        result = chain.invoke(chat_history)

        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
