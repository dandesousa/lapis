# .lapis.yml File

## Overview

Lapis uses pelican settings whenever possible, but some options are specific to lapis and they are contained in a file called .lapis.yml in your home directory.

## Example

```
---
# terminal color options
termcolors:
    # enables terminal colors (default: no)
    enabled: yes

# selects the editor (default: vim)
editor: vim

# selects default markup language (default: markdown)
markup: markdown

# preferred articles stub
article_path: posts/{year}/{month}
```

## Options

The follow is a complete list of options for the lapis configuration file:

### **termcolors > enabled** 

    (yes|no) 
    Whether the terminal should display colors for lapis commands.

### **editor**

    supported: (vim, *any*)
    Name of the editor that you want to use with lapis.

### **markup**

    supported: (markdown, restructuredtext)
    default: markdown
    Name of the format you preferred to use.

### **article_path**

    supported format specifiers: (year, month, day)
    Preferred path to the articles that lapis creates under the content directory.

#### Example

```
article_path: posts/{year}/{month}/{day}
```
