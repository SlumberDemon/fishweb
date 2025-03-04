# Arowana

If you need a database or a simple way to manage the filesystem within a `data` directory, Arowana is the perfect choice.
Fishweb makes it super simple to interact with Arowana. Arowana is a sister project of fishweb, [learn more](https://github.com/slumberdemon/arowana).

Arowana provides [`Base`](#base) which is a NoSQL wrapper of sqlite3 and [`Drive`](#drive) which is a simple filesystem wrapper.

## Installation

Install arowana into your app

::: code-group

```sh [uv]
uv add arowana
```

```sh [pip]
pip install arowana
```

:::

## Initialization

When using arowana in a fishweb app it will get the data directory from `FISHWEB_DATA_DIR` environment variable. However you can also specify the data directory yourself and use arowana standalone.

::: code-group

```py [fishweb.py]
# Fishweb example
from arowana import Base, Drive

drive = Drive("goldfish")
base = Base("clownfish")
```

```py [standalone.py]
# Standalone example
from arowana import Arowana

arowana = Arowana("data")

drive = arowana.Drive("goldfish")
base = arowana.Base("clownfish")
```

:::

## Base

### `put`

Put item into base. Overrides existing item if key already exists

Args:
  - data: The data to be stored
  - key: The key to store the data under. If None, a new key will be generated

Returns:
  - Item: Added item details

```py
# Key is automatically generated
base.put({"name": "sofa", "price": 20})

# Set key as "one"
base.put({"name": "sofa", "price": 20}, "one")

# The key can also be included in the object
base.put({"name": "sofa", "price": 20, "key": "test"})

# Supports multipe types
base.put("hello, worlds")
base.put(7)
base.put(True)

# "success" is the value and "smart_work" is the key.
base.put(data="sofa", key="name")
```

### `puts`

Put multiple items into base

Args:
  - items: Items to add

Returns:
  - Items: Added item details

```py
base.puts(
    [
        {"name": "sofa", "hometown": "Sofa islands", "key": "slumberdemon"},  # Key provided.
        ["nemo", "arowana", "fishweb", "clownfish"],  # Key auto-generated.
        "goldfish",  # Key auto-generated.
    ],
)
```


### `insert`

Insert item to base. Does not override existing item if key already exists

Args:
  - data: The data to be stored
  - key: The key to store the data under. If None, a new key will be generated

Returns:
  - Item: Added item details

```py
# Will succeed and auto generate a key
base.insert("hello, world")

# Will succeed with key "greeting1"
base.insert({"message": "hello, world"}, "greeting1")

# Will raise an error as key "greeting1" already exists
base.insert({"message": "hello, there"}, "greeting1")
```

### `get`

Get item from base.

Args:
  - key: key of the item to retrieve

Returns:
  - Item: Retrieved item details

```py
base.get("sofa")
```

### `delete`

Delete item from base.

Args:
  - key: key of the item to delete

```py
base.delete("sofa")
```

### `update`

Update item in base

Args:
  - data: Attributes to update
  - key: Key of the item to update

```py
base.update(
    {
        "name": "sofa",  # Set name to "sofa"
        "status.active": True,  # Set "status.active" to True
        "description": base.util.trim(),  # Remove description element
        "likes": base.util.append("fishing"),  # Append fishing to likes array
        "age": base.util.increment(1),  # Increment age by 1
    },
    "slumberdemon",
)
```

### `all`

Get all items in base

```py
base.all()
```

### `drop`

Delete base from database

```py
base.drop()
```

### `utils`

- `util.trim()` - Remove element from dict
- `util.increment(value)` - Increment element by value
- `util.append(value)` - Append element to list

## Drive

### `put`

Put file

Args:
  - name: Name and path of the file
  - data: Data content of file
  - path: Path of file to get content from

Returns:
  - str: Name of the file

```py
# Put content directly
drive.put("hello.txt", "Hello world")
drive.put(b"hello.txt", "Hello world")

import io

# Provide file content object
drive.put("arowana.txt", io.StringIO("hello world"))
drive.put("arowana.txt", io.BytesIO(b"hello world"))

with open("./arowana.txt", "r") as file:
    drive.put("arowana.txt", file)

# Provide a path to a file.
drive.put("arowana.txt", path="./arowana.txt")
```

### `get`

Get file content

Args:
  - name: Name and path of the file

Returns:
  - bytes: File bytes

```py
drive.get("arowana.txt")
```

### `list`

List all files

Args:
  - prefix: Prefix that file names start with

Returns:
  - list: List of file names

```py
drive.list()
```

### `delete`

Delete file

Args:
  - name: Name and path of the file

Returns:
  - str: Name of the deleted file

```py
drive.delete("arowana.txt")
```
