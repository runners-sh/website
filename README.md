# ssg branch

solrunners site generator!

# Installation

## Using `mask`
Install `mask` from the AUR or from crates.io using `cargo install mask`. Then run `mask init` to set up the .venv and install the requirements. Use `mask --help` for a list of commands.

## Manually
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Building

## Using `mask`
```sh
mask build
```
Build files will output to `/dist`.

## Manually
```sh
python3 -m blog
```
