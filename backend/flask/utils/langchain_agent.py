from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama, GooglePalm
from langchain.chains import RetrievalQA
from utils.mode_detector import detect_mode
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import time
from functools import lru_cache
import logging
import requests
logger = logging.getLogger(__name__)
from langchain_google_genai import ChatGoogleGenerativeAI

# Constants
MAX_CODE_EXECUTION_TIME = 5  # seconds
ALLOWED_LIBS = ['pd', 'np', 'plt']
SYSTEM_PROMPTS = {
    'online_global': """You are DARA (Domain-Aware Research Assistant), with real-time data access. Provide:
1. Comprehensive industry analysis
2. Current market trends
3. Statistical projections
4. Cited sources when possible
5. Professional formatting""",

    'offline_global': """You are DARA (Domain-Aware Research Assistant), offline research assistant. Provide:
1. Fundamental principles explanation
2. Historical context
3. Theoretical frameworks
4. Clear uncertainty markers""",

    'online_file': """You are DARA (Domain-Aware Research Assistant). Analyze the provided data:
1. Combine dataset insights with domain knowledge
2. Generate actionable recommendations
3. Include statistical significance
4. Professional tone""",

    'offline_file': """You are DARA (Domain-Aware Research Assistant). Focus on:
1. Strictly dataset-bound insights
2. Clear visualizations
3. Numerical evidence
4. Conservative interpretations"""
}

@lru_cache(maxsize=1)
def get_embeddings():
    return OllamaEmbeddings(model="mistral")

def extract_gemini_content(response):
    """Extract clean content from ChatGoogleGenerativeAI response"""
    if hasattr(response, 'content'):
        # Direct access to content attribute if available
        return response.content
    
    # Convert to string and extract with regex
    response_str = str(response)
    
    # Try to find content between content=' and ' using regex
    content_match = re.search(r"content='(.*?)'(?:\s|$)", response_str, re.DOTALL)
    if content_match:
        # Handle escaped quotes in the content
        return content_match.group(1).replace("\\'", "'")
    
    # If all else fails, return the original string
    return response_str

def query_global(question: str) -> dict:
    """Handle global analysis without dataset"""
    try:
        mode = detect_mode()
        logger.debug(f"Global analysis mode: {mode}")
        
        if mode == 'online':
            if not os.getenv("GEMINI_API_KEY"):
                raise ValueError("Gemini API key not configured")
                
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-1.5-pro",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.4
            )

            prompt = f"{SYSTEM_PROMPTS['online_global']}\n\nQuestion: {question}"
            
            # Get response from LLM
            response = llm.invoke(prompt)
            
            # Extract clean content from response
            response_content = extract_gemini_content(response)
        else:
            # Verify Ollama service is running
            try:
                requests.get('http://localhost:11434', timeout=2)
            except:
                raise ConnectionError("Ollama service not available")
                
            llm = Ollama(
                model="mistral:instruct",
                temperature=0.7,
                system=SYSTEM_PROMPTS['offline_global']
            )
            prompt = f"{SYSTEM_PROMPTS['offline_global']}\n\nQuery: {question}"
            
            # Get response from LLM
            response = llm.invoke(prompt)
            
            # For Ollama, response is usually already a string
            response_content = str(response)
        
        return {
            'type': 'global_analysis',
            'content': response_content,
            'status': 'success'
        }

    except Exception as e:
        logger.error(f"Global analysis failed: {str(e)}")
        return {
            'type': 'error',
            'message': str(e),
            'status': 'error'
        }

def query_df(df: pd.DataFrame, question: str, vector_dir: str = ".vector_cache") -> dict:
    """Enhanced dataset analysis with mode awareness"""
    mode = detect_mode()
    intent = detect_code_intent(question)
    
    try:
        # Configure LLM based on mode
        if mode == 'online':
            llm = GooglePalm(
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.3,
                model_kwargs={'max_output_tokens': 1500}
            )
            system_prompt = SYSTEM_PROMPTS['online_file']
        else:
            llm = Ollama(
                model="mistral:instruct",
                temperature=0.7,
                system=SYSTEM_PROMPTS['offline_file']
            )
            system_prompt = SYSTEM_PROMPTS['offline_file']

        # RAG Pipeline
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        formatted_data = format_dataframe(df)
        chunks = text_splitter.split_text(formatted_data)
        
        vectordb = Chroma.from_texts(
            chunks,
            get_embeddings(),
            persist_directory=vector_dir,
            metadatas=[{"source": "uploaded_data"} for _ in chunks]
        )
        vectordb.persist()

        # Enhanced prompt engineering
        full_prompt = f"""{system_prompt}
        
        Dataset Overview:
        {formatted_data[:2000]}... [truncated]
        
        User Query: {question}
        
        Required Format: {"Code Solution" if intent['needs_code'] else "Textual Analysis"}
        """

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )
        
        response = qa_chain.invoke(full_prompt)

        # Process GooglePalm response if needed
        if mode == 'online':
            if 'result' in response and isinstance(response['result'], str):
                # Regular dictionary response
                pass
            else:
                # Handle potential Gemini-specific response format
                response_content = extract_gemini_content(response)
                response = {'result': response_content, 'source_documents': response.get('source_documents', [])}

        # Post-processing
        if intent['needs_code']:
            return process_code_response(response, df)
        return process_text_response(response, mode)

    except Exception as e:
        logger.error(f"Dataset analysis failed: {str(e)}")
        return {
            'type': 'error',
            'message': f"Analysis failed: {str(e)}",
            'mode': mode,
            'timestamp': int(time.time())
        }

def process_code_response(response: dict, df: pd.DataFrame) -> dict:
    """Handle code generation and execution"""
    code = re.sub(r'^```python|```$', '', response['result']).strip()
    exec_result = safe_code_execution(code, df)
    
    if 'error' in exec_result:
        return {
            'type': 'code_error',
            'content': exec_result['error'],
            'code': code,
            'timestamp': int(time.time())
        }
        
    if 'plot_path' in exec_result:
        return {
            'type': 'visual_analysis',
            'content': exec_result.get('result', ''),
            'plot_path': exec_result['plot_path'],
            'code': code,
            'timestamp': int(time.time())
        }
        
    return {
        'type': 'code_analysis',
        'content': str(exec_result.get('result', '')),
        'code': code,
        'timestamp': int(time.time())
    }

def process_text_response(response: dict, mode: str) -> dict:
    """Process textual analysis results"""
    return {
        'type': 'dataset_analysis',
        'content': response['result'],
        'sources': list(set([doc.metadata['source'] for doc in response['source_documents']])),
        'mode': mode,
        'timestamp': int(time.time())
    }

def detect_code_intent(question: str) -> dict:
    """Enhanced intent detection with pattern matching"""
    patterns = {
        'plot': r'\b(plot|graph|chart|visualize)\b',
        'calculate': r'\b(calculate|compute|derive|measure)\b',
        'code': r'\b(code|script|generate|write\s+python)\b'
    }
    
    return {
        'needs_code': any(re.search(pattern, question.lower()) for pattern in patterns.values()),
        'needs_plot': bool(re.search(patterns['plot'], question.lower()))
    }

def format_dataframe(df: pd.DataFrame) -> str:
    """Enhanced dataframe formatting for context"""
    return f"""DATA OVERVIEW
Columns ({len(df.columns)}): {', '.join(df.columns)}
First 3 Rows:
{df.head(3).to_string(index=False)}

Statistical Summary:
{df.describe().to_string()}

Missing Values:
{df.isnull().sum().to_string()}

Data Types:
{df.dtypes.to_string()}
"""

def safe_code_execution(code: str, df: pd.DataFrame) -> dict:
    """Secure code execution with resource limits"""
    # Security sanitization
    code = re.sub(r'(os|system|subprocess)\b', '', code)
    code = '\n'.join([line for line in code.split('\n') if not line.strip().startswith('!')])
    
    local_vars = {'df': df.copy(), 'np': np, 'plt': plt, 'pd': pd}
    exec_globals = {}
    
    try:
        start_time = time.time()
        exec(
            f"def _execute():\n    " + '\n    '.join(code.split('\n')) +
            "\nresult = _execute()",
            {'__builtins__': None, **local_vars},
            exec_globals
        )
        
        if time.time() - start_time > MAX_CODE_EXECUTION_TIME:
            raise TimeoutError("Execution timed out")
            
        result = exec_globals.get('result', 'No output')
        
        # Plot handling
        if plt.gcf().get_axes():
            plot_path = f"static/plots/plot_{int(time.time())}.png"
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()
            return {'plot_path': plot_path, 'result': result}
            
        return {'result': result}
        
    except Exception as e:
        return {'error': f"{type(e).__name__}: {str(e)}", 'code': code}