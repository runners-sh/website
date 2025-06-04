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

## Contributing

### PR naming convention
This project follows the [Conventional Commit specification v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). You can use the following commit types:
- All types recognized by the [Angular convention](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type)
- `content:` for PRs that only introduce Markdown content
- `revert:` for reverted changes

You should also try to specify one of the following scopes if applicable:
- `main-site` for changes made to the actual website
- `solstice` for changes made to solstice
- `nix` for changes related to Nix packaging.

### Blog posts
See our [Guide for Publishing Blog Posts](blog-posts-guide.md).
