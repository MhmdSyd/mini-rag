from enum import Enum 

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = 'file_validate_successfully'
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FILE_SIZE_EXCEEDED = 'file_size_exceeded'
    FILE_UPLOAD_SUCCESS = 'file_upload_success'
    FILE_UPLOAD_FAILED = 'file_upload_failed'
    FILE_PROCESS_FAILED = 'file_process_failed'
    FILE_PROCESS_SUCCESS = 'file_process_success'
    FILE_ID_ERROR = 'file_not_found'
    NO_FILES_ERROR = 'no_files_in_project'
    PROJECT_NOT_FOUND = 'project_not_exist'
    ASSET_DELETED_SUCCESS = 'asset_deleted_success'
    Project_DELETED_SUCCESS = 'project_deleted_success'
    ASSET_NAME_ERROR = 'asset_name_is_not_valid'
    ASSET_NOT_FOUND = 'asset_name_not_found'
    INSERT_INTO_VECTORDB_ERROR = 'vector_insert_failed'
    INSERT_INTO_VECTORDB_SUCCESS = 'vector_insert_success'
