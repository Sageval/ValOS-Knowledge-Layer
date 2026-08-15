# Setup Notes & Gotchas

This isn't a restatement of the tech stack (see the README for that) — it's a running log of things that actually happened while setting this project up, kept so future-me (or anyone else running into the same thing) doesn't have to debug it twice.

---

## Renaming the project folder broke the venv

**What happened:** After renaming the project folder from `rag` to `ValOS-Knowledge-Layer`, running `python` or `pip` inside the activated venv failed with `The system cannot find the file specified.`

**Why:** A virtual environment's activation scripts (`venv/Scripts/Activate.ps1` on Windows, `venv/bin/activate` on macOS/Linux) hardcode the *absolute path* to the venv folder at creation time. Renaming or moving the parent directory doesn't update that path — the scripts keep pointing at a location that no longer exists.

**Fix:** There's no reliable way to "rename" a venv in place. Delete it and recreate it from the new location:

```bash
rm -rf venv                  # or manually delete on Windows
python -m venv venv
# then reactivate and reinstall
pip install -r requirements.txt
```

**Takeaway:** Settle on a project folder name *before* creating the venv, or recreate the venv any time the parent folder moves or is renamed.

---

## Re-running `build_knowledge_base.py` used to fail

**What happened:** Running the ingestion script a second time against an already-populated ChromaDB collection raised a duplicate-ID error.

**Why:** `collection.add()` assigns IDs like `chunk0`, `chunk1`, etc. Running it again tries to add those same IDs into a collection that already has them.

**Fix:** The script now calls `client.delete_collection(name="personal_profile")` before rebuilding, so each run starts from a clean collection instead of colliding with the previous one. See `app/build_knowledge_base.py`.

---

## Environment details

- Developed on Windows, PowerShell
- Python 3.x (see `requirements.txt` for the exact dependency versions this was built against)
- Ollama running locally with:

  ```bash
  ollama pull phi3:mini
  ollama pull nomic-embed-text
  ```

- IDE: Visual Studio Code

---

*This file is expected to grow as new issues come up during development — it's a log, not a finished doc.*
