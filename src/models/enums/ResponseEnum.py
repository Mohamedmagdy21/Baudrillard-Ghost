from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS="file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED="file_type_not_supported"
    FILE_SIZE_EXCEEDED="file_size_exceeded"
    FILE_UPLOADED_SUCCESS="file_upload_success"
    FILE_UPLOADED_FAILED="file_uploaded_failed"
    PROCESSING_SUCCESS="processing_success"
    PROCESSING_FAILED="processing_failed"
    NO_FILES_ERROR="not found files"
    FILE_ID_ERROR="no_file_found_with_this_id"
    PROJECT_NOT_FOUND_ERROR="project_not found"
    INSERT_INTO_VECTORDB_ERROR="error inserting chunks into vector database"
    INSERT_INTO_VECTORDB_SUCCESS="insert_into_vectordb_success"
    VECTOR_COLLECTION_RETRIEVED= "vectordb_collection_retrieved"
    VECTOR_DB_SEARCH_ERROR="vectordb_search_error"
    VECTOR_DB_SEARCH_SUCCESS="vectordb_search_success"
