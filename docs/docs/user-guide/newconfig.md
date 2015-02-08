# Command: newconfig

## Purpose

Creates a .lapis.yml file in the users home directory

## When To Use It?

   * You setup lapis for the first time or need to reset you lapis configuration file

## Usage

```
lapis newconfig 
```

### Command Line Help
```
usage: lapis newconfig [-h] [-l LOCATION]

optional arguments:
  -h, --help            show this help message and exit
  -l LOCATION, --location LOCATION
                        the location to generate the lapis configuration file
                        (default: /Users/daniel/.lapis.yml)

```

## Examples

```
# new config in home directory
lapis newconfig

# new config in custom location
lapis newconfig -l /path/to/new/config.yml
```
