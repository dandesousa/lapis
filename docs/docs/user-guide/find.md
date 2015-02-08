# Command: find

## Purpose

Locate, list, edit and delete pelican content from a user site.

## When To Use It?

   * You want to find content matching a certain criteria
   * You want to edit a piece of content
   * You want to find the path to a piece of content
   * You want to delete a piece of content

## Usage

```
lapis find [article|page] [title] [options]
```

### Command Line Help
```
usage: lapis find [-h] [-s {published,hidden,draft}] [-t TAGS] [-c CATEGORY]
                  [-w AUTHOR] [-b BEFORE] [-a AFTER] [-d ON] [-e EDIT]
                  [-p PATH] [--delete DELETE]
                  {page,article} [title]

positional arguments:
  {page,article}        the content type that should be searched for
  title                 case-insensitive search by the title

optional arguments:
  -h, --help            show this help message and exit
  -s {published,hidden,draft}, --status {published,hidden,draft}
                        The status that the content must have.
  -t TAGS, --tags TAGS  List of tags which the content must contain.
  -c CATEGORY, --category CATEGORY
                        The category that the content must have
  -w AUTHOR, --author AUTHOR
                        The author that the content must have
  -b BEFORE, --before BEFORE
                        created before the the given date (format: YYYY-MM-DD)
  -a AFTER, --after AFTER
                        created after the the given date (format: YYYY-MM-DD)
  -d ON, --on ON        created on the the given date (format: YYYY-MM-DD)
  -e EDIT, --edit EDIT  Edits the Nth (1-len(content)) found content.
  -p PATH, --path PATH  Prints the source path of the Nth (1-len(content))
                        found content.
  --delete DELETE       Deletes the content located at the given source path.
```

## Examples

### Find All Articles
```
$ lapis find article

1.) | Article | Published | 2014-03-09 | Autumn Crane
2.) | Article | Published | 2014-09-06 | New England Shoreline
```

### Find All Photography Tagged Articles:

```
$ lapis find article -t photography

1.) | Article | Published | 2014-03-09 | Autumn Crane
2.) | Article | Published | 2014-09-06 | New England Shoreline
```

### Find, Edit, Locate and Delete A Page Created Before 2015
```
$ lapis find page --before 2015-01-01

1.) | Page | Published | 2014-03-14 | About
```

Get the path of this page:

```
$ lapis find page --before 2015-01-01 -p 1

/path/to/page
```

Edit this page:

```
$ lapis find page --before 2015-01-01 -e 1

/path/to/page
```

Delete this page:
```
$ lapis find page --before 2015-01-01 --delete 1

/path/to/page
```
