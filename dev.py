import os
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Sitegen dev script",
        usage="python dev.py ",
        description="Dev script for sitegen.",
    )
    parser.add_argument(
        "--build", action="store_true", default=False, help="build binary for sitegen."
    )
    parser.add_argument(
        "--nuitka", action="store_true", default=False, help="Build using nuitka."
    )
    parser.add_argument(
        "--compiler",
        default="",
        choices=["gcc", "msvc", "clang"],
        help="Choose the compiler to use for building. Only used if `--nuitka` is used.",
    )

    return parser.parse_args(sys.argv[1:])


def install_deps(deps: list[str] | str) -> None:
    if type(deps) == str:
        cmd = f"{sys.executable} -m pip install {deps}"
    else:
        cmd = f"{sys.executable} -m pip install {''.join(deps)}"

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
        compiler = "--" + compiler

        os.system(f"{sys.executable} -m pip install nuitka")

        cmd = [
            "nuitka",
            "--follow-imports",
            " --mode=onefile",
            " --assume-yes-for-downloads",
            " --product-name=sitegen",
            " " + compiler,
            " --output-dir=dist",
            " sitegen.py",
        ]
        cmd = "".join(cmd)
    else:
        os.system(f"{sys.executable} -m pip install pyinstaller")
        cmd = [
            "pyinstaller",
            " --onefile",
            " --clean",
            " --noconfirm",
            " sitegen.py",
        ]
        cmd = "".join(cmd)

    os.system(cmd)


if __name__ == "__main__":
    args = parse_args()

    if args.build:
        print("Installing dependencies...")
        install_deps("markdown")
        print("Installed dependecies.", "\n")

        print("Beginning compilation...")
        build(args.nuitka, args.compiler)
        print("Compilation complete. Results are available in ./dist")
    else:
        pass
