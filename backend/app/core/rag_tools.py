from openai.types.responses import ToolParam

from app.schemas.agent import GetParentChunkInput, SearchDocumentsInput

RAG_TOOLS: list[ToolParam] = [
    {
        "type": "function",
        "name": "search_documents",
        "description": "Search documents for relevant child passages. Returns source labels and parent IDs. Increase limit or change query when evidence is missing.",
        "parameters": SearchDocumentsInput.model_json_schema(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_parent_chunk",
        "description": "Read the full parent passage for a parent_id returned by search_documents. Reuses its source label.",
        "parameters": GetParentChunkInput.model_json_schema(),
        "strict": True,
    },
]
