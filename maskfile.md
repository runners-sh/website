# Solrunners website project tasks

## init
> Initialize the python venv and install required packages
~~~sh
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
~~~

## build
> Build the website
~~~sh
python -m blog
~~~

## test
> Run tests
~~~sh
python -m pytest
~~~

## format
> Format using ruff
~~~sh
python -m ruff format
~~~

## lint
> Lint using ruff
```

## make-reqs
> Update the requirements.txt file
~~~sh
pip freeze > requirements.txt
~~~
