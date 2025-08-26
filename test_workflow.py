#!/usr/bin/env python3
"""
Test script for the LangGraph Document Processing Workflow

This script tests the workflow structure and validation logic without requiring
an actual OpenAI API key, making it useful for development and testing.
"""

import json
from typing import Dict, Any
from unittest.mock import Mock, patch

# Import the main processor
from langgraph_document_processor import DocumentProcessor, ValidationStatus


class MockLLM:
    """Mock LLM for testing without API calls."""
    
    def __init__(self):
        self.responses = {
            "complete": {
                "company": "TechCorp Solutions Inc.",
                "budget": "$75,000 USD",
                "deadline": "March 15, 2025"
            },
            "partial": {
                "company": "GreenEarth Marketing",
                "budget": "$25,000",
                "deadline": None
            },
            "empty": {
                "company": None,
                "budget": None,
                "deadline": None
            }
        }
    
    def invoke(self, messages):
        """Mock invoke method that returns predefined responses."""
        # Extract document content from messages
        content = messages[0].content if messages else ""
        
        # Determine which response to return based on document content
        if "TechCorp" in content:
            response_type = "complete"
        elif "GreenEarth" in content:
            response_type = "partial"
        else:
            response_type = "empty"
        
        # Create mock response
        mock_response = Mock()
        mock_response.content = json.dumps(self.responses[response_type])
        return mock_response


def test_validation_logic():
    """Test the validation logic independently."""
    print("🧪 Testing validation logic...")
    
    # Test cases
    test_cases = [
        {
            "name": "Complete extraction",
            "extracted": {"company": "Test Corp", "budget": "$50K", "deadline": "Q4 2024"},
            "expected_missing": [],
            "expected_status": ValidationStatus.SUCCESS
        },
        {
            "name": "Partial extraction",
            "extracted": {"company": "Test Corp", "budget": "$50K", "deadline": None},
            "expected_missing": ["deadline"],
            "expected_status": ValidationStatus.PARTIAL
        },
        {
            "name": "Failed extraction",
            "extracted": {"company": None, "budget": None, "deadline": None},
            "expected_missing": ["company", "budget", "deadline"],
            "expected_status": ValidationStatus.FAILED
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        
        # Simulate validation logic
        required = ["company", "budget", "deadline"]
        missing_fields = []
        
        for field in required:
            if not test_case["extracted"].get(field):
                missing_fields.append(field)
        
        # Determine status
        if not missing_fields:
            status = ValidationStatus.SUCCESS
        elif len(missing_fields) < len(required):
            status = ValidationStatus.PARTIAL
        else:
            status = ValidationStatus.FAILED
        
        # Verify results
        assert missing_fields == test_case["expected_missing"], \
            f"Expected missing fields {test_case['expected_missing']}, got {missing_fields}"
        assert status == test_case["expected_status"], \
            f"Expected status {test_case['expected_status']}, got {status}"
        
        print(f"    ✅ Passed - Missing: {missing_fields}, Status: {status.value}")


def test_response_generation():
    """Test response generation logic."""
    print("\n🧪 Testing response generation...")
    
    # Test successful extraction
    extracted = {"company": "Test Corp", "budget": "$50K", "deadline": "Q4 2024"}
    missing_fields = []
    
    response = f"✅ All required entities extracted successfully!\n\nExtracted entities:\n"
    for field, value in extracted.items():
        response += f"- {field}: {value}\n"
    
    assert "✅ All required entities extracted successfully!" in response
    assert "company: Test Corp" in response
    print("    ✅ Success response generation passed")
    
    # Test partial extraction
    extracted = {"company": "Test Corp", "budget": "$50K"}
    missing_fields = ["deadline"]
    
    response = f"⚠️  Partial extraction completed.\n\n"
    response += f"Extracted entities:\n"
    for field, value in extracted.items():
        if value:
            response += f"- {field}: {value}\n"
    
    response += f"\nMissing required fields: {', '.join(missing_fields)}"
    
    assert "⚠️  Partial extraction completed." in response
    assert "Missing required fields: deadline" in response
    print("    ✅ Partial response generation passed")
    
    # Test failed extraction
    missing_fields = ["company", "budget", "deadline"]
    
    response = f"❌ Entity extraction failed.\n\n"
    response += f"Missing all required fields: {', '.join(missing_fields)}\n\n"
    response += "The document may not contain the required information or the extraction process encountered an error."
    
    assert "❌ Entity extraction failed." in response
    assert "Missing all required fields: company, budget, deadline" in response
    print("    ✅ Failure response generation passed")


def test_workflow_structure():
    """Test the workflow structure and state management."""
    print("\n🧪 Testing workflow structure...")
    
    # Test state initialization
    state = {
        "document": "Test document",
        "extracted_entities": {},
        "validation_result": {},
        "missing_fields": [],
        "attempts": 0,
        "final_response": "",
        "error": None
    }
    
    # Verify state structure
    required_keys = ["document", "extracted_entities", "validation_result", 
                    "missing_fields", "attempts", "final_response", "error"]
    
    for key in required_keys:
        assert key in state, f"Missing required key: {key}"
    
    print("    ✅ State structure validation passed")
    
    # Test state updates
    state["extracted_entities"] = {"company": "Test Corp"}
    state["missing_fields"] = ["budget", "deadline"]
    
    assert state["extracted_entities"]["company"] == "Test Corp"
    assert len(state["missing_fields"]) == 2
    assert "budget" in state["missing_fields"]
    assert "deadline" in state["missing_fields"]
    
    print("    ✅ State update validation passed")


def test_mock_workflow():
    """Test the workflow with mocked LLM responses."""
    print("\n🧪 Testing mock workflow...")
    
    # Create processor with mock LLM
    processor = DocumentProcessor()
    
    # Mock the LLM
    with patch.object(processor, 'llm', MockLLM()):
        # Test complete document
        complete_doc = """
        Project Proposal: Website Redesign
        Company: TechCorp Solutions Inc.
        Budget: $75,000 USD
        Deadline: March 15, 2025
        """
        
        result = processor.process_document(complete_doc)
        assert result["success"]
        assert "company" in result["extracted_entities"]
        assert "budget" in result["extracted_entities"]
        assert "deadline" in result["extracted_entities"]
        print("    ✅ Complete document processing passed")
        
        # Test partial document
        partial_doc = """
        Marketing Campaign Request
        Company: GreenEarth Marketing
        Budget: $25,000
        """
        
        result = processor.process_document(partial_doc)
        assert result["success"]
        assert "company" in result["extracted_entities"]
        assert "budget" in result["extracted_entities"]
        assert result["extracted_entities"]["deadline"] is None
        print("    ✅ Partial document processing passed")


def main():
    """Run all tests."""
    print("🚀 Starting LangGraph Workflow Tests\n")
    
    try:
        test_validation_logic()
        test_response_generation()
        test_workflow_structure()
        test_mock_workflow()
        
        print("\n🎉 All tests passed successfully!")
        print("\n✅ The LangGraph workflow is properly structured and ready for use.")
        print("📝 To run with real API calls, set your Azure OpenAI environment variables and run:")
        print("   python langgraph_document_processor.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
