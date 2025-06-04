# Solrunners website project tasks

## init

> Initialize the python venv and install required packages

```sh
if ! type python > /dev/null; then
    echo "Python is not installed."
    exit 1
fi

if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d ./.venv ]; then
        echo "Creating Python venv..."
        python -m venv .venv
    fi
    echo "Entering venv..."
    source ./.venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt
```

## build (module)

> Build the website

Build files will appear in the `./dist` folder.

```sh
python -m "$module"
```

## test

> Run tests

```sh
python3 -m pytest
```

## format

> Run the ruff formatter

```sh
ruff format
```

## check

> Run the ruff checker

```sh
ruff check
```

## make-reqs

> Update the requirements.txt file

```sh
pip freeze > requirements.txt
```

## serve (module)

> Serve the specified website locally

```sh
python3 -m "$module" serve
```

## barcode
> Generate a random EAN-8 barcode

```sh
python3 -m runners_common barcode
```
