# PDF URL Knowledge

Creates a knowledge base from PDF documents loaded from URLs with metadata for filtering.

## URL Structure

The `urls` field requires a specific structure for each document:

```json
{
    "url": "https://agno-public.s3.amazonaws.com/recipes/thai_recipes_short.pdf",
    "metadata": {
        "cuisine": "Thai",
        "source": "Thai Cookbook", 
        "region": "Southeast Asia"
    }
}
```

## Example Configuration

```yaml
PDF URL Knowledge:
  vector_db: "[connected from LanceDB]"
  urls:
    - url: "https://example.com/document1.pdf"
      metadata:
        type: "manual"
        category: "technical"
    - url: "https://example.com/document2.pdf"
      metadata:
        type: "report"
        year: "2024"
```