"""
Agentic RAG pipeline with LangChain for intelligent query processing
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.tools import Tool, BaseTool
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks import AsyncCallbackHandler
from langchain.schema import BaseMessage

# Internal services
from .document_ingestion import DocumentIngestionPipeline
from .open_source_embeddings import get_embedding_service
from .open_source_llms import get_open_source_llm
from .open_source_search import get_search_service
from .open_source_monitoring import get_monitoring_service
from ..core.config import settings
from ..models.user import UserRole


class OpenSourceCallbackHandler(AsyncCallbackHandler):
    """Custom callback handler for open-source monitoring"""
    
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.metrics = {}
        self.monitoring = get_monitoring_service()
    
    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs):
        self.start_time = datetime.now()
        self.metrics = {"inputs": inputs}
    
    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.metrics["duration"] = duration
            self.metrics["outputs"] = outputs


class DocumentRetrievalTool(BaseTool):
    """Tool for retrieving relevant documents from vector store"""
    
    name = "document_retrieval"
    description = """
    Retrieve relevant documents from the internal knowledge base.
    Use this tool to find information from company documents, policies, procedures, and internal knowledge.
    Input should be a search query describing what information you're looking for.
    """
    
    def __init__(self, ingestion_pipeline: DocumentIngestionPipeline, user_role: str, department: str = None):
        super().__init__()
        self.ingestion_pipeline = ingestion_pipeline
        self.user_role = user_role
        self.department = department
    
    async def _arun(self, query: str) -> str:
        """Async implementation of document retrieval"""
        try:
            results = await self.ingestion_pipeline.search_documents(
                query=query,
                user_role=self.user_role,
                department=self.department,
                k=settings.TOP_K_RETRIEVAL
            )
            
            if not results:
                return "No relevant documents found in the knowledge base."
            
            # Format results for the agent
            formatted_results = []
            for i, result in enumerate(results, 1):
                content = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
                metadata = result.get('metadata', {})
                
                formatted_results.append(f"""
Document {i}:
Content: {content}
Source: {metadata.get('file_name', 'Unknown')}
Department: {metadata.get('department', 'General')}
Relevance Score: {1 - result.get('distance', 0):.2f}
""")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error retrieving documents: {str(e)}"
    
    def _run(self, query: str) -> str:
        """Sync wrapper for async implementation"""
        return asyncio.run(self._arun(query))


class WebSearchTool(BaseTool):
    """Tool for web search augmentation using open-source search"""
    
    name = "web_search"
    description = """
    Search the web for current information, news, or data not available in internal documents.
    Use this tool when the internal knowledge base doesn't have sufficient information
    or when you need current/recent information.
    Input should be a search query.
    """
    
    def __init__(self):
        super().__init__()
        self.search_service = get_search_service()
    
    async def _arun(self, query: str) -> str:
        """Async implementation of web search"""
        if not self.search_service.is_available():
            return "Web search is not available. No search engines configured."
        
        try:
            response = await self.search_service.search(
                query=query,
                max_results=settings.WEB_SEARCH_MAX_RESULTS,
                extract_content=settings.EXTRACT_ARTICLE_CONTENT,
                preferred_engine=settings.WEB_SEARCH_ENGINE
            )
            
            if not response.get('results'):
                return "No relevant web results found."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(response['results'], 1):
                content = result.get('content', 'No content')
                if len(content) > 400:
                    content = content[:400] + "..."
                
                formatted_results.append(f"""
Web Result {i}:
Title: {result.get('title', 'No title')}
Content: {content}
URL: {result.get('url', 'No URL')}
Source: {result.get('source', 'Unknown')}
""")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def _run(self, query: str) -> str:
        """Sync wrapper for async implementation"""
        return asyncio.run(self._arun(query))


class KnowledgeAnalysisTool(BaseTool):
    """Tool for analyzing and synthesizing information"""
    
    name = "knowledge_analysis"
    description = """
    Analyze and synthesize information from multiple sources to provide comprehensive answers.
    Use this tool to combine information from documents and web search results.
    Input should be the information to analyze and the original question.
    """
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__()
        self.llm = llm
    
    async def _arun(self, analysis_input: str) -> str:
        """Async implementation of knowledge analysis"""
        try:
            analysis_prompt = f"""
            Analyze the following information and provide a comprehensive, accurate answer:
            
            {analysis_input}
            
            Instructions:
            1. Synthesize information from all sources
            2. Identify any conflicts or inconsistencies
            3. Provide a clear, well-structured answer
            4. Cite sources when possible
            5. Note any limitations or uncertainties
            """
            
            response = await self.llm.ainvoke(analysis_prompt)
            return response.content
            
        except Exception as e:
            return f"Error analyzing information: {str(e)}"
    
    def _run(self, analysis_input: str) -> str:
        """Sync wrapper for async implementation"""
        return asyncio.run(self._arun(analysis_input))


class AgenticRAGPipeline:
    """Main agentic RAG pipeline orchestrator"""
    
    def __init__(self):
        # Initialize open-source LLM
        self.llm = get_open_source_llm()
        
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.callback_handler = OpenSourceCallbackHandler()
        self.monitoring = get_monitoring_service()
        
        # Memory for conversation context
        self.memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize services
        self.embedding_service = get_embedding_service()
        self.search_service = get_search_service()
    
    
    def _create_agent_tools(self, user_role: str, department: str = None) -> List[BaseTool]:
        """Create tools for the agent based on user role"""
        tools = [
            DocumentRetrievalTool(self.ingestion_pipeline, user_role, department),
            KnowledgeAnalysisTool(self.llm)
        ]
        
        # Add web search tool if available
        if self.search_service.is_available():
            tools.append(WebSearchTool())
        
        return tools
    
    def _create_agent_prompt(self, user_role: str) -> PromptTemplate:
        """Create role-specific agent prompt for ReAct agent"""
        
        role_context = {
            "employee": "You are an AI assistant helping an employee. Provide helpful information while respecting access controls.",
            "manager": "You are an AI assistant helping a manager. You have access to additional management information and can provide strategic insights.",
            "admin": "You are an AI assistant helping an administrator. You have full access to all information and can provide comprehensive insights."
        }
        
        template = f"""
        {role_context.get(user_role, role_context["employee"])}
        
        You have access to the following tools:
        {{tools}}
        
        Use the following format:
        
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{{tool_names}}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Guidelines:
        1. Always try to find information in internal documents first using document_retrieval
        2. Use web_search only when internal information is insufficient or outdated
        3. Use knowledge_analysis to synthesize information from multiple sources
        4. Provide accurate, well-sourced answers
        5. Respect role-based access controls
        6. If you cannot find information, clearly state this
        7. Always cite your sources
        
        When providing your Final Answer:
        - Be concise but comprehensive
        - Structure your response clearly
        - Highlight key points
        - Provide actionable insights when appropriate
        - Include source citations
        
        Question: {{input}}
        Thought: {{agent_scratchpad}}
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "{{tools}}",
                "tool_names": "{{tool_names}}"
            }
        )
    
    async def create_agent_executor(self, user_role: str, department: str = None) -> AgentExecutor:
        """Create agent executor for the user"""
        tools = self._create_agent_tools(user_role, department)
        prompt = self._create_agent_prompt(user_role)
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            max_execution_time=60,
            callbacks=[self.callback_handler],
            handle_parsing_errors=True
        )
        
        return executor
    
    async def process_query(self, query: str, user_role: str, department: str = None, 
                          use_web_search: bool = False) -> Dict[str, Any]:
        """Process a user query through the agentic RAG pipeline"""
        
        # Start monitoring
        async with self.monitoring.monitor_operation(
            name="query_processing",
            run_type="query",
            inputs={"query": query, "user_role": user_role, "use_web_search": use_web_search},
            metadata={"user_role": user_role, "department": department},
            user_role=user_role
        ) as run:
            try:
                # Create agent executor
                executor = await self.create_agent_executor(user_role, department)
                
                # Prepare input
                agent_input = {
                    "input": query,
                    "use_web_search": use_web_search
                }
                
                # Execute agent
                result = await executor.ainvoke(agent_input)
                
                # Extract sources from agent execution
                sources = self._extract_sources_from_result(result)
                
                response = {
                    "answer": result["output"],
                    "sources": sources,
                    "confidence_score": self._calculate_confidence_score(result),
                    "processing_time": 0,  # Will be set by monitoring
                    "user_role": user_role,
                    "department": department,
                    "used_web_search": use_web_search,
                    "status": "success"
                }
                
                # Update run with outputs
                run.outputs = response
                
                return response
                
            except Exception as e:
                error_response = {
                    "answer": f"I apologize, but I encountered an error processing your query: {str(e)}",
                    "sources": [],
                    "confidence_score": 0.0,
                    "processing_time": 0,
                    "status": "error",
                    "error": str(e)
                }
                
                # Update run with error
                run.outputs = error_response
                
                return error_response
    
    def _extract_sources_from_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract source information from agent result"""
        sources = []
        
        # This would be enhanced to properly extract sources from the agent's execution
        # For now, we'll return a placeholder structure
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                if isinstance(step, tuple) and len(step) == 2:
                    action, observation = step
                    if hasattr(action, 'tool') and action.tool == "document_retrieval":
                        sources.append({
                            "type": "document",
                            "content": observation[:200] + "..." if len(observation) > 200 else observation,
                            "tool_used": action.tool
                        })
                    elif hasattr(action, 'tool') and action.tool == "web_search":
                        sources.append({
                            "type": "web",
                            "content": observation[:200] + "..." if len(observation) > 200 else observation,
                            "tool_used": action.tool
                        })
        
        return sources
    
    def _calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result quality"""
        # Simple heuristic - this could be enhanced with more sophisticated scoring
        base_score = 0.7
        
        # Increase confidence if sources were found
        if "intermediate_steps" in result and result["intermediate_steps"]:
            base_score += 0.2
        
        # Increase confidence if answer is substantial
        if "output" in result and len(result["output"]) > 100:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        messages = self.memory.chat_memory.messages
        history = []
        
        for message in messages:
            history.append({
                "type": message.__class__.__name__,
                "content": message.content,
                "timestamp": datetime.now().isoformat()  # This would be stored properly in production
            })
        
        return history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.memory.clear()