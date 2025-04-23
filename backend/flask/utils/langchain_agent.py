from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import time
from functools import lru_cache

# Constants
MAX_CODE_EXECUTION_TIME = 5  # seconds
ALLOWED_LIBS = ['pd', 'np', 'plt']

def detect_code_intent(question):
    """Classify query type with weighted keywords"""
    code_patterns = {
        'plot': 0.8,
        'graph': 0.7,
        'chart': 0.7,
        'calculate': 0.6,
        'compute': 0.6,
        'code': 0.9,
        'generate': 0.5,
        'visualize': 0.7
    }
    
    question_lower = question.lower()
    score = sum(
        weight for pattern, weight in code_patterns.items()
        if pattern in question_lower
    )
    
    return {
        'needs_code': score >= 0.7,
        'needs_plot': any(p in question_lower for p in ['plot', 'graph', 'chart'])
    }

@lru_cache(maxsize=100)
def get_embeddings():
    return OllamaEmbeddings(model="mistral")

def format_dataframe(df):
    """Convert DataFrame to analysis-friendly format"""
    return f"""
Columns: {', '.join(df.columns)}
Sample Data:
{df.head(3).to_string(index=False)}
Statistics:
{df.describe().to_string()}
    """.strip()

def safe_code_execution(code: str, df: pd.DataFrame):
    """Execute code in restricted environment"""
    local_vars = {
        'df': df.copy(),
        'np': np,
        'plt': plt,
        'pd': pd
    }
    
    # Security sanitization
    code = re.sub(r'(plt|pd|np)\.\w+\s*\(?', '', code)  # Remove method calls
    code = '\n'.join([line for line in code.split('\n') 
                     if not line.strip().startswith('!')])  # Remove shell cmds
    
    try:
        exec_globals = {}
        start_time = time.time()
        
        exec(
            f"def _execute(df):\n    " + 
            '\n    '.join(code.split('\n')) + 
            "\nresult = _execute(df.copy())",
            {'__builtins__': None, **{lib: local_vars[lib] for lib in ALLOWED_LIBS}},
            exec_globals
        )
        
        result = exec_globals['result']
        
        # Handle plots
        if plt.gcf().get_axes():
            plot_path = f"static/plots/plot_{int(time.time())}.png"
            plt.savefig(plot_path)
            plt.close()
            return {'plot_path': plot_path, 'result': result}
            
        return {'result': result}
    
    except Exception as e:
        return {'error': str(e), 'code': code}
    
    finally:
        if time.time() - start_time > MAX_CODE_EXECUTION_TIME:
            raise TimeoutError("Code execution timed out")

def query_df(df, question, vector_dir=".vector_cache"):
    intent = detect_code_intent(question)
    
    # RAG Configuration
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
        metadatas=[{"source": "data_context"} for _ in chunks]
    )
    
    # Prompt Engineering
    system_prompt = f"""You are a Data Analysis Assistant. Respond with:
    - {"Python code using pd/np/plt" if intent['needs_code'] else "concise explanation"}
    - Use ONLY these variables: df (DataFrame), np, plt, pd
    - Never use external data
    - Add brief comments
    - Format code without markdown
    
    Query: {question}"""
    
    # Model Configuration
    llm = Ollama(
        model="mistral:instruct",
        temperature=0.3 if intent['needs_code'] else 0.7,
        system=system_prompt,
        options={
            'num_ctx': 4096,
            'top_k': 40,
            'stop': ['```']
        }
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    
    response = qa_chain.invoke(question)
    
    # Post-processing
    if intent['needs_code']:
        code = re.sub(r'^```python|```$', '', response['result']).strip()
        exec_result = safe_code_execution(code, df)
        
        if 'error' in exec_result:
            return {
                'type': 'error',
                'message': f"Execution error: {exec_result['error']}",
                'code': code
            }
            
        if 'plot_path' in exec_result:
            return {
                'type': 'plot',
                'plot_path': exec_result['plot_path'],
                'caption': str(exec_result.get('result', '')),
                'code': code
            }
            
        return {
            'type': 'code_result',
            'content': str(exec_result.get('result', '')),
            'code': code
        }
        
    else:
        return {
            'type': 'explanation',
            'content': response['result'],
            'sources': [doc.metadata['source'] for doc in response['source_documents']]
        }