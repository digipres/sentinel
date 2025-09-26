import json
from typing import List, Optional, Set, Dict, Tuple, Type, Union, Literal, Annotated, Iterator
from pydantic import BaseModel
from datetime import datetime, date
from abc import ABC, abstractmethod

#
# A Software record
#
class Software(BaseModel):
    id: str
    name: str
    version: Optional[str] = None
    summary: Optional[str] = None
    license: Optional[str] = None
    registry_url: Optional[str] = None

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.id)
    def __eq__(self,other):
        return self.id == other.id
    
#
# Data model of normalised form of a format record:
#
class Format(BaseModel):
    id: str | None 
    name: str | None 
    version: str | None
    summary: str | None 
    genres: list[str] | None
    extensions: list[str] | None 
    media_types: list[str] 
    has_magic: bool
    primary_media_type: str | None = None
    parent_media_type: str | None = None
    registry_url: str | None = None
    registry_source_data_url: str | None = None
    registry_index_data_url: str | None = None
    created: date | None = None
    last_modified: date | None = None

    readers: Optional[list[Software]] = []
    writers: Optional[list[Software]] = []

    registry_id: str | None


#
# And for a Registry:
#
class RegistryDataLogEntry(BaseModel):
    level: str
    message: str
    url: Optional[str] = None

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.message)
    def __eq__(self,other):
        return self.message == other.message

class Registry(BaseModel):
    id: str
    name: str 
    url: str
    id_prefix: Optional[str] = None
    index_data_url: Optional[str] = None
    # Log for any issues
    data_log: list[RegistryDataLogEntry] = []
    # The set of extensions known to this registry:
    extensions: Set[str] = None


#
# An Abstract Base Class for the client code:
#
class RegistryClient(ABC):

    @property
    @abstractmethod
    def registry(self) -> Registry:
        pass

    @abstractmethod
    def get_formats(self) -> Iterator[Format]:
        ...

