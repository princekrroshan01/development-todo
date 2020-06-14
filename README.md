# development-todo
development-todo is a program used to search through directories on the local machine and extract @TODO tags from a code base to create a task list and help developers stay on track.

## Example
./file.py
``` python
#!usr/bin/env python3
@TODO Fix output Formatting

import sys
...
```

todo ./
```
File        Line#   Comment
./file.py     2     Fix output Formatting
```

## Using
```python
python3 todo.py --help
Usage: todo.py [OPTIONS]

Options:
  --info TEXT           Tool to search through files on the local
                        machine and identify @TODO tags to create a task list
                        for developers.
                        Usage:
                            todo  --path=/dir
                            todo
                        --path=/root/project-one/
  --path TEXT           Target path
  --maxthreads INTEGER  Define maximmum no. of threads to be used(Default: 6)
  --help                Show this message and exit.

```

## Todo
- [x] Add support to untack the hidden files like .git,.idea etc.
- [x] Use click instead of argparse.
- [ ] Add label to the Todo and use different color code for diffrent labels.
- [x] Replace all print statement with click echo.
