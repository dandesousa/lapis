# Getting Started

## What's Going On?

Lapis works by using pelican to scan your files in the same way as the site-generator. Instead of generating it constructs a local database of your content so it can provide its indexing and creation features.

## Setup

First thing you want to do is create your lapis configuration file:

```
$ lapis newconfig
```

This creates a local .lapis.yml file in your home directory. You can add this to your dotfiles or edit it to suit your needs.

## Finding Content

You can find articles and pages using the `find` command:

```
$ lapis find article
```

Similarly find your pages like this:
```
lapis find page
```

You can filter by the metadata of the content like tags, categories, authors, etc.:

```
lapis find article -t tag1 -t tag2
# lapis find article -tag tag1 -tag tag2
```

filters are cumulative and restrict the content that appears in the article (so the above example only shows content that is tagged with both `tag1` and `tag2`).

### Edits

You can edit you content directory from a search by first seeing whats available:

```
lapis find article
```

then saying which you want to edit:

```
lapis find article -e 2
# lapis find article --edit 2

# opens the second item in your preferred editor
```

You can also inspect paths and delete content with `find`. For more information, see the [find command](find.md).

## Creating Content

You can create articles or posts with the `create` command.

```
lapis create article "My Post's Title Goes Here"

# creates the file on disk and opens it for edit in your preferred editor
```

You can also pre-populate the content withs tags and other metadata.

When you quit your editor lapis will save the results to the database (you need to save and quit to have lapis resume sync).

For more information, see the [create command](create.md).

## Listing Content Metadata

You can find the authors, tags and categories in your blog with the various listing commands:

### Tags
```
lapis tags
```

### Categories
```
lapis categories
```

### Authors
```
lapis authors
```

You can control the ordering and display of the lists of data. For more information, see [tags](tags.md), [authors](authors.md), [categories](categories.md).


