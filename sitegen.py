import os
import shutil
import webbrowser
import markdown
import argparse
import glob
import sys
import http.server
import socketserver


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("sitegen")

    parser.add_argument(
        "content_dir",
        type=str,
        help="The directory containing the content files.",
    )
    parser.add_argument(
        "--name", "-n", type=str, help="The name of the website.", default="My site"
    )
    parser.add_argument(
        "--host",
        "-H",
        type=str,
        help="the address where the website is hosted",
        default="localhost",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="The port where the website is hosted.",
        default=8888,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="the path where the output files will be stored.",
        default="output",
    )
    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        help="The css theme file.",
        default="themes/light_theme.css",
    )
    parser.add_argument(
        "--start",
        "-s",
        action="store_true",
        help="Option to launch a server locally.",
        default=False,
    )
    return parser.parse_args(sys.argv[1:])


def get_source_files(directory: str) -> dict[str, list[str]]:
    files = {}
    base_dir = os.path.abspath(directory)

    for i in glob.iglob(os.path.join(base_dir, "**", "*.md"), recursive=True):
        dirname = os.path.dirname(i)
        if dirname == os.path.abspath(base_dir):
            dirname = "."
        else:
            dirname = os.path.basename(dirname)
            dirname = os.path.join(".", dirname)

        if dirname not in files:
            files[dirname] = []

        files[dirname].append(i)

    return files


def create_index_files(files: dict[str, list[str]]) -> None:
    index = "index.md"

    for dirname, files in files.items():
        if files:
            index_path = os.path.join(dirname, index)

            if not os.path.exists(index_path):
                with open(index_path, "w") as f:
                    f.write(" ")


def setup_output_dir(output: str, theme: str) -> None:
    if os.path.exists(output) and os.path.isdir(output):
        for i in glob.iglob(os.path.join(output, "**"), recursive=True):
            if os.path.isfile(i):
                os.remove(i)
    else:
        os.makedirs(output)

    os.makedirs(os.path.join(output, "themes"), exist_ok=True)
    shutil.copyfile(
        os.path.abspath(theme), os.path.abspath(os.path.join(output, theme))
    )

    os.makedirs(os.path.join(output, "assets"), exist_ok=True)


def convert_md(
    files: dict[str, list[str]], output: str, content_dir: str, name: str, theme: str
) -> list:
    html_files = []
    header = f"# [{name}](/index.html)\n\n"

    for _, files in files.items():
        for i in files:
            with open(i, "r") as f:
                rel_path = os.path.relpath(i, content_dir)
                base, _ = os.path.splitext(rel_path)
                html_path = os.path.join(output, base + ".html")

                body = markdown.markdown(header + f.read())
                html = [
                    f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{name}</title>
    <link rel="stylesheet" href="{theme}">
</head>
<body>
    {body}
</body>
</html>
""",
                    html_path,
                ]

            html_files.append(html)

    return html_files


def create_html_files(data: list) -> None:
    for content, path in data:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


def start_server(host: str, port: int, directory: str) -> None:
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler

    host = host.replace("http://", "").replace("https://", "")
    url = f"http://{host}:{port}"
    with socketserver.TCPServer((host, port), handler) as server:
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop.\n")

        webbrowser.open(url)

        server.serve_forever()


if __name__ == "__main__":
    args = parse_args()
    print(args.theme)
    print()
    source_files = get_source_files(args.content_dir)

    setup_output_dir(args.output, args.theme)
    create_index_files(source_files)
    html_data = convert_md(
        source_files, args.output, args.content_dir, args.name, args.theme
    )

    create_html_files(html_data)

    print(
        f"{len(html_data)} HTML files created in directory: {os.path.abspath(args.output)}/\n"
    )

    if args.start:
        try:
            start_server(args.host, args.port, args.output)
        except KeyboardInterrupt:
            print("\nServer closed. Exiting...")
            sys.exit()
