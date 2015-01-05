from sqlalchemy import Column, ForeignKey, Integer, String, Table, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine

PATH_LEN = 500
Base = declarative_base()


class Site(Base):
    __tablename__ = 'site'
    id = Column(Integer, primary_key=True)
    content_path = Column(String(PATH_LEN), nullable=False)
    version = Column(Integer, nullable=False)


content_tag_table = Table('content_tag', Base.metadata,
                          Column('content_id', Integer, ForeignKey('content.id')),
                          Column('tag_id', Integer, ForeignKey('tag.id')))

class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True)
    source_path = Column(String(PATH_LEN), nullable=False, unique=True, index=True)
    title = Column(String(), index=True)
    type = Column(Enum('page', 'article'), nullable=False)
    tags = relationship('Tag', secondary=content_tag_table, backref="content_list")


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String())


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String())
