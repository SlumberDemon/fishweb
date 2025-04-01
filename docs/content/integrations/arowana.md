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

```py [fishweb]
# Fishweb example
from arowana import Base, Drive

drive = Drive("goldfish")
base = Base("clownfish")
```

```py [standalone]
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
  - dict: Added item details

```py
# Key is automatically generated
# Returns: {"name": "sofa", "price": 20, "key": "generated_key"}
base.put({"name": "sofa", "price": 20})

# Set key as "one"
# Returns: {"name": "sofa", "price": 20, "key": "one"}
base.put({"name": "sofa", "price": 20}, "one")

# The key can also be included in the object
# Returns: {"name": "sofa", "price": 20, "key": "test"}
base.put({"name": "sofa", "price": 20, "key": "test"})

# Supports multiple types
# Returns: {"key": "generated_key", "value": "hello, worlds"}
base.put("hello, worlds")

# Returns: {"key": "generated_key", "value": 7}
base.put(7)

# Returns: {"key": "generated_key", "value": true}
base.put(True)

# Returns: {"key": "name", "value": "sofa"}
base.put(data="sofa", key="name")
```

### `puts`

Put multiple items into base

Args:
  - items: Items to add

Returns:
  - dict: Added items details

```py
# Returns: {"items": [
#   {"name": "sofa", "hometown": "Sofa islands", "key": "slumberdemon"},
#   {"key": "generated_key", "value": ["nemo", "arowana", "fishweb", "clownfish"]},
#   {"key": "generated_key", "value": "goldfish"}
# ]}
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
  - dict: Added item details

```py
# Will succeed and auto generate a key
# Returns: {"key": "generated_key", "value": "hello, world"}
base.insert("hello, world")

# Will succeed with key "greeting1"
# Returns: {"message": "hello, world", "key": "greeting1"}
base.insert({"message": "hello, world"}, "greeting1")

# Will raise an error as key "greeting1" already exists
base.insert({"message": "hello, there"}, "greeting1")
```

### `get`

Get item from base.

Args:
  - key: key of the item to retrieve

Returns:
  - dict: Retrieved item details

```py
# If the stored item is a dictionary, returns the dict with a "key" field:
# {"name": "sofa", "price": 20, "key": "one"}
base.get("one")

# If the stored item is a non-dict value, returns:
# {"key": "my_key", "value": "stored_value"}
base.get("my_key")
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

Returns:
  - dict: All items

```py
# Returns: {"items": [
#   {"name": "sofa", "price": 20, "key": "one"},
#   {"key": "my_string", "value": "hello world"},
#   ...
# ]}
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
