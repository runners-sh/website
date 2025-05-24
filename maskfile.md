# Solrunners website project tasks

## init
> Initialize the python venv and install required packages
~~~sh
if ! type python; then
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
pytest
~~~

## make-reqs
> Make requirements.txt file
~~~sh
pip freeze > requirements.txt
~~~
