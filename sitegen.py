import os
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
        default="http://localhost",
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
        "--start",
        "-s",
        action="store_true",
        help="Option to launch a server on localhost",
        default=False,
    )
    return parser.parse_args(sys.argv[1:])


def get_source_files(directory: str) -> dict[str, list[str]]:
    files = {}
    base_dir = os.path.abspath(directory)

    for i in glob.iglob(f"{base_dir}\\**\\*.md", recursive=True):
        dirname = os.path.dirname(i)
        if dirname == os.path.abspath(base_dir):
            dirname = "."
        else:
            dirname = dirname.split("\\")[-1]
            dirname = os.path.join(".", dirname)

        if dirname not in files:
            files[dirname] = []

        files[dirname].append(i)

    return files


def create_index_files(files: dict[str, list[str]]) -> None:
    index = "index.md"

    for i, j in files.items():
        if index not in os.listdir(os.path.abspath(i)):
            j.append(index)

            with open(os.path.join(i, index), "w") as f:
                f.write("")


def convert_md(
    files: dict[str, list[str]], output: str, content_dir: str, name: str
) -> list:
    html_files = []
    header = f"# [{name}](/index.html)\n\n"

    for _, files in files.items():
        for i in files:
            with open(i, "r") as f:
                rel_path = os.path.relpath(i, content_dir)
                base, _ = os.path.splitext(rel_path)
                html_path = os.path.join(output, base + ".html")

                html = [markdown.markdown(header + f.read()), html_path]

            html_files.append(html)

    return html_files


def create_html_files(data: list, output: str) -> None:
    if os.path.exists(output) and os.path.isdir(output):
        for i in glob.iglob(f"{output}/**", recursive=True):
            if os.path.isfile(i):
                os.remove(i)
    else:
        os.makedirs(output)

    for content, path in data:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


def start_server(host: str, port: int, directory: str) -> None:
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler

    url = f"{host}:{port}"
    if not url.startswith("http"):
        url = "https://" + url

    with socketserver.TCPServer(("", port), handler) as server:
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop.")

        webbrowser.open(url)

        server.allow_reuse_address = True
        server.serve_forever()


if __name__ == "__main__":
    args = parse_args()
    source_files = get_source_files(args.content_dir)

    create_index_files(source_files)
    html_data = convert_md(source_files, args.output, args.content_dir, args.name)

    create_html_files(html_data, args.output)

    print(
        f"{len(html_data)} HTML files created in directory: {os.path.abspath(args.output)}/"
    )

    if args.start:
        try:
            start_server(args.host, args.port, args.output)
        except KeyboardInterrupt:
            print("\nServer closed. Exiting...")
            sys.exit()
