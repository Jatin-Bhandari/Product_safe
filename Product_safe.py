from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnableSequence
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun
import requests
import base64
from dotenv import load_dotenv


load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
search_tool = DuckDuckGoSearchRun()
llm_with_tools = llm.bind_tools([search_tool])
parser = StrOutputParser()

def get_template_from_image(image_path_or_url):
    """
    Identifies a product from an image using LangChain with Gemini.

    Args:
        image_path_or_url: The local file path or URL of the product image.

    Returns:
        A string containing the identified product information or an error message.
    """
    try:
        # --- 1. Load Image ---
        if image_path_or_url.startswith(("http://", "https://")):
            # Handle URL
            response = requests.get(image_path_or_url)
            response.raise_for_status()
            image_bytes = response.content
        else:
            # Handle local file path
            with open(image_path_or_url, "rb") as image_file:
                image_bytes = image_file.read()

        # --- 2. Prepare the Prompt and Image for LangChain ---
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
    
    
h_msg = get_template_from_image("Kurkure.jpg")

chat_history = [
    SystemMessage(content=(
        """You are an expert dietitian and nutritionist. Provide clear, evidence-based guidance on what foods and nutrients to consume for overall health, recommended portions, and which foods or ingredients are harmful or should be avoided. Prioritize safety, note common contraindications and allergies, and advise when to consult a healthcare professional. Be concise and practical."""
    )),
    h_msg
]

# from langchain_core.prompts import ChatPromptTemplate

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
    if result.tool_calls == []:
        return result
    search_results = []
    for tool_call in result.tool_calls:
        search_result = search_tool.invoke(tool_call)
        search_results.append(parser.invoke(search_result))
    return ','.join(search_results)

all_results = RunnableLambda(run_searches)


final_prompt = PromptTemplate(
    template='''Using the following two results, compile a final concise report:
    Result 1: {Result_1}
    Result 2: {Result_2}''',
    input_variables=['Result_1', 'Result_2']
)

first_chain = RunnableSequence(llm, parser)

parallel_chain = RunnableParallel({
    'Result_1': prompt_2 | llm | parser,
    'Result_2': prompt_3 | llm_with_tools | all_results | parser | llm | parser
})

last_chain = RunnableSequence(final_prompt, llm, parser)

chain = RunnableSequence(first_chain, parallel_chain, last_chain)

result = chain.invoke(chat_history)

print(result)


