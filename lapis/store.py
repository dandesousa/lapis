#!/usr/bin/env python
# encoding: utf-8


"""defines the lapis store which is used to perform fast searches and lookups"""

import logging
from lapis.models import Base, Content, Site, Tag, Author, Category
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ClauseElement


logger = logging.getLogger(__name__)


class Store(object):
    """the store object contains structured data about the metadata of pelican
    content on a site. it is responsible for caching data and ensuring that it
    can be accessed quickly.
    """
    __version__ = "00.00.001dev"

    def __init__(self, path):
        self.__created = False
        conn_str = "sqlite:///" + path
        self.__engine = create_engine(conn_str)
        Base.metadata.create_all(self.__engine)
        Base.metadata.bind = self.__engine
        self.__session = sessionmaker(self.__engine)()

        if self.site is None:
            self.__created = True
            site = Site(version=Store.__version__)
            self.__session.add(site)
            self.__session.commit()

    def __del__(self):
        self.__session.close()

    @property
    def created(self):
        """returns true if the site db was just regenerated"""
        return self.__created

    @property
    def schema_changed(self):
        return self.site.version != Store.__version__

    @property
    def site(self):
        return self.__session.query(Site).first()

    @property
    def __updated(self):
        """determines if the contents of the directory were updated since last track

        :rtype bool: True if the content directory was updated since store was updated
        """
        pass

    def get_or_create(self, model, defaults=None, **kwargs):
        instance = self.__session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
            params.update(defaults or {})
            instance = model(**params)
            self.__session.add(instance)
            self.__session.commit()
            return instance, True

    def __get_content_type(self, content):
        """returns the enum representing the type of content parsed"""
        from pelican.contents import Article
        cls = type(content)
        if cls == Article:
            return "article"
        return "page"

    def __sync_content(self, content):
        """syncs content with the database by either updating an existing
        content or adding it to the database if it doesn't exist

        :param content object: content class that should be updated in the database
        """
        # TODO: This is wrong, we need to search by path
        updated = False
        db_content = self.__session.query(Content).filter(Content.source_path == content.source_path).first()
        if db_content is None:
            tag_list = getattr(content, "tags", [])
            tags = [self.get_or_create(Tag, name=tag.name)[0] for tag in tag_list]
            author = self.get_or_create(Author, name=content.author.name)[0]
            category = self.get_or_create(Category, name=content.category.name)[0]
            content_type = self.__get_content_type(content)
            status = content.status
            date_created = content.date
            content = Content(source_path=content.source_path, status=status, date_created=date_created, title=content.title, tags=tags, type=content_type, author=author, category=category)
            self.__session.add(content)
            self.__session.commit()  # TODO: This might be sub-optimal, we can maybe commit after all the adds?
            updated = True
        elif db_content.title != content.title:  # TODO: needs to update if any attribute or sub-attribute changes
            db_content.title = content.title
            self.__session.commit()
            updated = True

        return updated

    def sync(self, settings):
        """syncs the stores metadata with actual filesystem metadata.

        this will attempt to search all available content, syncing un-tracked
        files and updating tracked files that have changed.

        :param settings: Settings dictionary from the pelican config
        """
        from pelican.generators import PagesGenerator, ArticlesGenerator
        generator_classes = [PagesGenerator, ArticlesGenerator]

        context = settings.copy()
        context['filenames'] = {}
        context['localsiteurl'] = settings['SITEURL']
        generators = [
            cls(
                context=context,
                settings=settings,
                path=settings['PATH'],
                theme=settings['THEME'],
                output_path=settings['OUTPUT_PATH']
            ) for cls in generator_classes
        ]

        for g in generators:
            if hasattr(g, 'generate_context'):
                g.generate_context()

        content_keys = ("articles", "pages")
        updated = False

        for key in content_keys:
            for content in context[key]:
                updated = self.__sync_content(content) or updated

        if self.schema_changed:
            site = self.site
            site.version = Store.__version__
            self.__session.commit()

        return updated

    def list(self, pattern, order_by="name", cls=Tag):
        """fetches the list of objs which match the given pattern

        :param pattern str: regular expression which returns the objs which match the pattern.
        :param order_by str: choice of ['name', 'content']

        :yields cls: the obj that matches the pattern
        """
        import re

        pattern = re.compile(pattern)
        order_by_prop = cls.name
        objs = self.__session.query(cls)

        # TODO: might be a way to more efficiently query here, by foreign key
        # length??

        if order_by == "content":
            objs = sorted(objs, key=lambda x: -len(x.content))
        else:
            objs = objs.order_by(order_by_prop)

        for obj in objs:
            if pattern.search(obj.name):
                yield obj

    def search(self, **kwargs):
        """searches available metadata and files for the given search criteria

        this function searches the available metadata for a matching object and
        generates properly constructed content objects that match those criteria.

        :param author str: the author that the content must match.
        :param category str: the category that the content must match.
        :param content_type enum: either article, page or None to filter by content type.
        :param tags list: returns content that is the logical conjuction of these tags.
        :param title str: title to search content by, produces a filter by case-insensitive match.
        :param dates tuple: a tuple of containing either the date range or a single date. If a single
            date is provided, it must match that date. If two dates are provided, must full in between
            those dates. If None is provided, that bound is ignored.

        :yields object: The type of content object constrained by search parameters.
        """
        # TODO: Any way to determine if file system has changed so we can
        # resync?

        articles = self.__session.query(Content)

        # filters by the author of the content
        author = kwargs.get("author", None)
        if author:
            articles = articles.filter(Content.author.has(Author.name == author))

        # filters by the type of content
        content_type = kwargs.get("content_type", None)
        if content_type in ("article", "page"):
            articles = articles.filter(Content.type == content_type)

        # filters by the category
        category = kwargs.get("category", None)
        if category:
            articles = articles.filter(Content.category.has(Category.name == category))

        # filters by the articles matching all the tags
        tags = kwargs.get("tags", [])
        if tags:
            articles = articles.filter(*[Content.tags.any(Tag.name == tag) for tag in tags])

        # filters by the title, case-insensitive
        title = kwargs.get("title", None)
        if title:
            lc_title = title.lower()
            articles = articles.filter(Content.title.like("%{}%".format(lc_title)))

        # filters by the date created, depending on what was passed
        dates = kwargs.get("dates", None)
        if dates:
            from datetime import timedelta
            fmt = "%Y-%m-%d"
            if len(dates) == 1:
                begin = dates[0]
                end = begin + timedelta(days=1)
                articles = articles.filter(Content.date_created.between(begin.strftime(fmt), end.strftime(fmt)))
            elif len(dates) == 2:
                before, after = dates
                if after:
                    after += timedelta(days=1)
                    articles = articles.filter(Content.date_created >= after.strftime(fmt))
                if before:
                    articles = articles.filter(Content.date_created < before.strftime(fmt))

        for content in articles:
            yield content
