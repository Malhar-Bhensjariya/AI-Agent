from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .utils.logger import log
from .utils.chroma_memory import store_interaction, retrieve_context
import os
from pymongo import MongoClient


# Setup Mongo client (lazy)
_mongo_client = None
_mongo_db = None

def _get_mongo():
    global _mongo_client, _mongo_db
    if _mongo_client is not None:
        return _mongo_db

    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        # attempt to construct from provided template and env password
        template = 'mongodb+srv://malhar:<db_password>@cluster0.kwb9l6o.mongodb.net/?appName=Cluster0'
        pwd = os.getenv('MONGO_PASSWORD')
        if not pwd:
            return None
        mongo_uri = template.replace('<db_password>', pwd)

    try:
        _mongo_client = MongoClient(mongo_uri)
        _mongo_db = _mongo_client.get_database()  # default DB from URI
        return _mongo_db
    except Exception:
        _mongo_client = None
        _mongo_db = None
        return None
import os
from dotenv import load_dotenv

load_dotenv()

class ChatAgentExecutor:
    def __init__(self):
        # Initialize Gemini model for LangChain
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7,  # Higher temperature for more conversational responses
            convert_system_message_to_human=True
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI Data Analyst (AIDA) assistant. Your role is to have natural conversations with users and provide helpful responses.

PERSONALITY TRAITS:
- Be conversational, warm, and approachable
- Provide helpful and informative responses
- Ask follow-up questions when appropriate
- Show empathy and understanding
- Be concise but thorough in your explanations

CONVERSATION GUIDELINES:
1. Engage in natural, flowing conversations
2. Answer questions across a wide range of topics
3. Provide explanations, advice, and information as needed
4. Maintain a positive and supportive tone
5. If you don't know something, admit it and offer to help find the information
6. Keep responses engaging and relevant to the user's interests

TOPICS YOU CAN DISCUSS:
- General knowledge and information
- Advice and recommendations
- Creative writing and brainstorming
- Problem-solving and explanations
- Casual conversation and small talk
- Learning and educational topics

Remember to be helpful while keeping the conversation natural and enjoyable!"""),
            ("human", "{input}"),
        ])

        # Create the chain with output parser
        self.chain = self.prompt | self.llm | StrOutputParser()

    def execute(self, question: str = None, file_path: str = None, file_bytes: bytes = None, user_id: str = None) -> str:
        """Execute a conversational query with optional file context.

        Backwards-compatible: accepts `file_bytes` and `question` keywords used
        by existing controllers. `user_id` is used for RAG memory lookup.
        """
        try:
            input_question = question
            log(f"Chat Agent - User Input: {input_question}", "INFO")

            # Retrieve nearby interactions from RAG memory (if any)
            retrieved = None
            try:
                if input_question:
                    retrieved = retrieve_context(user_id or 'global', input_question, k=5)
            except Exception:
                retrieved = None

            # If file_path or file_bytes is provided, mention it in the prompt
            file_notice = None
            if file_path:
                file_notice = f"Note: User has uploaded a file at {file_path}."
                log(f"Chat Agent - Processing with file context: {file_path}", "INFO")
            elif file_bytes:
                file_notice = "Note: User has uploaded binary file content for analysis."
                log(f"Chat Agent - Processing with file bytes", "INFO")

            # Build full input combining retrieved context and file notice
            parts = []
            if retrieved:
                parts.append(f"Context from previous conversation or memory:\n{retrieved}")
            if file_notice:
                parts.append(file_notice)
            if input_question:
                parts.append(f"User message: {input_question}")

            full_input = "\n\n".join(parts) if parts else input_question or ""

            # Generate response using the chain
            response = self.chain.invoke({
                "input": full_input
            })

            # Store interaction in RAG memory and Mongo
            try:
                if input_question and response is not None:
                    store_interaction(user_id or 'global', input_question, response)
                    # store chat message in Mongo
                    db = _get_mongo()
                    if db is not None:
                        try:
                            coll = db.get_collection('chat_messages')
                            coll.insert_one({
                                'user_id': user_id or 'global',
                                'query': input_question,
                                'response': response,
                                'ts': int(time.time())
                            })
                        except Exception:
                            pass
            except Exception:
                pass

            log(f"Chat Agent - Response Generated: {len(response)} characters", "INFO")
            return {'response': response, 'retrieved_memory': retrieved}

        except Exception as e:
            error_msg = f"Chat Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return "I apologize, but I encountered an error while processing your message. Please try again or rephrase your question."

    def execute_with_context(self, question: str, context: str = None) -> str:
        """Execute a conversational query with additional context"""
        try:
            if context:
                full_input = f"Context: {context}\n\nUser Question: {question}"
                log(f"Chat Agent - User Input with Context: {question}", "INFO")
            else:
                full_input = question
                log(f"Chat Agent - User Input: {question}", "INFO")
            
            # Generate response using the chain
            response = self.chain.invoke({
                "input": full_input
            })
            
            log(f"Chat Agent - Response Generated: {len(response)} characters", "INFO")
            return response

        except Exception as e:
            error_msg = f"Chat Agent execution error: {str(e)}"
            log(error_msg, "ERROR")
            return "I apologize, but I encountered an error while processing your message. Please try again or rephrase your question."