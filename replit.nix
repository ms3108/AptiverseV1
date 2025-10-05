{ pkgs }: {
  deps = [
    pkgs.postgresql
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
    pkgs.nodePackages.serve
    pkgs.bash
    pkgs.gcc
  ];
}
