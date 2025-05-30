{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});

      dependencies =
        sys: ppkgs: with ppkgs; [
          anyio
          click
          idna
          iniconfig
          jinja2
          markdown
          markupsafe
          mypy-extensions
          packaging
          pathspec
          platformdirs
          pluggy
          pymdown-extensions
          pytest
          python-frontmatter
          pyyaml
          ruff
          sniffio
          watchfiles
          setuptools
          minify-html
          self.packages.${sys}.l2m4m
          selenium
        ];
    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (python313.withPackages (dependencies system))
            mask
            (writeShellScriptBin "serve" "python -m main-site serve")
            firefox
          ];
        };

      });
      packages = forAllSystems (
        system:
        let
          opack = import nixpkgs {
            inherit system;
            overlays = [
              (final: prev: {
                solstice = prev.python313Packages.buildPythonPackage {
                  name = "solstice";
                  format = "pyproject";
                  src = fs.toSource {
                    root = ./.;
                    # since we have 2 projects, this prevents shit from breaking
                    fileset = fs.unions [
                      ./README.md
                      ./solstice
                      ./pyproject.toml
                    ];
                  };
                  propagatedBuildInputs = dependencies system prev.python313Packages;
                };
                l2m4m = prev.python313Packages.buildPythonPackage {
                  name = "l2m4m";
                  format = "pyproject";
                  src = prev.fetchFromGitLab {
                    owner = "parcifal";
                    repo = "l2m4m";
                    rev = "471c74b85b61b9e1b4546c510c4b840d960c2eaa";
                    hash = "sha256-3W8x9cThvQ7yM5n/eiQ9fISd1kvUvWQ4A9gYRFnWNbw=";
                  };
                  propagatedBuildInputs = with prev.python313Packages; [
                    markdown
                    latex2mathml
                    setuptools
                  ];
                };
              })
            ];
          };

          fs = pkgs.${system}.lib.fileset;
        in
        rec {
          solstice = opack.solstice;

          l2m4m = opack.l2m4m;

          main-site = opack.stdenv.mkDerivation {
            name = "main-site";
            version = "0.1.0";
            src = fs.toSource {
              root = ./.;
              fileset = fs.unions [
                ./mmain-site
                ./pyproject.toml
                ./README.md
              ];
            };

            nativeBuildInputs = [
              (opack.python313.withPackages (ppkgs: [ solstice ]))
            ];

            buildPhase = ''
              python -m main-site
            '';

            installPhase = ''
              cp -r dist/ $out
            '';
          };

          default = main-site;
        }
      );
    };
}
