import streamlit as st
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Constants
GEMINI_API_KEY = "AIzaSyB0kq7WBtDOYs6E8ZfIgZ-BxjnyNL-6v2U"  # Replace with your Gemini API key

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "api_key" not in st.session_state:
        st.session_state.api_key = GEMINI_API_KEY
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_summary" not in st.session_state:
        st.session_state.last_summary = None

def check_api_key(api_key):
    """Verify if the API key is valid."""
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        return any("gemini" in model.name.lower() for model in models)
    except Exception:
        return False

def get_gemini_llm(api_key, temperature=0.7):
    """Create and return a Gemini LLM instance."""
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                  google_api_key=api_key,
                                  temperature=temperature,
                                  max_output_tokens=2048)

def summarize_text(text, length="Medium", api_key=None):
    """Summarize the given text using the Gemini API."""
    length_guide = {
        "Very Short": "Provide an extremely concise summary in 2-3 sentences.",
        "Short": "Provide a brief summary in a short paragraph.",
        "Medium": "Provide a comprehensive summary covering all main points.",
        "Detailed": "Provide a detailed summary with all important information and supporting details."
    }

    template = """
    You are an expert academic assistant helping a student summarize their notes.
    
    TEXT TO SUMMARIZE:
    {text}
    
    INSTRUCTIONS:
    {length_guide}
    - Focus on key concepts, definitions, and important points
    - Maintain academic language and technical terms
    - Organize information in a clear, logical structure
    - Include any formulas, theorems, or key dates if present
    
    SUMMARY:
    """

    prompt = PromptTemplate(input_variables=["text", "length_guide"], template=template)
    llm = get_gemini_llm(api_key, temperature=0.2)  # Lower temperature for summaries
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(text=text, length_guide=length_guide[length])
    return response

def answer_question(question, subject_area="General", context=None, api_key=None):
    """Answer academic questions using the Gemini API."""
    context_section = ""
    if context:
        context_section = f"""
        ADDITIONAL CONTEXT FROM STUDENT'S NOTES:
        {context}
        
        Use this context to inform your answer if relevant to the question.
        """

    template = """
    You are an expert academic tutor specializing in {subject_area}.
    
    STUDENT QUESTION:
    {question}
    
    {context_section}
    
    INSTRUCTIONS:
    - Provide a comprehensive, educational answer 
    - Include key concepts and definitions
    - If applicable, mention different perspectives or theories
    - If the question is unclear, clarify your interpretation before answering
    - If the question asks for a step-by-step explanation, provide clear steps
    - Include examples if they would help illustrate the answer
    - If the question is requesting false or misleading information, politely correct any misconceptions
    
    ANSWER:
    """

    prompt = PromptTemplate(input_variables=["question", "subject_area", "context_section"], template=template)
    llm = get_gemini_llm(api_key, temperature=0.7)  # Higher temperature for creative answers
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(question=question, subject_area=subject_area, context_section=context_section)
    return response

def generate_study_tips(subject, goal, learning_style, additional_info="", api_key=None):
    """Generate personalized study tips using the Gemini API."""
    template = """
    You are an expert education consultant specializing in personalized study strategies.
    
    STUDENT INFORMATION:
    - Subject/Topic: {subject}
    - Study Goal: {goal}
    - Learning Style: {learning_style}
    - Additional Information: {additional_info}
    
    INSTRUCTIONS:
    - Provide 5-7 specific, actionable study tips tailored to the student's needs
    - Focus on evidence-based learning techniques relevant to their subject and goal
    - Include both general strategies and subject-specific approaches
    - Consider their learning style in your recommendations
    - Suggest specific tools, resources, or techniques that would be helpful
    - Format your response with clear headings, bullet points, and organization
    
    PERSONALIZED STUDY TIPS:
    """

    prompt = PromptTemplate(input_variables=["subject", "goal", "learning_style", "additional_info"], template=template)
    llm = get_gemini_llm(api_key, temperature=0.8)  # Higher temperature for personalized tips
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(subject=subject, goal=goal, learning_style=learning_style, additional_info=additional_info)
    return response

# App configuration
st.set_page_config(
    page_title="AstraLearn",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
initialize_session_state()

# Clean and minimal sidebar
with st.sidebar:
    st.title("AstraLearn")
    st.markdown("Your AI-powered study companion.")
    
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your Gemini API key or use the default."
    )
    
    if api_key:
        st.session_state.api_key = api_key
        if check_api_key(api_key):
            st.success("API Key is valid!")
        else:
            st.error("Invalid API Key. Please check and try again.")
    
    st.markdown("---")
    st.markdown("""
    **About AstraLearn**  
    - Summarize notes  
    - Answer academic questions  
    - Generate personalized study tips  
    Powered by Google's Gemini API.
    """)

# Main content
st.title("AstraLearn")
st.markdown("Simplify your studies with AI-driven note summarization, Q&A, and tailored study tips.")

# Tabs for functionalities
tab1, tab2, tab3 = st.tabs(["📝 Summarize Notes", "❓ Ask Questions", "💡 Study Tips"])

# Summarize Notes tab
with tab1:
    st.header("Summarize Notes")
    st.markdown("Paste your notes to get a concise summary.")
    
    notes_text = st.text_area(
        "Your Notes",
        height=200,
        placeholder="Paste your notes here...",
        key="notes_input"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        summarize_button = st.button("Summarize", use_container_width=True)
    with col2:
        summary_length = st.select_slider(
            "Summary Length",
            options=["Very Short", "Short", "Medium", "Detailed"],
            value="Medium"
        )
    
    if summarize_button and notes_text:
        if not st.session_state.api_key:
            st.error("Please enter a valid Gemini API Key in the sidebar.")
        else:
            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_text(notes_text, summary_length, st.session_state.api_key)
                    st.session_state.last_summary = summary
                    st.success("Summary generated!")
                    st.markdown("### Summary")
                    st.markdown(summary)
                    st.markdown("---")
                    
                    # Add to history
                    history_item = {
                        "type": "summary",
                        "input": notes_text[:100] + "..." if len(notes_text) > 100 else notes_text,
                        "output": summary[:100] + "..." if len(summary) > 100 else summary
                    }
                    st.session_state.history.insert(0, history_item)
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")

# Answer Questions tab
with tab2:
    st.header("Ask Academic Questions")
    st.markdown("Get detailed answers to your academic queries.")
    
    use_summary_context = False
    if st.session_state.get("last_summary"):
        use_summary_context = st.checkbox("Use last summary as context")
    
    question = st.text_input(
        "Your Question",
        placeholder="E.g., What are the key factors that led to World War II?",
        key="question_input"
    )
    
    subject_area = st.selectbox(
        "Subject Area",
        ["General", "Mathematics", "Science", "History", "Literature", "Computer Science", 
         "Economics", "Philosophy", "Arts", "Social Sciences"]
    )
    
    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question.")
        elif not st.session_state.api_key:
            st.error("Please enter a valid Gemini API Key in the sidebar.")
        else:
            context = st.session_state.last_summary if use_summary_context else None
            with st.spinner("Generating answer..."):
                try:
                    answer = answer_question(question, subject_area, context, st.session_state.api_key)
                    st.markdown("### Answer")
                    st.markdown(answer)
                    
                    # Add to history
                    history_item = {
                        "type": "question",
                        "input": question,
                        "output": answer[:100] + "..." if len(answer) > 100 else answer
                    }
                    st.session_state.history.insert(0, history_item)
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")

# Study Tips tab
with tab3:
    st.header("Personalized Study Tips")
    st.markdown("Receive tailored study strategies for your needs.")
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input(
            "Subject/Topic",
            placeholder="E.g., Organic Chemistry, Calculus",
            key="subject_input"
        )
    with col2:
        goal = st.selectbox(
            "Study Goal",
            ["Exam Preparation", "Long-term Retention", "Understanding Complex Concepts", 
             "Improving Focus", "Time Management", "Note-taking", "Memory Improvement"]
        )
    
    learning_style = st.selectbox(
        "Learning Style",
        ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Not Sure"]
    )
    
    additional_info = st.text_area(
        "Additional Information",
        placeholder="Any specific challenges or preferences...",
        height=100
    )
    
    if st.button("Generate Study Tips"):
        if not subject:
            st.warning("Please enter a subject.")
        elif not st.session_state.api_key:
            st.error("Please enter a valid Gemini API Key in the sidebar.")
        else:
            with st.spinner("Generating study tips..."):
                try:
                    tips = generate_study_tips(subject, goal, learning_style, additional_info, st.session_state.api_key)
                    st.markdown("### Your Study Tips")
                    st.markdown(tips)
                    
                    # Add to history
                    history_item = {
                        "type": "study_tips",
                        "input": f"Subject: {subject}, Goal: {goal}",
                        "output": tips[:100] + "..." if len(tips) > 100 else tips
                    }
                    st.session_state.history.insert(0, history_item)
                except Exception as e:
                    st.error(f"Error generating study tips: {str(e)}")

# History section
if st.session_state.get("history"):
    st.markdown("---")
    with st.expander("📜 History", expanded=False):
        for i, item in enumerate(st.session_state.history[:10]):
            st.markdown(f"**{item['type'].title()}**: {item['input']}")
            st.markdown(f"**Response**: {item['output']}")
            if i < len(st.session_state.history[:10]) - 1:
                st.markdown("---")
        
        if len(st.session_state.history) > 10:
            st.markdown(f"*{len(st.session_state.history) - 10} more interactions not shown*")
        
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
