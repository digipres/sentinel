from typing import List, Optional, Set, Dict
from pydantic import BaseModel, AnyHttpUrl, PastDate

# Pydantic data model for information about software and the formats the software may read or write:
class Software(BaseModel):
    registry_id: str
    id: str
    name: str
    version: Optional[str] = None
    summary: Optional[str] = None
    registry_url: AnyHttpUrl
    # 
    license: Optional[str] = None
    #
    writes: List[str] = []
    reads: List[str] = []

# Pydantic data model for partially normalised/star-schema format registry entries:
class Format(BaseModel):
    registry_id: str
    id: str
    name: str
    version: Optional[str]
    summary: Optional[str] = None
    registry_url: AnyHttpUrl
    registry_source_data_url: AnyHttpUrl
    registry_index_data_url: Optional[AnyHttpUrl]
    created: Optional[PastDate] = None
    last_modified: Optional[PastDate] = None
    # A spot of any additional fields:
    additional_fields: Optional[Dict[str,List[str]]] = None
    # Fields relating to format:
    genres: List[str] = []
    extensions: List[str] = []
    iana_media_types: List[str] = []
    has_magic: bool
    primary_media_type: Optional[str]
    parent_media_type: Optional[str]
    # Nested fields relating to software:
    readers: List[Software] = []
    writers: List[Software] = []

