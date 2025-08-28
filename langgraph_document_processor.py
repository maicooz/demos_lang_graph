#!/usr/bin/env python3
"""
LangGraph Document Processing Workflow

This module implements a three-agent workflow:
1. Extractor Agent: Extracts entities from documents
2. Validator Agent: Validates extracted entities against required fields
3. Responder Agent: Provides final response with missing fields if any

Required entities: ["company", "budget", "deadline"]
"""

import os
import json
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
from enum import Enum

import dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables from .env file
dotenv.load_dotenv()

class AgentState(TypedDict):
    """State for the document processing workflow."""
    document: str
    extracted_entities: Dict[str, Any]
    validation_result: Dict[str, Any]
    missing_fields: List[str]
    attempts: int
    final_response: str
    error: Optional[str]


class ValidationStatus(Enum):
    """Validation status enumeration."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class DocumentProcessor:
    """Main document processing workflow."""
    
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        
        # Check environment variables
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if not all([deployment, endpoint, api_key]):
            raise ValueError("Missing required Azure OpenAI environment variables")
        
        self.llm = AzureChatOpenAI(
            azure_deployment=deployment,
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=endpoint,
            api_key=api_key
        )
        
        # Initialize the workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("extractor", self._extractor_agent)
        workflow.add_node("validator", self._validator_agent)
        workflow.add_node("responder", self._responder_agent)
        
        # Set entry point
        workflow.set_entry_point("extractor")
        
        # Add edges
        workflow.add_edge("extractor", "validator")
        workflow.add_edge("validator", "responder")
        workflow.add_edge("responder", END)
        
        # Compile the workflow without checkpointer for simple execution
        return workflow.compile()
    
    def _extractor_agent(self, state: AgentState) -> AgentState:
        """Extract entities from the document."""
        try:
            # Create extraction prompt
            extraction_prompt = ChatPromptTemplate.from_template("""
            You are an expert entity extractor. Extract the following entities from the given document:
            - company: The company name or organization
            - budget: The budget amount or financial information
            - deadline: The deadline or timeline information
            
            Document: {document}
            
            Please extract these entities and return them in JSON format. If an entity is not found, use null.
            Example format:
            {{
                "company": "Company Name",
                "budget": "$50,000",
                "deadline": "Q4 2024"
            }}
            
            Only return valid JSON, no additional text.
            """)
            
            # Get LLM response
            messages = extraction_prompt.format_messages(document=state["document"])
            response = self.llm.invoke(messages)
            
            # Parse the response
            try:
                extracted_data = json.loads(response.content)
                state["extracted_entities"] = extracted_data
                state["error"] = None
            except json.JSONDecodeError:
                state["extracted_entities"] = {}
                state["error"] = "Failed to parse extraction response"
                
        except Exception as e:
            state["extracted_entities"] = {}
            state["error"] = f"Extraction error: {str(e)}"
        
        return state
    
    def _validator_agent(self, state: AgentState) -> AgentState:
        """Validate extracted entities against required fields."""
        try:
            required = ["company", "budget", "deadline"]
            extracted = state.get("extracted_entities", {})
            
            # Check for missing fields
            missing_fields = []
            for field in required:
                if not extracted.get(field):
                    missing_fields.append(field)
            
            # Determine validation status
            if not missing_fields:
                status = ValidationStatus.SUCCESS
            elif len(missing_fields) < len(required):
                status = ValidationStatus.PARTIAL
            else:
                status = ValidationStatus.FAILED
            
            # Update state
            state["missing_fields"] = missing_fields
            state["validation_result"] = {
                "status": status.value,
                "missing_fields": missing_fields,
                "extracted_count": len(required) - len(missing_fields),
                "total_required": len(required)
            }
            state["error"] = None
            
        except Exception as e:
            state["validation_result"] = {
                "status": ValidationStatus.FAILED.value,
                "missing_fields": required,
                "extracted_count": 0,
                "total_required": len(required)
            }
            state["error"] = f"Validation error: {str(e)}"
        
        return state
    
    def _responder_agent(self, state: AgentState) -> AgentState:
        """Generate final response based on validation results."""
        try:
            validation = state.get("validation_result", {})
            missing_fields = state.get("missing_fields", [])
            extracted = state.get("extracted_entities", {})
            
            if validation.get("status") == ValidationStatus.SUCCESS.value:
                response = f"✅ All required entities extracted successfully!\n\nExtracted entities:\n"
                for field, value in extracted.items():
                    response += f"- {field}: {value}\n"
                    
            elif validation.get("status") == ValidationStatus.PARTIAL.value:
                response = f"⚠️  Partial extraction completed.\n\n"
                response += f"Extracted entities:\n"
                for field, value in extracted.items():
                    if value:
                        response += f"- {field}: {value}\n"
                
                response += f"\nMissing required fields: {', '.join(missing_fields)}"
                
            else:  # FAILED
                response = f"❌ Entity extraction failed.\n\n"
                response += f"Missing all required fields: {', '.join(missing_fields)}\n\n"
                response += "The document may not contain the required information or the extraction process encountered an error."
            
            # Add error information if any
            if state.get("error"):
                response += f"\n\nError: {state['error']}"
            
            state["final_response"] = response
            
        except Exception as e:
            state["final_response"] = f"Error generating response: {str(e)}"
            state["error"] = f"Response generation error: {str(e)}"
        
        return state
    
    def process_document(self, document: str) -> Dict[str, Any]:
        """Process a document through the workflow."""
        # Initialize state
        initial_state = AgentState(
            document=document,
            extracted_entities={},
            validation_result={},
            missing_fields=[],
            attempts=0,
            final_response="",
            error=None
        )
        
        # Run the workflow
        try:
            result = self.workflow.invoke(initial_state)
            return {
                "success": True,
                "extracted_entities": result.get("extracted_entities", {}),
                "validation_result": result.get("validation_result", {}),
                "missing_fields": result.get("missing_fields", []),
                "final_response": result.get("final_response", ""),
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Workflow execution error: {str(e)}",
                "extracted_entities": {},
                "validation_result": {},
                "missing_fields": ["company", "budget", "deadline"],
                "final_response": f"Workflow failed: {str(e)}"
            }


def main():
    """Example usage of the document processor."""
    # Check for required Azure OpenAI environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Please set the following environment variables: {', '.join(missing_vars)}")
        print("\nExample .env file:")
        print("AZURE_OPENAI_API_KEY=your_api_key_here")
        print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name")
        print("AZURE_OPENAI_API_VERSION=2024-02-15-preview")
        return
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Example documents
    documents = [
        # Document with all entities
        # """
        # Project Proposal: Website Redesign
        
        # Company: TechCorp Solutions Inc.
        # Budget: $75,000 USD
        # Deadline: March 15, 2025
        
        # We are seeking to redesign our corporate website to improve user experience
        # and increase conversion rates. The project will involve modernizing the design,
        # improving mobile responsiveness, and integrating new e-commerce features.
        # """,
        
        # # Document with partial entities
        # """
        # Marketing Campaign Request
        
        # Company: GreenEarth Marketing
        # Budget: $25,000
        
        # We need a comprehensive marketing campaign for our new eco-friendly product line.
        # The campaign should focus on social media, influencer partnerships, and content marketing.
        # Please provide a detailed proposal.
        # """,
        
        # # Document with no entities
        # """
        # General Inquiry
        
        # Hello, I'm interested in learning more about your services.
        # Could you please send me some information about your pricing
        # and what you can offer for small businesses?
        
        # Thank you for your time.
        # """,
        """
        Acme needs a campaign with a budget of 10000 and a deadline of 2025-09-01.
        """,
        """
        Acme needs a campaign with a budget of 10000.
        """,
        """
        A campaign with a budget of 10000 and a deadline of 2025-09-01.
        """,
        """
        A campaign is needed.
        """,
        """
        A campaign with a budget of 10000 and a deadline of 2025-09-01.
        """,
    ]
    
    # Process each document
    for i, doc in enumerate(documents, 1):
        print(f"\n{'='*60}")
        print(f"PROCESSING DOCUMENT {i}")
        print(f"{'='*60}")
        print(f"Document:\n{doc.strip()}")
        
        result = processor.process_document(doc)
        
        print(f"\n{'='*60}")
        print(f"RESULT {i}")
        print(f"{'='*60}")
        print(f"Success: {result['success']}")
        print(f"Missing Fields: {result['missing_fields']}")
        print(f"\nFinal Response:\n{result['final_response']}")
        
        if result.get('error'):
            print(f"\nError: {result['error']}")


if __name__ == "__main__":
    main()
