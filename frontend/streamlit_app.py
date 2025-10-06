"""
Streamlit frontend for AI Knowledge Assistant
"""
import streamlit as st
import requests
import json
import time
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


class APIClient:
    """Client for interacting with the FastAPI backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={"username": username, "password": password}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register new user"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=user_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user info"""
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def query_assistant(self, query: str, use_web_search: bool = False) -> Dict[str, Any]:
        """Query the AI assistant"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/query/ask",
                json={
                    "query": query,
                    "use_web_search": use_web_search,
                    "max_results": 5
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def upload_document(self, file, title: str, access_level: str = "employee", department: str = None) -> Dict[str, Any]:
        """Upload a document"""
        try:
            files = {"file": file}
            data = {
                "title": title,
                "access_level": access_level,
                "department": department
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/documents/upload",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def list_documents(self) -> Dict[str, Any]:
        """List accessible documents"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/documents/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status (manager/admin only)"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/admin/system/status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get system analytics (manager/admin only)"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/admin/analytics")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient(API_BASE_URL)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def login_page():
    """Login page"""
    st.markdown('<h1 class="main-header">🤖 AI Knowledge Assistant</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username and password:
                    with st.spinner("Logging in..."):
                        result = st.session_state.api_client.login(username, password)
                    
                    if "error" not in result:
                        st.session_state.api_client.set_auth_token(result["access_token"])
                        st.session_state.authenticated = True
                        
                        # Get user info
                        user_info = st.session_state.api_client.get_current_user()
                        if "error" not in user_info:
                            st.session_state.user_info = user_info
                        
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
                else:
                    st.error("Please enter both username and password")
        
        st.markdown("---")
        
        # Registration section
        with st.expander("Don't have an account? Register here"):
            with st.form("register_form"):
                reg_email = st.text_input("Email", key="reg_email")
                reg_username = st.text_input("Username", key="reg_username")
                reg_full_name = st.text_input("Full Name", key="reg_full_name")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_role = st.selectbox("Role", ["employee", "manager", "admin"], key="reg_role")
                
                reg_submitted = st.form_submit_button("Register")
                
                if reg_submitted:
                    if all([reg_email, reg_username, reg_full_name, reg_password]):
                        user_data = {
                            "email": reg_email,
                            "username": reg_username,
                            "full_name": reg_full_name,
                            "password": reg_password,
                            "role": reg_role
                        }
                        
                        with st.spinner("Creating account..."):
                            result = st.session_state.api_client.register(user_data)
                        
                        if "error" not in result:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error(f"Registration failed: {result['error']}")
                    else:
                        st.error("Please fill in all fields")


def main_app():
    """Main application interface"""
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_info['full_name']}!")
        st.markdown(f"**Role:** {st.session_state.user_info['role'].title()}")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["Chat Assistant", "Document Management", "System Status", "Analytics"]
        )
    
    # Main content based on selected page
    if page == "Chat Assistant":
        chat_interface()
    elif page == "Document Management":
        document_management()
    elif page == "System Status":
        system_status()
    elif page == "Analytics":
        analytics_dashboard()


def chat_interface():
    """Chat interface for the AI assistant"""
    st.markdown('<h1 class="main-header">💬 AI Knowledge Assistant</h1>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input("Ask me anything about your organization's knowledge base:", key="chat_input")
    
    with col2:
        use_web_search = st.checkbox("Include web search", value=False)
    
    if st.button("Send", type="primary") or user_query:
        if user_query:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "type": "user",
                "content": user_query,
                "timestamp": datetime.now()
            })
            
            # Query the assistant
            with st.spinner("Thinking..."):
                response = st.session_state.api_client.query_assistant(user_query, use_web_search)
            
            if "error" not in response:
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "type": "assistant",
                    "content": response["answer"],
                    "sources": response.get("sources", []),
                    "confidence_score": response.get("confidence_score", 0),
                    "processing_time": response.get("processing_time", 0),
                    "timestamp": datetime.now()
                })
            else:
                st.error(f"Error: {response['error']}")
            
            # Clear input
            st.session_state.chat_input = ""
            st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Conversation")
        
        for message in reversed(st.session_state.chat_history[-10:]):  # Show last 10 messages
            if message["type"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                    <br><small>{message["timestamp"].strftime("%H:%M:%S")}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Assistant:</strong> {message["content"]}
                    <br><small>Confidence: {message.get("confidence_score", 0):.2f} | 
                    Processing time: {message.get("processing_time", 0):.2f}s | 
                    {message["timestamp"].strftime("%H:%M:%S")}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Show sources if available
                if message.get("sources"):
                    with st.expander("Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**Source {i}:** {source.get('type', 'Unknown')}")
                            st.markdown(f"Content: {source.get('content', 'No content')[:200]}...")
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


def document_management():
    """Document management interface"""
    st.markdown('<h1 class="main-header">📄 Document Management</h1>', unsafe_allow_html=True)
    
    # Upload section
    st.markdown("### Upload New Document")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'docx', 'md'],
            help="Supported formats: PDF, TXT, DOCX, MD"
        )
        
        if uploaded_file:
            title = st.text_input("Document Title", value=uploaded_file.name)
    
    with col2:
        if uploaded_file:
            access_level = st.selectbox("Access Level", ["employee", "manager", "admin"])
            department = st.text_input("Department (optional)")
            
            if st.button("Upload Document", type="primary"):
                with st.spinner("Uploading and processing document..."):
                    result = st.session_state.api_client.upload_document(
                        uploaded_file, title, access_level, department
                    )
                
                if "error" not in result:
                    st.success(f"Document uploaded successfully! Processing status: {result['status']}")
                    if result.get('processing_info'):
                        st.json(result['processing_info'])
                else:
                    st.error(f"Upload failed: {result['error']}")
    
    st.markdown("---")
    
    # Document list
    st.markdown("### Your Documents")
    
    documents = st.session_state.api_client.list_documents()
    
    if "error" not in documents:
        if documents:
            df = pd.DataFrame(documents)
            
            # Display as a nice table
            for _, doc in df.iterrows():
                with st.expander(f"📄 {doc['title']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Access Level:** {doc['access_level']}")
                        st.markdown(f"**Department:** {doc.get('department', 'General')}")
                    
                    with col2:
                        st.markdown(f"**File Type:** {doc['file_type']}")
                        st.markdown(f"**Indexed:** {'✅' if doc['is_indexed'] else '❌'}")
                    
                    with col3:
                        st.markdown(f"**Uploaded:** {doc['created_at'][:10]}")
                        st.markdown(f"**Size:** {doc.get('file_size', 'Unknown')} bytes")
        else:
            st.info("No documents found. Upload your first document above!")
    else:
        st.error(f"Error loading documents: {documents['error']}")


def system_status():
    """System status page (manager/admin only)"""
    st.markdown('<h1 class="main-header">⚙️ System Status</h1>', unsafe_allow_html=True)
    
    user_role = st.session_state.user_info.get('role', 'employee')
    
    if user_role not in ['manager', 'admin']:
        st.error("Access denied. This page is only available to managers and administrators.")
        return
    
    # Get system status
    status = st.session_state.api_client.get_system_status()
    
    if "error" not in status:
        # Overall status
        status_color = "🟢" if status["status"] == "healthy" else "🔴"
        st.markdown(f"## {status_color} System Status: {status['status'].title()}")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Documents",
                status["documents"]["total"],
                help="Total number of documents in the system"
            )
        
        with col2:
            st.metric(
                "Indexed Documents",
                status["documents"]["indexed"],
                help="Documents that have been processed and indexed"
            )
        
        with col3:
            st.metric(
                "Pending Indexing",
                status["documents"]["pending_indexing"],
                help="Documents waiting to be processed"
            )
        
        with col4:
            indexing_rate = (status["documents"]["indexed"] / max(status["documents"]["total"], 1)) * 100
            st.metric(
                "Indexing Rate",
                f"{indexing_rate:.1f}%",
                help="Percentage of documents successfully indexed"
            )
        
        # Detailed status
        st.markdown("### Component Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Secrets Management")
            secrets_status = status.get("secrets_status", {})
            for secret, is_valid in secrets_status.items():
                icon = "✅" if is_valid else "❌"
                st.markdown(f"{icon} {secret.replace('-', ' ').title()}")
        
        with col2:
            st.markdown("#### Vector Database")
            vector_status = status.get("vector_database", {})
            st.markdown(f"**Status:** {vector_status.get('status', 'Unknown')}")
            st.markdown(f"**Collection:** {vector_status.get('collection_name', 'Unknown')}")
        
        # Refresh button
        if st.button("Refresh Status"):
            st.rerun()
    
    else:
        st.error(f"Error loading system status: {status['error']}")


def analytics_dashboard():
    """Analytics dashboard (manager/admin only)"""
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    user_role = st.session_state.user_info.get('role', 'employee')
    
    if user_role not in ['manager', 'admin']:
        st.error("Access denied. This page is only available to managers and administrators.")
        return
    
    # Get analytics data
    analytics = st.session_state.api_client.get_analytics()
    
    if "error" not in analytics:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", analytics["total_users"])
        
        with col2:
            st.metric("Active Users", analytics["active_users"])
        
        with col3:
            st.metric("Total Documents", analytics["total_documents"])
        
        with col4:
            st.metric("Indexed Documents", analytics["indexed_documents"])
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Users by role
            st.markdown("### Users by Role")
            users_by_role = analytics["users_by_role"]
            
            if users_by_role:
                fig_users = px.pie(
                    values=list(users_by_role.values()),
                    names=list(users_by_role.keys()),
                    title="User Distribution by Role"
                )
                st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Documents by access level
            st.markdown("### Documents by Access Level")
            docs_by_access = analytics["documents_by_access_level"]
            
            if docs_by_access:
                fig_docs = px.bar(
                    x=list(docs_by_access.keys()),
                    y=list(docs_by_access.values()),
                    title="Documents by Access Level"
                )
                st.plotly_chart(fig_docs, use_container_width=True)
        
        # Documents by department
        st.markdown("### Documents by Department")
        docs_by_dept = analytics["documents_by_department"]
        
        if docs_by_dept:
            fig_dept = px.bar(
                x=list(docs_by_dept.keys()),
                y=list(docs_by_dept.values()),
                title="Documents by Department"
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        
        # Raw data
        with st.expander("Raw Analytics Data"):
            st.json(analytics)
    
    else:
        st.error(f"Error loading analytics: {analytics['error']}")


# Main app logic
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()