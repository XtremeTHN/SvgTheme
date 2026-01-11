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
      python = (
        pkgs.python3.withPackages (
          ps: with ps; [
            pyqt6
          ]
        )
      );
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          python
          pkgs.pkg-config
          pkgs.ruff
        ];
      };
    };
}
