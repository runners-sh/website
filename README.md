# Solrunners website
Source code for the [runners.sh](https://runners.sh) website.

## Installation
Requirements:
- `python >= 3.13`
- `mask`

This project uses the [`mask` command runner](https://github.com/jacobdeichert/mask). You can install it from the AUR or crates.io. Refer to [`maskfile.md`](maskfile.md) for manual installation instructions.

To initialize the environment, run `mask init`. This sets up a python venv and installs the required packages.

### Nix (flakes)

When using the nix package manager you can build the website using `nix build` with flake support enabled.  
A development shell is also available which can be used instead of a venv and can be accessed using `nix develop`.

## Building, testing, etc.
Run `mask help` or refer to the [`maskfile.md`](maskfile.md) for different dev commands.
