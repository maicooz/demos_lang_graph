# LangGraph Document Processing Workflows

A collection of document processing systems built with LangGraph that use specialized agents to extract, validate, and respond to document entities. The project includes both synchronous and asynchronous implementations with different approaches to workflow orchestration.

## Overview

This project implements document processing workflows using three specialized agents:

1. **Extractor Agent**: Analyzes documents and extracts required entities
2. **Validator Agent**: Validates extracted entities against required fields  
3. **Responder Agent**: Generates comprehensive responses with missing field information

## Required Entities

All workflows are configured to extract and validate these specific entities:
- `company`: Company name or organization
- `budget`: Budget amount or financial information  
- `deadline`: Deadline or timeline information

## Available Modules

### 1. **langgraph_document_processor.py** - Synchronous LLM-based Workflow
- **Type**: Full LangGraph implementation with OpenAI LLM integration
- **Features**: 
  - Uses OpenAI's language models for intelligent entity extraction
  - Comprehensive validation and error handling
  - Production-ready workflow orchestration
- **Use Case**: When you need high-quality entity extraction using AI models

### 2. **langgraph_simple_async.py** - Asynchronous LangGraph Workflow
- **Type**: Proper LangGraph async implementation with simple parsing
- **Features**:
  - Full LangGraph workflow with async execution
  - Regex-based entity extraction (no LLM dependency)
  - Proper workflow compilation and state management
- **Use Case**: When you need async processing without LLM costs

### 3. **langgraph_async_processor.py** - Async Simulation (Conceptual)
- **Type**: Async workflow simulation without LangGraph
- **Features**:
  - Demonstrates async agent concepts
  - Manual workflow orchestration
  - Regex-based entity extraction
- **Use Case**: Learning/understanding async workflow patterns

## Features

- **Multiple Implementation Approaches**: Choose between LLM-based and rule-based extraction
- **Async and Sync Support**: Both synchronous and asynchronous processing options
- **Comprehensive Validation**: Ensures all required fields are present and valid
- **Detailed Response Generation**: Provides clear feedback on extraction success/failure
- **Error Handling**: Robust error handling with informative error messages
- **Flexible Input**: Accepts various document formats and structures

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (for LLM-based workflows):
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env and add your Azure OpenAI configuration
   AZURE_OPENAI_API_KEY=your_actual_api_key_here
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
   ```

## Usage

### Option 1: LLM-based Processing (Synchronous)

```python
from langgraph_document_processor import DocumentProcessor

# Initialize the processor
processor = DocumentProcessor()

# Process a document
document = """
Project Proposal: Website Redesign
Company: TechCorp Solutions Inc.
Budget: $75,000 USD
Deadline: March 15, 2025
"""

result = processor.process_document(document)
print(result['final_response'])
```

### Option 2: Async Processing with LangGraph

```python
from langgraph_simple_async import LangGraphDocumentProcessor
import asyncio

async def process_document():
    processor = LangGraphDocumentProcessor()
    
    document = "Acme needs a campaign with a budget of 10000 and deadline of 2025-09-01."
    
    initial_state = {
        "document": document,
        "entities": {},
        "missing": ["company", "budget", "deadline"],
        "response": None,
        "attempts": 0
    }
    
    result = await processor.graph.ainvoke(initial_state)
    print(result['response'])

# Run the async workflow
asyncio.run(process_document())
```

### Option 3: Async Processing Simulation

```python
from langgraph_async_processor import AsyncDocumentProcessor
import asyncio

async def process_document():
    processor = AsyncDocumentProcessor()
    result = await processor.process_document("Acme needs a campaign with budget 10000")
    print(result['response'])

# Run the async simulation
asyncio.run(process_document())
```

## Running Examples

### Synchronous LLM Workflow
```bash
python langgraph_document_processor.py
```

### Async LangGraph Workflow
```bash
python langgraph_simple_async.py
```

### Async Simulation Workflow
```bash
python langgraph_async_processor.py
```

## Workflow Architecture

### LLM-based Workflow (langgraph_document_processor.py)
```
Document Input → Extractor Agent (LLM) → Validator Agent → Responder Agent → Final Response
```

### Async LangGraph Workflow (langgraph_simple_async.py)
```
Document Input → Extractor Agent (Regex) → Validator Agent → Responder Agent → Final Response
```

### Async Simulation (langgraph_async_processor.py)
```
Document Input → Manual Agent Orchestration → Final Response
```

## Agent Details

### Extractor Agent
- **LLM Version**: Uses structured prompts and OpenAI models for intelligent extraction
- **Regex Version**: Uses pattern matching for fast, rule-based extraction
- **Returns**: JSON-formatted entity results

### Validator Agent
- **Function**: Checks against required fields: `["company", "budget", "deadline"]`
- **Output**: Validation status (success/partial/failed) and missing fields list

### Responder Agent
- **Function**: Generates human-readable responses with actionable feedback
- **Includes**: Missing field information and extraction status

## Response Types

### Success Response
```
✅ All required entities extracted successfully!

Extracted entities:
- company: TechCorp Solutions Inc.
- budget: $75,000 USD
- deadline: March 15, 2025
```

### Partial Success Response
```
⚠️  Partial extraction completed.

Extracted entities:
- company: GreenEarth Marketing
- budget: $25,000

Missing required fields: deadline
```

### Failure Response
```
❌ Entity extraction failed.

Missing all required fields: company, budget, deadline

The document may not contain the required information or the extraction process encountered an error.
```

## Configuration

### Model Settings (LLM-based workflows)
- **Azure OpenAI Deployment**: Configured via environment variables
- **API Version**: `2024-02-15-preview` (configurable)
- **Temperature**: `0.1` (for consistent extraction)
- **Max Attempts**: `3` (configurable in constructor)

### Customization
You can modify the required entities by updating the `required_fields` list in the processor classes:

```python
self.required_fields = ["company", "budget", "deadline", "contact_person"]
```

## Error Handling

The systems handle various error scenarios:
- **API Errors**: Network issues, rate limits, authentication failures (LLM workflows)
- **Parsing Errors**: Invalid JSON responses from the LLM
- **Validation Errors**: Missing or malformed data
- **Workflow Errors**: State management issues

## Dependencies

- `langchain`: Core LangChain functionality
- `langchain-openai`: Azure OpenAI integration (for LLM workflows)
- `langgraph`: Workflow orchestration
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation

## API Requirements

**Note**: Only required for LLM-based workflows (`langgraph_document_processor.py`)

- **Azure OpenAI API Key**: Required for entity extraction
- **Azure OpenAI Endpoint**: Your Azure OpenAI resource endpoint
- **Deployment Name**: Your Azure OpenAI model deployment name
- **Model Access**: Access to your deployed Azure OpenAI models

## Example Documents

All workflows include test scenarios:
1. **Complete Document**: Contains all required entities
2. **Partial Document**: Missing one required entity
3. **Empty Document**: No required entities present

## Document Processing Results

Here are the actual results from running the `langgraph_document_processor.py` with different document types:

### Complete Document Example
**Input Document:**
```
Project Proposal: Website Redesign
        
        Company: TechCorp Solutions Inc.
        Budget: $75,000 USD
        Deadline: March 15, 2025
        
        We are seeking to redesign our corporate website to improve user experience
        and increase conversion rates. The project will involve modernizing the design,
        improving mobile responsiveness, and integrating new e-commerce features.
```

**Processing Result:**
```
✅ All required entities extracted successfully!

Extracted entities:
- company: TechCorp Solutions Inc.
- budget: $75,000 USD
- deadline: March 15, 2025
```

### Partial Document Example
**Input Document:**
```
Marketing Campaign Request
        
        Company: GreenEarth Marketing
        Budget: $25,000
        
        We need a comprehensive marketing campaign for our new eco-friendly product line.
        The campaign should focus on social media, influencer partnerships, and content marketing.
        Please provide a detailed proposal.
```

**Processing Result:**
```
⚠️  Partial extraction completed.

Extracted entities:
- company: GreenEarth Marketing
- budget: $25,000

Missing required fields: deadline
```

### Incomplete Document Example
**Input Document:**
```
General Inquiry
        
        Hello, I'm interested in learning more about your services.
        Could you please send me some information about your pricing
        and what you can offer for small businesses?
        
        Thank you for your time.
```

**Processing Result:**
```
❌ Entity extraction failed.

Missing all required fields: company, budget, deadline

The document may not contain the required information or the extraction process encountered an error.
```

## Choosing the Right Module

| Module | Use When | Pros | Cons |
|--------|----------|------|------|
| `langgraph_document_processor.py` | High-quality extraction needed | Best accuracy, intelligent parsing | Requires API key, slower, costs money |
| `langgraph_simple_async.py` | Async processing without LLM | Fast, no costs, proper LangGraph | Limited extraction patterns |
| `langgraph_async_processor.py` | Learning async concepts | Simple to understand | Not production-ready, manual orchestration |

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `AZURE_OPENAI_API_KEY` is set for LLM workflows
2. **Installation Errors**: Verify all dependencies are installed correctly
3. **API Rate Limits**: Check your Azure OpenAI account for usage limits
4. **Model Access**: Ensure your Azure OpenAI deployment is active and accessible

### Debug Mode

For debugging, you can add logging to see the workflow state at each step:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Feel free to extend this project with:
- Additional entity types and extraction patterns
- Custom validation rules
- Enhanced error handling
- Integration with other LLM providers
- Web interface or API endpoints
- Performance optimizations

## License

This project is open source and available under the MIT License.
