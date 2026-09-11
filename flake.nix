{
  description = "Entorno de desarrollo para lockey";

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
        protobuf
      ];
      buildInputs = [ pkgs.openssl ];

      OPENSSL_DIR = "${pkgs.openssl.dev}";
      OPENSSL_LIB_DIR = "${pkgs.openssl.out}/lib";
      OPENSSL_INCLUDE_DIR = "${pkgs.openssl.dev}/include";
      # Variables de entorno para que los scripts build.rs (prost-build, tonic, etc.) encuentren protoc
      PROTOC = "${pkgs.protobuf}/bin/protoc";
      PROTOC_INCLUDE = "${pkgs.protobuf}/include";
    };
  };
}
