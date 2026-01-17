import os
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "primrose dev script",
        usage="python dev.py ",
        description="Dev script for primrose.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        default=False,
        help="build binary for primrose.",
    )
    parser.add_argument(
        "--nuitka",
        action="store_true",
        default=False,
        help="Build using nuitka.",
    )
    parser.add_argument(
        "--compiler",
        default="",
        choices=["gcc", "msvc", "clang"],
        help="Choose the compiler to use for building. Only used if `--nuitka` is used.",
    )

    return parser.parse_args(sys.argv[1:])


def install_deps(deps: list[str] | str) -> None:
    if type(deps) is str:
        cmd = f"{sys.executable} -m pip install {deps}"
    else:
        cmd = f"{sys.executable} -m pip install {' '.join(deps)}"

    os.system(cmd)


def build(nuitka: bool, compiler: str) -> None:
    if nuitka:
        if compiler == "gcc" and sys.platform == "win32":
            compiler = "mingw64"
        elif compiler == "msvc":
            if sys.platform != "win32":
                compiler = ""
            else:
                compiler = "msvc=latest"
        if compiler:
            compiler = "--" + compiler
        else:
            compiler = " "

        cmd = [
            sys.executable,
            "-m",
            "nuitka",
            "--onefile",
            "--assume-yes-for-downloads",
            "--follow-imports",
            compiler,
            "--output-dir=dist",
            f"--output-filename={'primrose.exe' if sys.platform == 'win32' else 'primrose'}",
            "primrose.py",
        ]
    else:
        cmd = [
            "pyinstaller",
            "--onefile",
            "--clean",
            "--noconfirm",
            "primrose.py",
        ]

    cmd = " ".join(cmd)
    os.system(cmd)


if __name__ == "__main__":
    args = parse_args()

    if args.build:
        print("Installing dependencies...")
        install_deps(["markdown", "nuitka", "pyinstaller"])
        print("Installed dependecies.", "\n")

        print("Beginning compilation...")
        build(args.nuitka, args.compiler)
        print("Compilation complete. Results are available in ./dist")
    else:
        pass
