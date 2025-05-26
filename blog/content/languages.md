---
title: Programming Languages Gallery
author: Cubic
date: 2025-05-26
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
