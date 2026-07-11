from enum import Enum

from fastapi import Query

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "COHERE"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"
    IBM = "ibm"
    OVH = "ovh"
    GLM="GLM"
    QWEN25 = "qwen25"
    QWEN25_XL = "qwen25_xl"
    QWEN25_XL_V1 = "qwen25_xl_v1"
    QWEN25_XL_V2 = "qwen25_xl_v2"
    QWEN25_XL_V3 = "qwen25_xl_v3"
    QWEN25_XL_V4 = "qwen25_xl_v4"
    QWEN25_XL_V5 = "qwen25_xl_v5"
    QWEN25_XL_V6 = "qwen25_xl_v6"
    QWEN25_XL_V7 = "qwen25_xl_v7"
    QWEN25_XL_V8 = "qwen25_xl_v8"
    QWEN25_XL_V9 = "qwen25_xl_v9"
    QWEN25_XL_V10 = "qwen25_xl_v10"

class OpenAiEnums(Enum):
    System = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_CALL_ID = "tool_call_id"
    TOOL_CALL_NAME = "tool_call_name"
    TOOL_CALL_ARGS = "tool_call_args"
    TOOL_CALL_RESULT = "tool_call_result"

class CohereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER="USER"
    ASSISTANT="CHATBOT"
    DOCUMENT="search_document"
    QUERY="search_query"

class DocumentTypeEnum(Enum):
    DOCUMENT="document"
    Query="query"    

