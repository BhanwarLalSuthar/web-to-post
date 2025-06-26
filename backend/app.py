import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel

# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not TAVILY_API_KEY or not GOOGLE_API_KEY:
    raise RuntimeError("Ensure TAVILY_API_KEY and GOOGLE_API_KEY are set in .env")

# Initialize clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# 1. Search Function
def web_search(user_query: str) -> str:
    response = tavily.search(query=user_query, max_results=5, search_depth="basic")
    return "
".join([r.get("content", "") for r in response.get("results", [])])

# 2. Summarization Chain
summary_prompt = ChatPromptTemplate.from_template(
    """
You are a research assistant.
Summarize the following content into 4–5 clear, informative bullet points:
{content}
"""
)

# 3. Draft Generation Chains
drafts_prompts = {
    "LinkedIn": ChatPromptTemplate.from_template(
        """
You are a social media manager. Write a professional LinkedIn post based on this summary:
{summary}
"""),
    "Twitter": ChatPromptTemplate.from_template(
        """
You are a social media expert. Write a catchy Twitter post under 280 characters based on this summary:
{summary}
"""),
    "Instagram": ChatPromptTemplate.from_template(
        """
You are a fun content creator. Write an Instagram caption with emojis and friendly tone based on this summary:
{summary}
""")
}
draft_chain = RunnableParallel({k: prompt | llm for k, prompt in drafts_prompts.items()})

# 4. Polishing Chains (individual)
polish_prompts = {
    "LinkedIn": ChatPromptTemplate.from_template(
        """
Polish this LinkedIn post to be professional and concise:
{post}
"""),
    "Twitter": ChatPromptTemplate.from_template(
        """
Polish this Twitter post to be punchy, under 280 characters:
{post}
"""),
    "Instagram": ChatPromptTemplate.from_template(
        """
Polish this Instagram caption to be emoji-friendly and engaging:
{post}
"""
    )
}
polish_chain = RunnableParallel({k: prompt | llm for k, prompt in polish_prompts.items()})

@app.route('/api/generate', methods=['POST'])
def generate_content():
    data = request.get_json(force=True)
    user_prompt = data.get('prompt', '').strip()
    if not user_prompt:
        return jsonify({"error": "Missing 'prompt' field."}), 400

    # Step 1: Web search and summary
    content = web_search(user_prompt)
    summary_output = (summary_prompt | llm).invoke({"content": content})
    summary = summary_output.content if hasattr(summary_output, 'content') else str(summary_output)

    # Step 2: Generate raw drafts
    raw_drafts = draft_chain.invoke({"summary": summary})
    drafts = {k: (v.content if hasattr(v, 'content') else str(v)) for k, v in raw_drafts.items()}

    # Step 3: Polish each draft
    polished = polish_chain.invoke({"post": drafts})
    final = {k: (v.content if hasattr(v, 'content') else str(v)) for k, v in polished.items()}

    return jsonify({"summary": summary, "drafts": final})

if __name__ == '__main__':
    app.run(port=5000, debug=True)