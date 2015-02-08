# Command: sync

## Purpose

Syncs the on-disk pelican content with the database for faster indexing. Also purges data that was in the database that no longer exists.

## When To Use It?
    
   * Lapis tells you to run sync because a problem occurred.
   * You create or edit a piece of content without using a lapis command.
   * Data displayed by lapis is incorrect.

When lapis tells you that you should run sync, you should do so. Additionally, this is probably a result of doing something in a less-than-optimal way. Ideally, the user should never have to run sync and lapis should be smart enough to intelligently sync as needed.

## Examples

```
lapis sync
```
