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
          jinja2
          pymdown-extensions
          python-frontmatter
          markdown
          self.packages.${sys}.l2m4m
        ];
    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (python313.withPackages (
              ppkgs:
              dependencies system ppkgs
              ++ [
                ppkgs.pytest
                ppkgs.selenium
                ppkgs.watchfiles
              ]
            ))
            (writeShellScriptBin "serve" "python -m main-site serve")
            mask # if there is a desire to use the maskfile
            firefox # to function as a selenium test driver
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
              (final: prev: {
                runners-common = prev.python313Packages.buildPythonPackage {
                  name = "runners_common";
                  format = "pyproject";
                  src = fs.toSource {
                    root = ./.;
                    fileset = fs.unions [
                      ./runners_common
                      ./pyproject.toml
                    ];
                  };
                  propagatedBuildInputs = [ prev.solstice ];
                };
              })
            ];
          };

          fs = pkgs.${system}.lib.fileset;
        in
        rec {
          solstice = opack.solstice;

          l2m4m = opack.l2m4m;

          runners-common = opack.runners-common;

          main-site = opack.stdenv.mkDerivation {
            name = "main-site";
            version = "0.1.0";
            src = fs.toSource {
              root = ./.;
              fileset = fs.unions [
                ./main-site
                ./pyproject.toml
                ./README.md
              ];
            };

            nativeBuildInputs = [
              (opack.python313.withPackages (ppkgs: [
                solstice
                runners-common
              ]))
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
