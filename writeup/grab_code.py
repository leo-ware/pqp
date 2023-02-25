# Script for grabbing code from the python and rust directories and putting it in a massive
# jupyter notebook. Apparently this is the format you guys (graders) want (?)
# I recommend going to github and looking at the code there, it's much easier to read.

import os
import json

def main():
    # project = "/Users/leoware/Documents/pqp"
    agg = "/Users/leoware/Documents/pqp/writeup/agg.ipynb"
    python = "/Users/leoware/Documents/pqp/python/pqp"
    rust = "/Users/leoware/Documents/pqp/src"

    def make_cell(name, handle, comment, lang):
        source = [f"\n```{lang}\n"]
        source.append(f"{comment} {name}")
        for line in handle.readlines():
            source.append(line)
        source.append("\n```")
        cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": source
        }
        return cell

    cells = [{
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# Appendix: Code"]
    }]
    for lang, dir, ext, comment in [["python", python, ".py", "#"], ["rust", rust, ".rs", "//"]]:
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"\n## `{lang}` code"]
        })
        for root, _, files in os.walk(dir):
            for f_name in files:
                f_name = os.path.join(root, f_name)
                if f_name.endswith(ext):
                    with open(f_name, "r") as f:
                        cell = make_cell(f_name, f, comment, lang)
                        cells.append(cell)

    with open(agg, "r") as f:
        notebook = json.load(f)
    notebook["cells"] = cells
    with open(agg, "w") as f:
        json.dump(notebook, f)

if __name__ == "__main__":
    main()
