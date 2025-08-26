#!/usr/bin/env python3
"""
Async LangGraph Document Processing Workflow

This module implements an async three-agent workflow compatible with the user's examples:
1. Extractor Agent: Extracts entities from documents (using simple parsing)
2. Validator Agent: Validates extracted entities against required fields (no LLM needed)
3. Responder Agent: Provides final response with missing fields if any

Required entities: ["company", "budget", "deadline"]
"""

import re
import asyncio
from typing import Dict, List, Any, Optional, TypedDict


class AgentState(TypedDict):
    """State for the async document processing workflow."""
    document: str
    entities: Dict[str, Any]
    missing: List[str]
    response: Optional[str]
    attempts: int


class ValidationStatus:
    """Validation status constants."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class AsyncDocumentProcessor:
    """Async document processing workflow without LLM dependency."""
    
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.required_fields = ["company", "budget", "deadline"]
        
        # Initialize the workflow
        self.graph = self._build_workflow()
    
    def _build_workflow(self):
        """Build the async workflow (simplified without LangGraph for demo)."""
        # For this demo, we'll simulate the workflow without LangGraph
        # In a real implementation, you'd use StateGraph here
        pass
    
    async def _extractor_agent(self, state: AgentState) -> AgentState:
        """Extract entities from the document using simple parsing."""
        try:
            document = state["document"].lower()
            entities = {}
            
            # Extract company (look for company names, "needs", "wants", etc.)
            company_patterns = [
                r'(\w+)\s+(?:needs|wants|requires|is requesting)',
                r'company[:\s]+(\w+)',
                r'client[:\s]+(\w+)'
            ]
            
            for pattern in company_patterns:
                match = re.search(pattern, document)
                if match:
                    entities["company"] = match.group(1).title()
                    break
            
            # Extract budget (look for numbers with currency or budget keywords)
            budget_patterns = [
                r'budget[:\s]+(\d+)',
                r'(\d+)\s*(?:dollars?|usd|\$)',
                r'budget\s+of\s+(\d+)'
            ]
            
            for pattern in budget_patterns:
                match = re.search(pattern, document)
                if match:
                    entities["budget"] = f"${match.group(1)}"
                    break
            
            # Extract deadline (look for dates and deadline keywords)
            deadline_patterns = [
                r'deadline[:\s]+(\d{4}-\d{2}-\d{2})',
                r'(\d{4}-\d{2}-\d{2})',
                r'deadline\s+of\s+(\d{4}-\d{2}-\d{2})'
            ]
            
            for pattern in deadline_patterns:
                match = re.search(pattern, document)
                if match:
                    entities["deadline"] = match.group(1)
                    break
            
            state["entities"] = entities
            
        except Exception as e:
            state["entities"] = {}
        
        return state
    
    async def _validator_agent(self, state: AgentState) -> AgentState:
        """Validate extracted entities against required fields (no LLM needed)."""
        try:
            extracted = state.get("entities", {})
            
            # Check for missing fields
            missing_fields = []
            for field in self.required_fields:
                value = extracted.get(field)
                if not value or (isinstance(value, str) and not value.strip()):
                    missing_fields.append(field)
            
            # Update state
            state["missing"] = missing_fields
            
        except Exception as e:
            state["missing"] = self.required_fields.copy()
        
        return state
    
    async def _responder_agent(self, state: AgentState) -> AgentState:
        """Generate final response based on validation results."""
        try:
            missing_fields = state.get("missing", [])
            extracted = state.get("entities", {})
            
            if not missing_fields:
                response = f"✅ All required entities extracted successfully!\n\nExtracted entities:\n"
                for field, value in extracted.items():
                    response += f"- {field}: {value}\n"
                    
            elif len(missing_fields) < len(self.required_fields):
                response = f"⚠️  Partial extraction completed.\n\n"
                response += f"Extracted entities:\n"
                for field, value in extracted.items():
                    if value:
                        response += f"- {field}: {value}\n"
                
                response += f"\nMissing required fields: {', '.join(missing_fields)}"
                
            else:  # All missing
                response = f"❌ Entity extraction failed.\n\n"
                response += f"Missing all required fields: {', '.join(missing_fields)}\n\n"
                response += "The document may not contain the required information or the extraction process encountered an error."
            
            state["response"] = response
            
        except Exception as e:
            state["response"] = f"Error generating response: {str(e)}"
        
        return state
    
    async def process_document(self, document: str) -> Dict[str, Any]:
        """Process a document through the async workflow."""
        # Initialize state
        initial_state = AgentState(
            document=document,
            entities={},
            missing=self.required_fields.copy(),
            response=None,
            attempts=0
        )
        
        # Run the workflow (simulated without LangGraph)
        try:
            # Extract
            state = await self._extractor_agent(initial_state)
            
            # Validate
            state = await self._validator_agent(state)
            
            # Respond
            state = await self._responder_agent(state)
            
            return state
        except Exception as e:
            return {
                "document": document,
                "entities": {},
                "missing": self.required_fields.copy(),
                "response": f"Workflow failed: {str(e)}",
                "attempts": 0
            }


async def main():
    """Example usage with the provided scenarios."""
    # Initialize processor
    processor = AsyncDocumentProcessor()
    
    # Test scenarios from the user's examples
    scenarios = [
        # Scenario 1: All entities present
        "Acme needs a campaign with a budget of 10000 and a deadline of 2025-09-01.",
        # Scenario 2: Missing deadline
        "Acme needs a campaign with a budget of 10000.",
        # Scenario 3: Missing budget
        "Acme needs a campaign with a deadline of 2025-09-01.",
        # Scenario 4: Missing company
        "A campaign with a budget of 10000 and a deadline of 2025-09-01.",
        # Scenario 5: All missing
        "A campaign is needed.",
    ]
    
    print("🚀 Testing Async Document Processing Workflow with User Scenarios\n")
    
    for i, input_doc in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}")
        print(f"{'='*60}")
        print(f"Input: {input_doc}")
        
        # Process document
        result = await processor.process_document(input_doc)
        
        print(f"\nExtracted Entities: {result['entities']}")
        print(f"Missing Fields: {result['missing']}")
        print(f"\nResponse:\n{result['response']}")


if __name__ == "__main__":
    asyncio.run(main())
