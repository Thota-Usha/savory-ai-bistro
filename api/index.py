import sys
import os

# Add project root and backend to sys.path so modules resolve seamlessly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, "backend")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import shutil

# Ensure writable database in /tmp for Vercel Serverless
if os.path.exists("/tmp"):
    tmp_db = "/tmp/restaurant.db"
    if not os.path.exists(tmp_db):
        for candidate in [
            os.path.join(backend_dir, "restaurant.db"),
            os.path.join(project_root, "restaurant.db")
        ]:
            if os.path.exists(candidate):
                try:
                    shutil.copyfile(candidate, tmp_db)
                    os.chmod(tmp_db, 0o666)
                    break
                except Exception:
                    pass
    else:
        try:
            os.chmod(tmp_db, 0o666)
        except Exception:
            pass

from app.main import app
