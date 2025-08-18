# PDF URL Knowledge Base

AI-powered document knowledge base that loads PDF documents from URLs with advanced metadata support for intelligent filtering and retrieval.

## **Overview**

The PDF URL Knowledge Base node creates searchable knowledge repositories from online PDF documents. Built on Agno's knowledge management system, it provides intelligent document chunking, metadata-based filtering, and seamless integration with vector databases for high-performance semantic search.

### **Available Nodes**

| Node | Description | Best For |
|------|-------------|----------|
| **PDF URL Knowledge Base** | Service node that creates knowledge bases from PDF URLs | RAG applications, document Q&A, content analysis |
| **Knowledge Base Load** | Execution node for indexing documents into knowledge bases | Data ingestion workflows, batch processing |

---

## **Key Features**

### **🌐 URL-Based Document Loading**
- Direct PDF loading from web URLs
- Automatic document download and processing
- Support for password-protected and authenticated URLs
- Robust error handling for network issues

### **🏷️ Advanced Metadata System**
- Flexible JSON-based metadata for each document
- Custom filtering during retrieval
- Support for complex document categorization
- Hierarchical tagging and organization

### **🧠 Intelligent Document Processing**
- Multiple chunking strategies (basic, by_title, sentence)
- Optimization profiles (accuracy, latency, cost)
- Format-aware processing
- Configurable document limits

### **🔍 Vector Database Integration**
- Compatible with LanceDB, Qdrant, and other vector stores
- Semantic search capabilities
- Efficient embedding storage and retrieval
- Scalable for large document collections

### **⚡ Performance Optimization**
- Lazy loading and caching
- Configurable processing parameters
- Memory-efficient document handling
- Asynchronous processing support

---

## **Quick Start**

### **Basic PDF Knowledge Base**
```yaml
# Set up vector database
LanceDB Vector Database:
  uri: "/tmp/lancedb"
  table_name: "documents"

# Create knowledge base with PDFs
PDF URL Knowledge Base:
  vector_db: "[connected from LanceDB]"
  urls:
    - key: "https://example.com/manual.pdf"
      value: '{"type": "manual", "category": "technical"}'
    - key: "https://example.com/report.pdf"  
      value: '{"type": "report", "year": "2024"}'
```

### **Advanced Configuration**
```yaml
PDF URL Knowledge Base:
  vector_db: "[connected vector database]"
  urls: "[see metadata structure below]"
  num_documents: 100
  optimize_on: "accuracy"
  chunking_strategy: "by_title"
  formats: ["pdf"]
```

### **Using with Agents**
```yaml
# Create knowledge base
PDF URL Knowledge Base:
  # ... configuration ...

# Configure agent knowledge settings  
Agent Knowledge Settings:
  knowledge: "[connected from PDF URL Knowledge Base]"
  add_references: true
  
# Create agent with knowledge
Agno Agent:
  knowledge: "[connected from Agent Knowledge Settings]"
```

---

## **Metadata Structure**

### **📝 Input Format**

The `urls` field accepts a list of key-value pairs where:
- **Key (URL)**: The direct URL to the PDF document
- **Value (Metadata)**: JSON string containing document metadata

### **Metadata Schema**

```json
{
  "type": "document_type",
  "category": "main_category", 
  "subcategory": "sub_category",
  "source": "document_source",
  "author": "document_author",
  "year": "2024",
  "language": "en",
  "region": "north_america",
  "tags": ["tag1", "tag2", "tag3"],
  "priority": "high",
  "custom_field": "custom_value"
}
```

### **Common Metadata Fields**

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `type` | string | Document type/format | `"manual"`, `"report"`, `"whitepaper"`, `"specification"` |
| `category` | string | Primary classification | `"technical"`, `"financial"`, `"legal"`, `"marketing"` |
| `subcategory` | string | Secondary classification | `"api_docs"`, `"user_guide"`, `"quarterly_report"` |
| `source` | string | Document origin | `"company_website"`, `"research_portal"`, `"government"` |
| `author` | string | Document creator | `"John Doe"`, `"Engineering Team"`, `"Legal Department"` |
| `year` | string/number | Publication year | `"2024"`, `2024` |
| `language` | string | Document language | `"en"`, `"es"`, `"fr"`, `"de"` |
| `region` | string | Geographic relevance | `"north_america"`, `"europe"`, `"asia_pacific"` |
| `tags` | array | Keyword tags | `["api", "rest", "authentication"]` |
| `priority` | string | Importance level | `"high"`, `"medium"`, `"low"` |

### **Example Configurations**

#### **Technical Documentation**
```yaml
urls:
  - key: "https://api.example.com/docs/auth.pdf"
    value: |
      {
        "type": "api_documentation",
        "category": "technical", 
        "subcategory": "authentication",
        "source": "official_docs",
        "tags": ["api", "oauth", "security"],
        "priority": "high",
        "language": "en"
      }
```

#### **Research Papers**
```yaml
urls:
  - key: "https://arxiv.org/pdf/2024.01234.pdf"
    value: |
      {
        "type": "research_paper",
        "category": "academic",
        "author": "Smith et al.",
        "year": "2024",
        "tags": ["machine_learning", "nlp", "transformers"],
        "source": "arxiv"
      }
```

#### **Company Reports**
```yaml
urls:
  - key: "https://company.com/reports/q4-2024.pdf"
    value: |
      {
        "type": "financial_report", 
        "category": "financial",
        "subcategory": "quarterly",
        "year": "2024",
        "quarter": "Q4",
        "region": "global",
        "priority": "high"
      }
```

#### **Multi-Language Content**
```yaml
urls:
  - key: "https://example.com/manual-en.pdf"
    value: '{"type": "manual", "language": "en", "region": "north_america"}'
  - key: "https://example.com/manual-es.pdf" 
    value: '{"type": "manual", "language": "es", "region": "latin_america"}'
  - key: "https://example.com/manual-fr.pdf"
    value: '{"type": "manual", "language": "fr", "region": "europe"}'
```

---

## **Configuration Options**

### **Vector Database Connection**
- **Required**: Must connect to a vector database service node
- **Supported**: LanceDB, Qdrant, or any VectorDb-compatible service
- **Purpose**: Stores document embeddings for semantic search

### **Document Processing**

#### **Optimization Profiles**
- **`accuracy`** (default): Best quality results, slower processing
- **`latency`**: Faster processing, good quality
- **`cost`**: Most efficient processing, basic quality

#### **Chunking Strategies**
- **`basic`** (default): Simple text splitting by size
- **`by_title`**: Smart splitting using document structure
- **`sentence`**: Sentence-boundary aware chunking

#### **Document Limits**
- **`num_documents`**: Maximum number of documents to process
- **`formats`**: Supported file formats (default: `["pdf"]`)

---

## **Architecture Overview**

```
PDF URL Knowledge Base Flow:

[PDF URLs] ──┐
              │
[Metadata] ───┼──> [PDF URL Knowledge Base] ──┐
              │                                │
[Vector DB] ──┘                                ├──> [Agent Knowledge Settings] ──> [Agno Agent]
                                               │
[Config] ──────────────────────────────────────┘

Document Processing Pipeline:
├── URL Validation & Download
├── PDF Parsing & Text Extraction  
├── Metadata Integration
├── Document Chunking (configurable strategy)
├── Embedding Generation (via Vector DB)
└── Knowledge Base Creation
```

### **Key Components**

1. **Service Layer**: Provides AgentKnowledge instances for agents
2. **URL Processing**: Downloads and validates PDF documents  
3. **Metadata Integration**: Combines document content with structured metadata
4. **Vector Storage**: Leverages connected vector database for embeddings
5. **Knowledge Interface**: Agno-compatible knowledge base for RAG applications

---

## **Usage Patterns**

### **Document Q&A System**
```yaml
# Knowledge base with technical docs
PDF URL Knowledge Base:
  urls:
    - key: "https://docs.api.com/reference.pdf"
      value: '{"type": "api_reference", "category": "technical"}'
    
# Agent for technical support
Agno Agent:
  knowledge: "[connected knowledge base]"
  model: "gpt-4"
  instructions: "Answer technical questions using the API documentation."
```

### **Multi-Source Research Assistant**
```yaml
# Knowledge base with diverse sources
PDF URL Knowledge Base:
  urls:
    - key: "https://research.org/paper1.pdf"
      value: '{"type": "research", "field": "ai", "year": "2024"}'
    - key: "https://gov.org/report.pdf"  
      value: '{"type": "government_report", "field": "policy"}'
    - key: "https://company.com/whitepaper.pdf"
      value: '{"type": "whitepaper", "field": "industry"}'

# Agent with research capabilities
Agno Agent:
  knowledge: "[connected knowledge base]"
  instructions: "Provide comprehensive research insights from multiple sources."
```

### **Filtered Knowledge Retrieval**
```yaml
# Agent settings with filtering
Agent Knowledge Settings:
  knowledge: "[connected knowledge base]"
  knowledge_filters: {"type": "manual", "language": "en"}
  enable_agentic_knowledge_filters: true
  
# Agent will only use English manuals
Agno Agent:
  knowledge: "[connected knowledge settings]"
```

---

## **Best Practices**

### **🏷️ Metadata Design**
- **Consistent Schema**: Use standardized field names across documents
- **Hierarchical Categories**: Implement category/subcategory structure
- **Rich Tagging**: Include relevant keywords for better filtering
- **Version Control**: Track document versions and update dates

### **📚 Document Organization**
- **Logical Grouping**: Group related documents with similar metadata
- **Language Separation**: Use language codes for multilingual content
- **Source Attribution**: Always include source information
- **Priority Levels**: Mark important documents for preferential retrieval

### **⚡ Performance Optimization**
- **Batch Processing**: Group similar documents for efficient processing
- **Strategic Chunking**: Choose chunking strategy based on document structure
- **Reasonable Limits**: Set appropriate `num_documents` limits
- **Vector DB Tuning**: Optimize vector database settings for your use case

### **🔍 Search Quality**
- **Descriptive Metadata**: Provide rich context for better retrieval
- **Balanced Chunks**: Avoid overly large or small document chunks
- **Quality URLs**: Ensure PDF URLs are reliable and accessible
- **Content Validation**: Verify document quality before indexing

---

## **Integration Examples**

### **Customer Support Knowledge Base**
```yaml
# Support documentation knowledge base
PDF URL Knowledge Base:
  urls:
    - key: "https://support.company.com/troubleshooting.pdf"
      value: '{"type": "troubleshooting", "category": "support", "priority": "high"}'
    - key: "https://support.company.com/faq.pdf"
      value: '{"type": "faq", "category": "support", "priority": "medium"}'

# Support agent with knowledge filtering
Agent Knowledge Settings:
  knowledge: "[connected knowledge base]"
  knowledge_filters: {"category": "support"}
  add_references: true

# Customer support agent
Agno Agent:
  knowledge: "[connected knowledge settings]"
  instructions: "Provide helpful customer support using company documentation."
```

### **Legal Document Analysis**
```yaml
# Legal document knowledge base
PDF URL Knowledge Base:
  urls:
    - key: "https://legal.company.com/terms.pdf"
      value: '{"type": "terms_of_service", "category": "legal", "jurisdiction": "US"}'
    - key: "https://legal.company.com/privacy.pdf"
      value: '{"type": "privacy_policy", "category": "legal", "jurisdiction": "EU"}'

# Legal analysis agent
Agno Agent:
  knowledge: "[connected knowledge base]"
  instructions: "Analyze legal documents and provide compliance insights."
```

### **Research and Development**
```yaml
# R&D knowledge base
PDF URL Knowledge Base:
  urls:
    - key: "https://research.company.com/innovation-2024.pdf"
      value: '{"type": "research_report", "department": "rd", "year": "2024"}'
    - key: "https://patents.company.com/patent-123.pdf"
      value: '{"type": "patent", "status": "approved", "technology": "ai"}'

# R&D assistant agent
Agno Agent:
  knowledge: "[connected knowledge base]"
  instructions: "Assist with research and development insights from company patents and reports."
```

---

## **Troubleshooting**

### **Common Issues**

#### **URL Access Problems**
- Verify PDF URLs are publicly accessible
- Check for authentication requirements
- Ensure URLs return actual PDF content
- Test URLs in browser before configuration

#### **Metadata Parsing Errors**
- Validate JSON syntax in metadata values
- Use consistent field naming conventions  
- Avoid special characters in field values
- Test metadata structure with small examples

#### **Vector Database Connection**
- Ensure vector database node is properly configured
- Verify connection between nodes in workflow
- Check vector database compatibility
- Monitor vector database resource usage

#### **Processing Performance**
- Adjust `num_documents` limit for large collections
- Choose appropriate `optimize_on` setting
- Consider document size and complexity
- Monitor memory usage during processing

### **Debug Steps**
1. **Test Individual URLs**: Verify each PDF URL loads correctly
2. **Validate Metadata**: Check JSON syntax and structure
3. **Check Connections**: Ensure proper node connections
4. **Monitor Logs**: Review processing logs for errors
5. **Start Small**: Begin with few documents, scale gradually

---

## **Advanced Features**

### **Custom Knowledge Filtering**
Enable agents to dynamically filter knowledge based on context:

```yaml
Agent Knowledge Settings:
  knowledge: "[connected knowledge base]"
  enable_agentic_knowledge_filters: true
  knowledge_filters: {"default_filter": "value"}
```

### **Reference Integration**
Include source references in agent responses:

```yaml
Agent Knowledge Settings:
  knowledge: "[connected knowledge base]"
  add_references: true
  references_format: "json"  # or "yaml"
```

### **Custom Retrieval Functions**
Implement specialized retrieval logic:

```yaml
Agent Knowledge Settings:
  knowledge: "[connected knowledge base]"
  retriever: "[custom retrieval function]"
```

---

## **Migration and Scaling**

### **From File-Based Systems**
1. **URL Migration**: Convert file paths to accessible URLs
2. **Metadata Extraction**: Extract existing metadata to JSON format
3. **Batch Processing**: Process documents in manageable batches
4. **Validation**: Verify document accessibility and quality

### **Scaling Considerations**
- **Vector Database Selection**: Choose appropriate vector DB for scale
- **Processing Resources**: Ensure adequate CPU/memory for document processing
- **Network Bandwidth**: Consider bandwidth for large document collections
- **Storage Requirements**: Plan for vector storage space needs

---

📚 **The PDF URL Knowledge Base provides enterprise-grade document intelligence for AI agents with flexible metadata support and seamless vector database integration.**