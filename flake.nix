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
        ppkgs: with ppkgs; [
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
          pytest
          python-frontmatter
          pyyaml
          ruff
          sniffio
          watchfiles
          setuptools
        ];
    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (python313.withPackages dependencies)
            mask
          ];
        };

      });
      packages = forAllSystems (
        system:
        let
          ppkgs = pkgs.${system}.python3Packages;
          fs = pkgs.${system}.lib.fileset;
        in
        {
          solstice = ppkgs.buildPythonPackage {
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
            propagatedBuildInputs = dependencies ppkgs;
          };
        }
      );
    };
}
