from datetime import date
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class Registry(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: str | None = Field()
    id_prefix: str | None = Field()
    index_data_url: str | None = Field()

    data_log: list["RegistryDataLogEntry"] = Relationship()
    

class RegistryDataLogEntry(SQLModel, table=True):
    __tablename__ = 'registry_data_log'
    id: int | None = Field(default=None, primary_key=True)
    level: str = Field(index=True)
    message: str = Field()
    url: str | None = Field()

    registry_id: str | None = Field(default=None, foreign_key="registry.id")
    registry: Registry | None = Relationship(back_populates="data_log")

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.message)
    def __eq__(self,other):
        return self.message == other.message
    
class SoftwareReadsFormatLink(SQLModel, table=True):
    __tablename__ = "formats_read_by_software"
    format_id: str | None = Field(default=None, foreign_key="format.id", primary_key=True)
    software_id: str | None = Field(default=None, foreign_key="software.id", primary_key=True)

class SoftwareWritesFormatLink(SQLModel, table=True):
    __tablename__ = "formats_written_by_software"
    format_id: str | None = Field(default=None, foreign_key="format.id", primary_key=True)
    software_id: str | None = Field(default=None, foreign_key="software.id", primary_key=True)

class Software(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    version: str | None = Field(index=True)
    summary: str | None = Field(index=True)
    license: str | None = Field(index=True)
    registry_url: str | None = Field(index=True)

    reads: list["Format"] = Relationship(back_populates="readers", link_model=SoftwareReadsFormatLink)
    writes: list["Format"] = Relationship(back_populates="writers", link_model=SoftwareWritesFormatLink)

    registry_id: str | None = Field(default=None, foreign_key="registry.id")
    registry: Registry | None = Relationship()

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.id)
    def __eq__(self,other):
        return self.id == other.id
    
class FormatGenresLink(SQLModel, table=True):
    __tablename__ = "format_genres"
    format_id: str | None = Field(default=None, foreign_key="format.id", primary_key=True)
    genre_id: str | None = Field(default=None, foreign_key="genre.id", primary_key=True)

class Genre(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    #
    formats: list["Format"] = Relationship(back_populates="genres", link_model=FormatGenresLink)

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.name)
    def __eq__(self,other):
        return self.name == other.name
    
class ExtensionFormatsLink(SQLModel, table=True):
    __tablename__ = "format_extensions"
    format_id: str | None = Field(default=None, foreign_key="format.id", primary_key=True)
    extension_id: str | None = Field(default=None, foreign_key="extension.id", primary_key=True)

class Extension(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    #
    formats: list["Format"] = Relationship(back_populates="extensions", link_model=ExtensionFormatsLink)

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.id)
    def __eq__(self,other):
        return self.id == other.id

class MediaTypesFormatsLink(SQLModel, table=True):
    __tablename__ = "format_media_types"
    format_id: str | None = Field(default=None, foreign_key="format.id", primary_key=True)
    media_type_id: str | None = Field(default=None, foreign_key="media_type.id", primary_key=True)

class MediaType(SQLModel, table=True):
    __tablename__ = "media_type"
    id: str | None = Field(default=None, primary_key=True)
    #
    formats: list["Format"] = Relationship(back_populates="media_types", link_model=MediaTypesFormatsLink)

    # Define how to spot unique entries in a set
    def __hash__(self):
        return hash(self.id)
    def __eq__(self,other):
        return self.id == other.id

class Format(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    name: str | None = Field(index=True)
    version: str | None = Field(index=True)
    summary: str | None = Field(index=True)
    genres: list["Genre"] = Relationship(back_populates="formats", link_model=FormatGenresLink)
    extensions: list["Extension"] = Relationship(back_populates="formats", link_model=ExtensionFormatsLink)
    media_types: list["MediaType"] = Relationship(back_populates="formats", link_model=MediaTypesFormatsLink)
    has_magic: bool = Field(default=False)
    primary_media_type: str | None = Field(index=True)
    parent_media_type: str | None = Field(index=True)
    registry_url: str | None = Field(index=True)
    registry_source_data_url: str | None = Field(index=True)
    registry_index_data_url: str | None = Field(index=True)
    created: date | None = Field(index=True)
    last_modified: date | None = Field(index=True)

    readers: list["Software"] = Relationship(back_populates="reads", link_model=SoftwareReadsFormatLink)
    writers: list["Software"] = Relationship(back_populates="writes", link_model=SoftwareWritesFormatLink)

    registry_id: str | None = Field(default=None, foreign_key="registry.id")
    registry: Registry | None = Relationship()

