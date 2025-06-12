from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.logger import log
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

    def execute(self, question: str, file_path: str = None) -> str:
        """Execute a conversational query with optional file context"""
        try:
            log(f"Chat Agent - User Input: {question}", "INFO")
            
            # If file_path is provided, add context about file availability
            if file_path:
                context_input = f"Note: User has uploaded a file at {file_path}. If they ask about data analysis, let them know they should use specific data analysis commands.\n\nUser message: {question}"
                log(f"Chat Agent - Processing with file context: {file_path}", "INFO")
            else:
                context_input = question
            
            # Generate response using the chain
            response = self.chain.invoke({
                "input": context_input
            })
            
            log(f"Chat Agent - Response Generated: {len(response)} characters", "INFO")
            return response

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