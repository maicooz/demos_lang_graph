#!/usr/bin/env python3
"""
Quick Start Demo for LangGraph Document Processing Workflow

This script demonstrates the workflow using mock data, so you can see
how it works without setting up external dependencies.
"""

from test_basic import MockDocumentProcessor, ValidationStatus

def demo_workflow():
    """Demonstrate the complete workflow."""
    print("🚀 LangGraph Document Processing Workflow Demo\n")
    
    # Initialize processor
    processor = MockDocumentProcessor()
    
    # Sample documents
    documents = [
        {
            "name": "Complete Project Proposal",
            "content": """
            Project: Website Redesign
            Company: TechCorp Solutions Inc.
            Budget: $75,000 USD
            Deadline: March 15, 2025
            
            We are seeking to redesign our corporate website to improve user experience
            and increase conversion rates.
            """,
            "expected_status": ValidationStatus.SUCCESS
        },
        {
            "name": "Partial Marketing Request",
            "content": """
            Marketing Campaign Request
            
            Company: GreenEarth Marketing
            Budget: $25,000
            
            We need a comprehensive marketing campaign for our new eco-friendly product line.
            The campaign should focus on social media and influencer partnerships.
            """,
            "expected_status": ValidationStatus.PARTIAL
        },
        {
            "name": "General Inquiry",
            "content": """
            Hello, I'm interested in learning more about your services.
            Could you please send me some information about your pricing
            and what you can offer for small businesses?
            
            Thank you for your time.
            """,
            "expected_status": ValidationStatus.FAILED
        }
    ]
    
    print("📋 Processing Documents Through the Workflow\n")
    print("=" * 70)
    
    for i, doc in enumerate(documents, 1):
        print(f"\n📄 DOCUMENT {i}: {doc['name']}")
        print("-" * 50)
        print(f"Content:\n{doc['content'].strip()}")
        
        # Simulate extraction (in real workflow, this would be done by LLM)
        if "TechCorp" in doc["content"]:
            extracted = {
                "company": "TechCorp Solutions Inc.",
                "budget": "$75,000 USD", 
                "deadline": "March 15, 2025"
            }
        elif "GreenEarth" in doc["content"]:
            extracted = {
                "company": "GreenEarth Marketing",
                "budget": "$25,000",
                "deadline": None
            }
        else:
            extracted = {
                "company": None,
                "budget": None,
                "deadline": None
            }
        
        print(f"\n🔍 EXTRACTION RESULT:")
        for field, value in extracted.items():
            status = "✅" if value else "❌"
            print(f"  {status} {field}: {value}")
        
        # Validate
        validation = processor.validate_entities(extracted)
        print(f"\n✅ VALIDATION RESULT:")
        print(f"  Status: {validation['status'].upper()}")
        print(f"  Extracted: {validation['extracted_count']}/{validation['total_required']}")
        print(f"  Missing: {', '.join(validation['missing_fields']) if validation['missing_fields'] else 'None'}")
        
        # Generate response
        response = processor.generate_response(validation, extracted)
        print(f"\n💬 FINAL RESPONSE:")
        print(response)
        
        print("\n" + "=" * 70)
    
    print("\n🎯 WORKFLOW SUMMARY")
    print("=" * 30)
    print("This demo shows how the three-agent workflow processes documents:")
    print("1. 🔍 Extractor Agent: Identifies and extracts entities")
    print("2. ✅ Validator Agent: Checks against required fields")
    print("3. 💬 Responder Agent: Generates human-readable output")
    print("\nRequired entities: company, budget, deadline")
    print("\nTo run with real AI processing:")
    print("1. Install dependencies: python3 setup.py")
    print("2. Set Azure OpenAI environment variables:")
    print("   export AZURE_OPENAI_API_KEY=your_key")
    print("   export AZURE_OPENAI_ENDPOINT=your_endpoint")
    print("   export AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment")
    print("3. Run: python3 langgraph_document_processor.py")


if __name__ == "__main__":
    demo_workflow()
