# Solrunners website project tasks

## init
> Initialize the python venv and install required packages

```sh
if ! type python > /dev/null; then
    echo "Python is not installed."
    exit 1
fi

if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d $MASKFILE_DIR/.venv ]; then
        echo "Creating Python venv..."
        python -m venv .venv
    fi
    echo "Entering venv..."
    source $MASKFILE_DIR/.venv/bin/activate
fi

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

printf "Project initialized. Don't forget to load the venv using \033[32msource .venv/bin/activate\033[0m.\n"
```

## verify
> Runs all CI checks

```sh
python3 -m pytest && ruff check && ruff format --check \
&& printf "\e[32mCI checks passed!\e[0m\n" \
|| printf "\e[31mCI checks failed.\e[0m\n"
```

## test
> Run tests

```sh
python3 -m pytest
```

## format
> Run the ruff formatter

**OPTIONS**
- check
	- flags: --check
	- desc: Only check formatting

```sh
[[ "$check" == "true" ]] \
&& ruff format --check \
|| ruff format
```

## check
> Run the ruff checker

**OPTIONS**
- fix
	- flags: --fix
	- desc: Also apply autofixes

```sh
[[ "$fix" == "true" ]] \
&& ruff check --fix \
|| ruff check
```

## update-reqs
> Update the requirements.txt file

```sh
pip freeze > requirements.txt
```

## build (module)
> Build the specified website

Build files will appear in the `./dist` folder.

```sh
python -m "$module"
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

## clean
> Clean all generated files

```sh
cd $MASKFILE_DIR
rm -rf \
	dist \
	.ruff_cache \
	.pytest_cache \
	**/__pycache__
```
