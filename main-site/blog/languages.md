---
title: Programming Languages Gallery
author: Cubic
date: 2025-05-26
barcode: 29015535
---

```rs
#[tokio::main(flavor = "current_thread")]
async fn main() -> ExitCode {
    tracing::subscriber::set_global_default(subscriber::MegacorpSubscriber::default()).unwrap();

    let args = match <Args as clap::Parser>::try_parse() {
        Ok(args) => args,
        Err(err) => {
            eprintln!("{err}");
            return ExitCode::from(40u8);
        }
    };

    if let Err(err) = main_loop(args).await {
        eprintln!("\r\n{err}");
        return ExitCode::FAILURE;
    }

    ExitCode::SUCCESS
}
```

```py
from solstice import *

init(__package__)
copy("public")
page("index.jinja")

for dirname, file, name in recurse_files("content", [".md"]):
	src_path = path.join(dirname, file)
	dist_path = path.join(dirname, name + ".jinja")
	page_md("blog.jinja", src_path, dist_path)
```

```c++
int LedPin1 = 6;
int LedPin2 = 11;
int LedPin3 = 10;
int LedPin4 = 9;
int ButtonPin = 2;
int versie = 4;
const int VersieAantal = 9;

void setup()
{
    Serial.begin(9600);
    pinMode(LedPin1, OUTPUT);
    pinMode(LedPin4, OUTPUT);
    pinMode(LedPin2, OUTPUT);
    pinMode(LedPin3, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(ButtonPin, INPUT);
    attachInterrupt(digitalPinToInterrupt(ButtonPin), InterruptSwitch, RISING);
}
```

```nix

    rule = fconst { type = "hr"; } (
      pack part.smallIndent (choice (
        map (char: filter (lst: builtins.length lst >= 3) (listOf (symbol char) (many part.whitespace))) [
          "*"
          "-"
          "_"
        ]
      )) part.blankLines
    );

    indentedCodeBlock =
      let
        parseCodeIndent = filter (len: len == tabSize) part.indent;
        parseCodeLine = pack parseCodeIndent (some (notSymbol "\n")) part.lineEnd;
        parseBlockCore = app (fmap (old: new: old ++ [ new ]) (
          many (alt parseCodeLine (fconst [ ] (skipThen (upTo part.whitespace tabSize) part.lineEnd)))
        )) parseCodeLine;
      in
      fmap (lines: {
        type = "code";
        content = lines;
        info = [ ];
      }) (thenSkip parseBlockCore (greedy part.blankLine));
```

```html
<!doctype html>
<html class="theme-dark">
    <head>
        <meta charset="utf-8" />
        <title>solrunners</title>
        <link
            rel="icon"
            href="/public/img/solrunners-color-64.png"
            sizes="64x64"
        />
        <link rel="icon" href="/public/img/solrunners-color.svg" />
        {% block head %}{% endblock %}
    </head>
    <body>
        {% block body %}{% endblock %}
    </body>
</html>
```

```bash
case $1 in
    "init")
    echo "initialising git repo"
    [[ ! -d '.git' ]] && echo "creating .git folder" && mkdir .git
    [[ ! -d '.git/objects' ]] && echo "creating objects folder in .git" && mkdir .git/objects
    [[ ! -d '.git/refs' ]] && echo "creating objects folder in .git" && mkdir .git/refs
    [[ ! -f '.git/HEAD' ]] && echo "HEAD missing, creating..." && printf "ref: refs/heads/main\n" > .git/HEAD
    exit
    ;;
    "cat-file")
    # TODO: add actual parsing to the arguments
    if [[ ! $2 = '-p' || $3 = '' ]]; then echo "please implement cat-file with params $*"; exit; fi # asserting that the 'hash' is included
    unzlib "$(fp "$3")"
    exit
    ;;
    "hash-object")
    if [[ ! $2 = '-w' || $3 = '' ]]; then echo "please implement hash-object with params $*"; exit; fi
    SHA=$(printf "blob %s\0%s" "$(stat -c%s "$3")" "$(cat "$3")" | zlib | shasum - | awk '{print $1}')
    zlib "$(printf "blob %s\0%s" "$(stat -c%s "$3")" "$(cat "$3")")" > "$(fp "$SHA")"
    echo "$SHA"
    exit
    ;;
esac
```
