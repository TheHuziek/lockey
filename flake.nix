{
  description = "Entorno de desarrollo para Rust puro";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      nativeBuildInputs = with pkgs; [
        cargo
        rustc
        rustfmt
        rustPackages.clippy
        rust-analyzer
      ];
    };
  };
}
