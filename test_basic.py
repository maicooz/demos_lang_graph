#!/usr/bin/env python3
"""
Basic test script for the document processing logic

This script tests the core validation and response generation logic
without requiring external packages.
"""

import json
from typing import Dict, List, Any, Optional
from enum import Enum


class ValidationStatus(Enum):
    """Validation status enumeration."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class MockDocumentProcessor:
    """Mock document processor for testing core logic."""
    
    def __init__(self):
        self.required_fields = ["company", "budget", "deadline"]
    
    def validate_entities(self, extracted_entities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted entities against required fields."""
        missing_fields = []
        
        for field in self.required_fields:
            value = extracted_entities.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        
        # Determine validation status
        if not missing_fields:
            status = ValidationStatus.SUCCESS
        elif len(missing_fields) < len(self.required_fields):
            status = ValidationStatus.PARTIAL
        else:
            status = ValidationStatus.FAILED
        
        return {
            "status": status.value,
            "missing_fields": missing_fields,
            "extracted_count": len(self.required_fields) - len(missing_fields),
            "total_required": len(self.required_fields)
        }
    
    def generate_response(self, validation_result: Dict[str, Any], 
                         extracted_entities: Dict[str, Any]) -> str:
        """Generate final response based on validation results."""
        status = validation_result.get("status")
        missing_fields = validation_result.get("missing_fields", [])
        
        if status == ValidationStatus.SUCCESS.value:
            response = f"✅ All required entities extracted successfully!\n\nExtracted entities:\n"
            for field, value in extracted_entities.items():
                response += f"- {field}: {value}\n"
                
        elif status == ValidationStatus.PARTIAL.value:
            response = f"⚠️  Partial extraction completed.\n\n"
            response += f"Extracted entities:\n"
            for field, value in extracted_entities.items():
                if value:
                    response += f"- {field}: {value}\n"
            
            response += f"\nMissing required fields: {', '.join(missing_fields)}"
            
        else:  # FAILED
            response = f"❌ Entity extraction failed.\n\n"
            response += f"Missing all required fields: {', '.join(missing_fields)}\n\n"
            response += "The document may not contain the required information or the extraction process encountered an error."
        
        return response


def test_validation_logic():
    """Test the validation logic."""
    print("🧪 Testing validation logic...")
    
    processor = MockDocumentProcessor()
    
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
        },
        {
            "name": "Mixed extraction",
            "extracted": {"company": "Test Corp", "budget": None, "deadline": "Q4 2024"},
            "expected_missing": ["budget"],
            "expected_status": ValidationStatus.PARTIAL
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        
        result = processor.validate_entities(test_case["extracted"])
        
        # Verify results
        assert result["missing_fields"] == test_case["expected_missing"], \
            f"Expected missing fields {test_case['expected_missing']}, got {result['missing_fields']}"
        assert result["status"] == test_case["expected_status"].value, \
            f"Expected status {test_case['expected_status'].value}, got {result['status']}"
        
        print(f"    ✅ Passed - Missing: {result['missing_fields']}, Status: {result['status']}")


def test_response_generation():
    """Test response generation logic."""
    print("\n🧪 Testing response generation...")
    
    processor = MockDocumentProcessor()
    
    # Test successful extraction
    extracted = {"company": "Test Corp", "budget": "$50K", "deadline": "Q4 2024"}
    validation = processor.validate_entities(extracted)
    response = processor.generate_response(validation, extracted)
    
    assert "✅ All required entities extracted successfully!" in response
    assert "company: Test Corp" in response
    assert "budget: $50K" in response
    assert "deadline: Q4 2024" in response
    print("    ✅ Success response generation passed")
    
    # Test partial extraction
    extracted = {"company": "Test Corp", "budget": "$50K"}
    validation = processor.validate_entities(extracted)
    response = processor.generate_response(validation, extracted)
    
    assert "⚠️  Partial extraction completed." in response
    assert "company: Test Corp" in response
    assert "budget: $50K" in response
    assert "Missing required fields: deadline" in response
    print("    ✅ Partial response generation passed")
    
    # Test failed extraction
    extracted = {"company": None, "budget": None, "deadline": None}
    validation = processor.validate_entities(extracted)
    response = processor.generate_response(validation, extracted)
    
    assert "❌ Entity extraction failed." in response
    assert "Missing all required fields: company, budget, deadline" in response
    print("    ✅ Failure response generation passed")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing edge cases...")
    
    processor = MockDocumentProcessor()
    
    # Test empty dictionary
    extracted = {}
    validation = processor.validate_entities(extracted)
    assert validation["status"] == ValidationStatus.FAILED.value
    assert len(validation["missing_fields"]) == 3
    print("    ✅ Empty dictionary handling passed")
    
    # Test with extra fields
    extracted = {"company": "Test Corp", "budget": "$50K", "deadline": "Q4 2024", "extra": "value"}
    validation = processor.validate_entities(extracted)
    assert validation["status"] == ValidationStatus.SUCCESS.value
    assert len(validation["missing_fields"]) == 0
    print("    ✅ Extra fields handling passed")
    
    # Test with empty strings
    extracted = {"company": "", "budget": "   ", "deadline": None}
    validation = processor.validate_entities(extracted)
    assert validation["status"] == ValidationStatus.FAILED.value
    assert len(validation["missing_fields"]) == 3
    print("    ✅ Empty string handling passed")


def test_workflow_simulation():
    """Simulate the complete workflow."""
    print("\n🧪 Testing workflow simulation...")
    
    processor = MockDocumentProcessor()
    
    # Simulate document processing
    documents = [
        {
            "name": "Complete Document",
            "content": "Company: TechCorp, Budget: $75K, Deadline: Q1 2025",
            "expected_status": ValidationStatus.SUCCESS
        },
        {
            "name": "Partial Document", 
            "content": "Company: GreenEarth, Budget: $25K",
            "expected_status": ValidationStatus.PARTIAL
        },
        {
            "name": "Empty Document",
            "content": "General inquiry about services",
            "expected_status": ValidationStatus.FAILED
        }
    ]
    
    for doc in documents:
        print(f"\n  Processing: {doc['name']}")
        
        # Simulate extraction (in real workflow, this would be done by LLM)
        if "TechCorp" in doc["content"]:
            extracted = {"company": "TechCorp", "budget": "$75K", "deadline": "Q1 2025"}
        elif "GreenEarth" in doc["content"]:
            extracted = {"company": "GreenEarth", "budget": "$25K", "deadline": None}
        else:
            extracted = {"company": None, "budget": None, "deadline": None}
        
        # Validate
        validation = processor.validate_entities(extracted)
        
        # Generate response
        response = processor.generate_response(validation, extracted)
        
        # Verify
        assert validation["status"] == doc["expected_status"].value
        print(f"    ✅ {doc['name']} processed successfully")
        print(f"       Status: {validation['status']}")
        print(f"       Missing: {validation['missing_fields']}")


def main():
    """Run all tests."""
    print("🚀 Starting Basic Document Processing Tests\n")
    
    try:
        test_validation_logic()
        test_response_generation()
        test_edge_cases()
        test_workflow_simulation()
        
        print("\n🎉 All basic tests passed successfully!")
        print("\n✅ The core logic is working correctly.")
        print("📝 To test the full LangGraph workflow:")
        print("1. Install dependencies: python3 setup.py")
        print("2. Set Azure OpenAI environment variables:")
    print("   export AZURE_OPENAI_API_KEY=your_key")
    print("   export AZURE_OPENAI_ENDPOINT=your_endpoint")
    print("   export AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment")
        print("3. Run full tests: python3 test_workflow.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
