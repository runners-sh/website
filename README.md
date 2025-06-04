# Solrunners website
Source code for the [runners.sh](https://runners.sh) website.

## Installation
Requirements:
- `python >= 3.13`
- `mask`

This project uses the [`mask` command runner](https://github.com/jacobdeichert/mask). You can install it from the AUR or crates.io. Refer to [`maskfile.md`](maskfile.md) for manual installation instructions.

To initialize the environment, run `mask init`. This sets up a python venv and installs the required packages. Don't forget to `source .venv/bin/activate` afterwards!

Run `mask help` or refer to the [`maskfile.md`](maskfile.md) for different dev commands.

### Nix (flakes)
When using the Nix package manager with flake support enabled, you can build the website using `nix build`. A development shell is also available and can be accessed using `nix develop`, removing the need to use a venv.

##