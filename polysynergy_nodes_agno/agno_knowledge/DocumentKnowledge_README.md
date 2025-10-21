# 📚 Document Knowledge

Load documents into a vector knowledge base with support for URLs, file paths, and bytes content.

---

## Overview

The Document Knowledge node processes documents and stores them in a vector database for retrieval by AI agents. It supports multiple input formats and automatically handles downloading, chunking, and embedding.

## Supported Input Formats

The node accepts a flexible list of items in the `URLs, Paths, or Bytes` input. Each item can be in one of these formats:

### 1. URLs (HTTP/HTTPS)

Download and process documents from web URLs:

```json
{
  "url": "https://example.com/document.pdf",
  "metadata": {
    "source": "web",
    "category": "manual"
  }
}
```

### 2. S3 Keys

Download documents from S3 buckets:

```json
{
  "url": "s3://my-bucket/documents/report.pdf",
  "metadata": {
    "department": "sales"
  }
}
```

### 3. Local File Paths

Process existing files from `/tmp/` or other locations:

```json
{
  "url": "/tmp/document.pdf",
  "metadata": {
    "uploaded_by": "user123"
  }
}
```

### 4. Bytes Content (Recommended)

Process in-memory document bytes (e.g., from HTTP Request nodes):

```json
{
  "bytes": <PDF_BYTES>,
  "metadata": {
    "filename": "report.pdf",
    "source": "http_request"
  }
}
```

**Alternative format (backwards compatible):**

```json
{
  "url": <PDF_BYTES>,
  "metadata": {
    "filename": "report.pdf"
  }
}
```

## Configuration

### Vector Database

Connect a Vector Database node (e.g., Qdrant) to store the document embeddings.

**Required**: Yes

### Chunking Strategy

Connect a Chunking Strategy node to control how documents are split into chunks.

**Required**: No (defaults to FixedSizeChunking with 1000 chars, 100 overlap)

Available strategies:
- Fixed Size Chunking
- Semantic Chunking
- Sentence Chunking
- Token Chunking

### Allowed Extensions

Specify which file extensions to accept.

**Default**: `[".pdf", ".docx", ".doc", ".rtf", ".txt", ".pptx", ".xlsx", ".csv"]`

## Metadata

Metadata is optional but recommended for better document organization and retrieval.

### Common Metadata Fields

- `filename`: Custom name for the document (**REQUIRED for bytes content**)
- `source`: Where the document came from
- `category`: Document category or type
- `uploaded_by`: User who uploaded the document
- `department`: Department or team
- Any custom fields you need

**Important**: For bytes content, you **must** provide `filename` in metadata. The node cannot determine the file type from raw bytes alone.

## Example Workflows

### Load PDF from HTTP Request

```
HTTP Request (download PDF)
  ↓ body (bytes)
Variable Dict (wrap bytes with metadata)
  ↓
Document Knowledge
  ↓
Agent (can now search the document)
```

### Load Multiple Documents

```json
[
  {
    "url": "https://docs.example.com/manual.pdf",
    "metadata": {"type": "manual", "version": "1.0"}
  },
  {
    "bytes": <PDF_BYTES_FROM_HTTP>,
    "metadata": {"filename": "report.pdf", "type": "report"}
  },
  {
    "url": "/tmp/local-doc.pdf",
    "metadata": {"type": "internal"}
  }
]
```

## Outputs

### Success Path

Returns a message like:
- `"Successfully processed 3 documents"`
- `"Processed 3 documents (1 failed)"`

### Failure Path

Returns error message if processing fails completely:
- `"Failed to process all 5 documents"`
- `"No valid documents found after processing URLs and tmp paths"`

## Tips

1. **Bytes from HTTP**: Use the HTTP Request node's body output directly as bytes content
2. **Filename required for bytes**: Always include `filename` in metadata when using bytes content
3. **Mixed inputs**: You can combine URLs, paths, and bytes in the same list
4. **Metadata for retrieval**: Add rich metadata to improve agent search accuracy
5. **Chunking matters**: Choose the right chunking strategy for your document type

---

## Related Nodes

- **Vector Database**: Qdrant, Pinecone, etc.
- **Chunking Strategies**: Fixed Size, Semantic, Token-based
- **HTTP Request**: Download documents from URLs
- **Agent Settings Knowledge**: Configure agent knowledge retrieval

---

**👉 [Agno Official Documentation](https://docs.agno.com/introduction)**
