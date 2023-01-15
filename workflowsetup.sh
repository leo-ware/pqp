python3 -m venv venv
source venv/bin/activate
pip install -q -r sherlock_py/requirements.txt
maturin develop -q -m backend/Cargo.toml