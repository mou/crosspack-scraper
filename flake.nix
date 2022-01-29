{
  description = "Crosspack Food Service menu scraper";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }: {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [ poetry2nix.overlay
        (final: prev: {
          # The application
          crosspack-scraper = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      rec {
        apps = {
          crosspack-scraper = pkgs.crosspack-scraper;
        };

        defaultApp = apps.crosspack-scraper;

        packages = {
          crosspack-scraper = pkgs.crosspack-scraper;
        };

        defaultPackage = pkgs.crosspack-scraper;

#       devShell = pkgs.mkShell {
#         buildInputs = with pkgs; [
#           python39
#           poetry
#         ];
#       };
        devShell = (pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          editablePackageSources = {
            crosspack-scraper = ./.;
          };
        }).env.overrideAttrs (oldAttrs: {
          buildInputs = [ pkgs.poetry ];
        });
      }));
}
