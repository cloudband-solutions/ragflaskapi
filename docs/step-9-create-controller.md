# 9) Create a controller (example: Project)

## 9.1 Add tests (domain + per-operation files)
Create a domain folder under `tests/` (for example `tests/projects/`), and split
each CRUD operation into its own file (similar to `tests/users/test_create.py`).

Example files:
- `tests/projects/test_list.py`
- `tests/projects/test_show.py`
- `tests/projects/test_create.py`
- `tests/projects/test_update.py`
- `tests/projects/test_delete.py`
