# RAG Flask API

A Retrieval Augmented Generation engine in Flask.

## Dev Setup

0. (Optional) Create your python environment and install packages.

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

1. Create `.env` file and modify values accordingly.

```bash
cp .env.example .env
```

2. Initialize the database

```bash
flask db create
flask db init
flask db migrate -m "init"
flask db upgrade
```

2. Run tests:

```bash
./bin/test
```

3. Run the server:

```bash
./bin/dev
```
