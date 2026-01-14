import subprocess
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Sitegen dev script", usage="python dev.py ", description="Dev script for sitegen."
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
        cmd = [sys.executable, "-m", "pip", "install", deps]
    else:
        cmd = [sys.executable, "-m", "pip", "install", *deps]

    subprocess.run(cmd)

def build(nuitka: bool=False, compiler: str) -> None:
    if nuitka:
        if compiler == "gcc" and sys.platform == "win32":
            compiler = "mingw64"
        elif compiler == "msvc":
            if sys.platform != "win32":
                compiler = ""
            else:
                compiler = "msvc=latest"
        compiler = "--" + compiler

        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"])

        cmd = [sys.executable, "-m", "nuitka", "--follow-imports", "--mode=onefile", "--assume-yes-for-downloads", "--jobs=-1", "--product-name=sitegen", compiler, "--output-dir=dist" ,"sitegen.py"]
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        cmd = [sys.executable, "-m", "pyinstaller", "--onefile","--clean" , "--noconfirm", "sitegen.py"]

    subprocess.run(cmd)


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


