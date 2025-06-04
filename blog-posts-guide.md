# Guide for Publishing Blog Posts

> [!IMPORTANT]
> Since this is a public repository, We should make it clear that only members of the solrunners discord server can post on the solrunners website. To get your PR merged, send a link to it in [#website/Blog post PRs (discord)](https://discord.com/channels/1009569562032885772/1379796345572818996).

## 1. Joining the GitHub organization
You can request to join the GitHub organization by sending a message with your GitHub username in [#website/Join the github org! (discord)](https://discord.com/channels/1009569562032885772/1379801267097964695).

## 2. Setting up the environment
> [!NOTE]
> If you are unfamiliar with Git, feel free to ask for help in the #website channel.

First, clone the repository:
```sh
git clone git@github.com:runners-sh/website.git
```

Then follow the [installation steps in the README of this repository](README.md#Installation). Finally, run `mask serve main-site` and visit http://localhost:5123/ to get a preview of your local copy of the website.

## 3. Adding your files
The website repo has branch protection enabled, so creating a new branch is required.

Blog posts are written in markdown and are located in the `main-site/blog` directory. The name of your file should be `snake_case` (lowercase with underscores), and should be preferably less than 30 and strictly less than 50 characters long.

The following Markdown features are supported:
- All features described by [John Gruber's Markdown Syntax](https://daringfireball.net/projects/markdown/syntax)
- [Fenced code blocks](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/) with [syntax highlighting](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/)
- [Footnotes](https://python-markdown.github.io/extensions/footnotes/)
- [Attribute lists](https://python-markdown.github.io/extensions/attr_list/)
- [Definition lists](https://python-markdown.github.io/extensions/definition_lists/)
- [Tables](https://python-markdown.github.io/extensions/tables/)
- LaTeX math notation (`$...$` and `$$...$$`) through [L2M4M](https://pypi.org/project/L2M4M/)
- [Admonition blocks](https://python-markdown.github.io/extensions/admonition/)
- [Emoji](https://facelessuser.github.io/pymdown-extensions/extensions/emoji/)

If you need a feature that is not in this list but is supported by [Pymdown Extensions](https://facelessuser.github.io/pymdown-extensions/) or [python-markdown](https://python-markdown.github.io/), let us know in the #website channel.

### Frontmatter
Each blog post needs the following frontmatter fields:

```yml
---
title: My First Blog Post # blog post title
author: username # your Discord username
date: 1983-09-27 # release date
barcode: 42424246 # EAN-8 barcode
---
```

The barcode needs to be an 8-digit sequence where:
- The first digit must be `2` or `4`
- The last digit is the checksum of the code. The website builder will let you know what it should be if it is incorrect.

You can generate a random barcode that isn't already in use with `mask new-post`.

### Images
Image attachments go into `main-site/public/img` and should be linked to with `![alt-text](/public/img/<file name>)`. We recommend you use lossy formats that are widely supported (e.g. AVIF or JPEG) for images without transparency. SVGs are also supported.

Verify your blog post looks as intended by running `mask serve main-site` and visiting `http://localhost:5123/blog/<blog-post-name>`.

## 4. Creating a PR
Once you are satisified with how the blog post looks, you can commit your changes.

> [!WARNING]
> Our CI requires single-commit PRs to have semantic commit titles. This is unintended, and we are looking for a way to disable this.
>
> For now, please make your commit title conform to the Conventional Commit specification if this is the case.

Then, create a PR named: `content(main-site): <your blog post title here`. No description needs to be provided. Once the PR is made, let us know by sending a link in [#website/Blog post PRs (discord)](https://discord.com/channels/1009569562032885772/1379796345572818996).

## 5. Done!
Once the PR is merged, we will try and deploy the website ASAP. This can usually be done right away.
