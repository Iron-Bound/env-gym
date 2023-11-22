{pkgs ? import <nixpkgs> {}}:

pkgs.mkShell {
  packages = with pkgs.python3Packages; [
    torch
    pip
    virtualenv
    numpy
    pyglet
    pygame
    cffi
    opencv4
    python-lsp-server
    ipykernel
    jupyterlab_launcher
    jupyterlab
    sounddevice
    rich
    ruamel-yaml
    pandas
  ];
  buildInputs = with pkgs; [
    #python3
    portaudio
    qt5.wrapQtAppsHook
    xvfb-run
    libGLU
  ];
  propagatedBuildInputs = [
    pkgs.mgba
  ];

  shellHook = ''
    source env/bin/activate
    export LD_LIBRARY_PATH="${pkgs.mgba}/lib"
    # export LD_LIBRARY_PATH=$(nix eval --raw nixpkgs.mgba)/lib
    # export LD_LIBRARY_PATH=$NIX_LDFLAGS
    export QT_QPA_PLATFORM=wayland
  '';
}