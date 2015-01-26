from sqlalchemy import Column, ForeignKey, Integer, String, Table, Enum, DateTime
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
    date_created = Column(DateTime())
    type = Column(Enum('page', 'article'), nullable=False)
    tags = relationship('Tag', secondary=content_tag_table, backref="content")
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', backref='content')
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category', backref='content')

    def __repr__(self):
        return "Content(title='{}', date_created='{}', type='{}', author='{}', category='{}', tags='{}')".format(self.title, self.date_created, self.type, self.author, self.category, self.tags)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String())

    def __repr__(self):
        return self.name


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String())

    def __repr__(self):
        return self.name


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String())

    def __repr__(self):
        return self.name
