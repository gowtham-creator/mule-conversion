import streamlit as st
from langchain_openai import AzureChatOpenAI #type:ignore
from dotenv import load_dotenv #type:ignore
import time
from datetime import datetime

# Load environment variables and initialize LLM
load_dotenv()
llm = AzureChatOpenAI(
    model="gpt-4o",
    api_version="2024-05-01-preview",
    temperature=0,
)

# --- Core Functions ---
def mule_convert(mule_code):
    """Function which converts the given mule soft code into aws specific code and integrations."""
    mule_to_aws = f"""
You are a highly skilled AWS solutions architect with deep experience in refactoring and migrating enterprise integration flows from MuleSoft to AWS-native architectures. Your task is to analyze the following MuleSoft code snippet and generate a fully functional, scalable, and cloud-native equivalent using AWS services.

MuleSoft Code Snippet:
{mule_code}

Objectives:

Deconstruct the MuleSoft flow and explain its logical components and functionality.

Identify the appropriate AWS services and components to replicate the behavior using best practices.

Provide the complete AWS Infrastructure as Code (IaC)—preferably in AWS CDK (Python) or CloudFormation—to implement the solution.

Specify clearly where each part of the AWS code should be placed (e.g., Lambda handler, API Gateway integration, Step Function definition, etc.).

Provide instructions on how to deploy and run the solution using AWS CLI or relevant deployment tools.

Include detailed reasoning behind each service selection, ensuring that the proposed architecture is performant, secure, maintainable, and cost-efficient.

Output Format:

1. AWS Components List: A list of AWS services and their purpose in the architecture.

2. AWS Code (IaC): Fully working code snippets for the solution.

3. File & Placement Guidance: Clear file names and where each code snippet should be placed in the project structure.

4. Deployment Instructions: Step-by-step guide to run and deploy the solution on AWS.

5. Reasoning for Component Selection: Justification for choosing each AWS component over alternatives.

6. Conclusion: Summary of how the AWS solution mirrors or improves upon the original MuleSoft flow.

"""
    aws_blocks = llm.invoke(mule_to_aws).content
    return aws_blocks

def summary_generator(mule_code):
    """Function that proivides summary of the mule soft code provided"""
    summary_prompt = f"""
<PERSONA>
You are a senior integration architect and MuleSoft expert with deep experience in analyzing and documenting complex MuleSoft applications. You have worked extensively on enterprise-grade APIs, data integrations, and system orchestration using MuleSoft. Your role is to break down complex MuleSoft code into a thorough and readable summary that is understandable to both technical and semi-technical stakeholders.

<INPUT>
{mule_code}  
</INPUT>

<INSTRUCTION>
Create a comprehensive, detailed summary of the above MuleSoft code. Your analysis should go beyond a surface-level overview and dive into the design intent, configuration strategies, and inter-flow interactions. The summary should be structured and categorized, covering both functionality and architecture. Use technical accuracy while maintaining clarity.
Your output should includes these topics.

1. Overview
Brief summary of the application’s purpose and what problem it solves.
Whether it's part of a larger system, reusable API, or stand-alone integration.

2. Flows & Sub-Flows
List of all flows and sub-flows with their names and descriptions.
Trigger type (e.g., HTTP listener, scheduler, JMS) and expected inputs/outputs.
Summary of logic inside each flow (conditionals, routers, orchestration, etc.).

3. Connectors & External Systems
All connectors used (HTTP, DB, Salesforce, etc.) and what systems they interact with.
Type of communication (e.g., synchronous API call, async message queue).
Connection details or security strategy (OAuth, TLS, etc.).

4. API Layer & Exposure
REST API details: endpoints, HTTP methods, response structure.
RAML or OAS usage if applicable.
Policies applied (rate limiting, CORS, etc.).

5. Security Controls
Authentication/authorization used in API Manager or flows.
TLS configuration, encryption/decryption usage.
Access control via client ID enforcement, tokens, IP whitelisting.

6. Deployment & Runtime Notes
Environment types (CloudHub, Runtime Fabric, standalone, hybrid).
Worker size, VPCs, region deployment (if CloudHub).
Scaling strategy and failover setup.

7. Interactions & Dependencies
Communication between flows.
External dependency calls or chained flows.
Data/service dependencies (e.g., dependent on upstream API call).

8. Diagram 
*Provide an achitecture diagram if required.*

9. Summary/Conclusion
Recap of how the MuleSoft application works, its strengths, and any limitations or technical debt observed.
Optional recommendations for improvement, modernization, or migration.

"""
    
    summary = llm.invoke(summary_prompt).content
    return summary

# --- Cached versions for performance ---
@st.cache_data(show_spinner=False)
def cached_mule_convert(mule_code):
    return mule_convert(mule_code)

@st.cache_data(show_spinner=False)
def cached_summary(mule_code):
    return summary_generator(mule_code)

# --- File Handling ---
def extract_content(uploaded_file):
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        else:
            return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        try:
            return uploaded_file.read().decode("latin-1")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# --- Streamlit App ---
def main():
    st.set_page_config(
        page_title="MuleSoft Transformer",
        page_icon="🔀",
        layout="centered"
    )
    
    st.title("🔀 MuleSoft to AWS Transformer")
    st.markdown("""
    <style>
    .small-font {
        font-size:12px !important;
        color: #666;
    }
    .file-preview {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        max-height: 300px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="small-font">Supports .mule, .xml, and .txt files</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize session state
    if 'uploaded_content' not in st.session_state:
        st.session_state.uploaded_content = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results_history' not in st.session_state:
        st.session_state.results_history = []
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'show_preview' not in st.session_state:
        st.session_state.show_preview = False

    # File upload section
    uploaded_file = st.file_uploader(
        "Upload MuleSoft File", 
        type=["xml", "mule", "txt"],
        help="Supported formats: .xml, .mule, .txt"
    )
    
    if uploaded_file:
        if uploaded_file.name != st.session_state.current_file:
            # Clear history when new file is uploaded
            st.session_state.results_history = []
            st.session_state.current_file = uploaded_file.name
            
        content = extract_content(uploaded_file)
        if content:
            st.session_state.uploaded_content = content
            st.success("✅ File uploaded successfully!")
            
            # File preview section
            st.markdown("---")
            st.subheader("📄 File Preview")
            st.session_state.show_preview = st.checkbox(
                "Show file content", 
                value=True,
                key="preview_toggle"
            )
            
            if st.session_state.show_preview:
                st.markdown(f"**Filename:** `{uploaded_file.name}`")
                st.markdown("**File content:**")
                st.markdown(f'<div class="file-preview"><pre>{content}</pre></div>', 
                           unsafe_allow_html=True)

    # Always show controls if file is uploaded
    if st.session_state.uploaded_content:
        st.markdown("---")
        action = st.radio(
            "Select Transformation Type:",
            ["AWS Code Generation", "Code Summary"],
            horizontal=True,
            key="action_selector"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Process", type="primary", key="process_btn"):
                st.session_state.processing = True
        
        if st.session_state.processing:
            with st.spinner("🧠 Analyzing code. This may take a moment..."):
                start_time = time.time()
                
                try:
                    if "AWS" in action:
                        result = cached_mule_convert(st.session_state.uploaded_content)
                    else:
                        result = cached_summary(st.session_state.uploaded_content)
                    
                    processing_time = time.time() - start_time
                    
                    # Store result in history
                    st.session_state.results_history.insert(0, {
                        "type": action,
                        "content": result,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "processing_time": f"{processing_time:.2f} seconds"
                    })
                
                except Exception as e:
                    st.error(f"⚠️ Processing error: {str(e)}")
                
                st.session_state.processing = False

    # Display history
    if st.session_state.results_history:
        st.markdown("---")
        st.subheader("📚 Processing History")
        
        for idx, result in enumerate(st.session_state.results_history):
            with st.expander(f"{result['type']} - {result['timestamp']}", expanded=idx==0):
                st.markdown(result['content'], unsafe_allow_html=True)    
                st.download_button(
                    label=f"Download {result['type']}",
                    data=result['content'],
                    file_name=f"{result['type'].replace(' ', '_')}_{idx+1}.md",
                    mime="text/markdown",
                    key=f"download_{idx}"
                )
                st.caption(f"⏱️ Processed in {result['processing_time']}")

    # New file upload prompt
    if not uploaded_file and st.session_state.results_history:
        st.markdown("---")
        st.info("ℹ️ Upload a new file to start fresh analysis")

if __name__ == "__main__":
    main()
