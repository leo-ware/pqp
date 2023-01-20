python3 -m venv venv
source venv/bin/activate
pip install -q -r doc_requirements.txt
maturin develop
