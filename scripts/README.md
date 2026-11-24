# Scripts

Run from the repo root after `pip install -r api/requirements.txt`.

- `seed.py`: summary of the fake demo data (1 school, 3 courses, 40 fake students). `--json` prints all of it. Writing it into Supabase comes in Phase 3.
- `compare_matching.py`: greedy vs. max-weight on the demo data, then on ~600 random fake classes. Use these numbers in the Devpost writeup. `--trials N` changes how many seeds it runs.
