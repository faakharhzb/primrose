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
    return parser.parse_args(sys.argv[1:])


def get_source_files(directory: str) -> list[str]:
    return glob.glob(
        os.path.join(os.path.abspath(directory), "**", "*.md"),
        recursive=True,
    )


def convert_md(files: list, output: str, content_dir: str) -> list:
    html_files = []

    if "index.md" not in files:
        files.append(os.path.abspath("index.md"))
        with open(files[-1], "w") as f:
            f.write("Nothing to see here.")

    for i in files:
        if not os.path.isdir(i):
            with open(i, "r") as f:
                rel_path = os.path.relpath(i, content_dir)
                base, _ = os.path.splitext(rel_path)
                html_path = os.path.join(output, base + ".html")

                html = [markdown.markdown(f.read()), html_path]

        html_files.append(html)

    return html_files


def create_html_files(data: list, output: str) -> None:
    if os.path.exists(output) and os.path.isdir(output):
        for i in glob.iglob("output/**", recursive=True):
            if os.path.isfile(i):
                os.remove(i)
    else:
        os.makedirs(output)

    for content, path in data:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


def start_server(port: int, directory: str) -> None:
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    url = f"http://localhost:{port}"
    with socketserver.TCPServer(("", port), handler) as server:
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop.")

        webbrowser.open(url)

        server.serve_forever()


if __name__ == "__main__":
    args = parse_args()
    source_files = get_source_files(args.content_dir)
    html_data = convert_md(source_files, args.output, args.content_dir)

    create_html_files(html_data, args.output)

    try:
        start_server(args.port, args.output)
    except KeyboardInterrupt:
        print("\nServer closed. Exiting...")
        sys.exit()
