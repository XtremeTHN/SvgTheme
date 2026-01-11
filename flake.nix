{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = (pkgs.python314.withPackages (ps: with ps; [
        xdg-base-dirs
        colorama
      ]));
      
      nativeBuildInputs = with pkgs; [
        python
        meson
        ninja
      ];
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        inherit nativeBuildInputs;
        packages = [
          pkgs.ruff
        ];
      };

      packages.${system}.default = pkgs.stdenv.mkDerivation {
        name = "svgtheme";
        version = "0.1.0";
        src = ./.;

        inherit nativeBuildInputs;
      };
    };
}
