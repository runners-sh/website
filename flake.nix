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

    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (python313.withPackages (
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
              ]
            ))
            mask
          ];
        };

      });
      packages = forAllSystems (
        system:
        let
          sps = pkgs.${system};
        in
        {
          alive = sps.python313Packages.alive-progress.overrideAttrs ({
            postInstall = ''rm $out/LICENSE'';
          });
        }
      );
    };
}
