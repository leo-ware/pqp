Welcome to `pqp`! Here is a quick overview of some basic things.

## Installation

The package can be installed from PyPi using `pip`:

```bash
pip install pqp
```

## Testing

Clone the repo and install local dependencies:

```bash
# run in root of repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After activating the virtual environment, run `test.sh` using `source`. This will build the rust library and run the tests for both the rust and python code.

```bash
# run in root of repo
source test.sh
```

## Documentation

To build the documentation, use the makefile in the `docs` directory:

```bash
# run in root of repo
cd python/pqp/docs

# regenerate documentation source (only run when adding new modules)
make autodoc

# build html documentation (runs local development server)
make livehtml
```

To deploy the documentation to github pages, run the following. This will push the docs build to the `gh-pages` branch of the repo. Github pages will serve. This will not work if you have not already built the docs.

```bash
# run in root of repo
source venv/bin/activate
source publish_docs.sh
```