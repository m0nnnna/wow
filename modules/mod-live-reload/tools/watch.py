#!/usr/bin/env python3
"""
wow-refresh/watch.py — Watch the sql/ folder for .sql files, apply them to the
world DB, then send the correct .reload commands to AzerothCore live.

Drop any .sql file into the watch_dir (default: ./sql/) and this script will:
  1. Apply it to MySQL
  2. Detect which tables were touched (via UPDATE/INSERT/DELETE/REPLACE statements)
  3. Send the matching .reload command(s) via SOAP
  4. Move the file to sql/done/ so it isn't reprocessed

Usage:
  pip install mysql-connector-python watchdog
  python watch.py
"""

import json
import re
import shutil
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_db_connection(cfg):
    try:
        import mysql.connector
    except ImportError:
        raise SystemExit(
            "mysql-connector-python not installed.\n"
            "Run:  pip install mysql-connector-python watchdog"
        )
    m = cfg["mysql"]
    return mysql.connector.connect(
        host=m["host"],
        port=int(m["port"]),
        user=m["user"],
        password=m["password"],
        database=m["database"],
        autocommit=True,
    )


def apply_sql_file(cfg, sql_path):
    """Execute all statements in a SQL file against the world DB."""
    sql = sql_path.read_text(encoding="utf-8", errors="replace")
    conn = get_db_connection(cfg)
    cur = conn.cursor()
    # Split on semicolons, skip empty/comment-only lines
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    executed = 0
    for stmt in statements:
        # Skip pure comment blocks
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
        clean = "\n".join(lines).strip()
        if clean:
            cur.execute(clean)
            executed += 1
    conn.close()
    return executed


def detect_tables(sql_path):
    """
    Parse a SQL file and return all table names that are written to.
    Matches UPDATE, INSERT INTO, REPLACE INTO, DELETE FROM.
    """
    sql = sql_path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r"(?:UPDATE|INSERT\s+(?:IGNORE\s+)?INTO|REPLACE\s+(?:INTO\s+)?|DELETE\s+FROM)\s+`?(\w+)`?",
        re.IGNORECASE,
    )
    tables = set(pattern.findall(sql))
    return tables


def send_reloads(cfg, tables):
    """Fire .reload commands for every matched table."""
    from reload import soap_command, extract_result

    reload_map = cfg.get("reload_map", {})
    reloaded = set()

    for tbl in tables:
        if tbl in reload_map:
            cmd = reload_map[tbl]
            if cmd not in reloaded:
                print(f"  -> {cmd}")
                try:
                    result = soap_command(cfg, cmd)
                    print(f"     {extract_result(result)}")
                except RuntimeError as e:
                    print(f"     SOAP error: {e}")
                reloaded.add(cmd)

    if not reloaded:
        print(f"  No reload mappings for tables: {tables}")
        print(f"  Add entries to reload_map in config.json if needed.")


def process_file(cfg, sql_path):
    done_dir = sql_path.parent / "done"
    done_dir.mkdir(exist_ok=True)

    print(f"\n[{sql_path.name}] Detected")

    # Detect tables before applying (file still intact)
    tables = detect_tables(sql_path)
    print(f"  Tables touched: {tables or '(none detected)'}")

    # Apply SQL
    try:
        count = apply_sql_file(cfg, sql_path)
        print(f"  Applied {count} statement(s) to DB")
    except Exception as e:
        print(f"  ERROR applying SQL: {e}")
        error_dir = sql_path.parent / "errors"
        error_dir.mkdir(exist_ok=True)
        shutil.move(str(sql_path), str(error_dir / sql_path.name))
        return

    # Send reloads
    send_reloads(cfg, tables)

    # Move to done/
    dest = done_dir / sql_path.name
    if dest.exists():
        dest = done_dir / f"{sql_path.stem}_{int(time.time())}{sql_path.suffix}"
    shutil.move(str(sql_path), str(dest))
    print(f"  Moved to {dest.relative_to(Path(__file__).parent)}")


def main():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        raise SystemExit(
            "watchdog not installed.\n"
            "Run:  pip install mysql-connector-python watchdog"
        )

    cfg = load_config()
    watch_dir = Path(__file__).parent / cfg.get("watch_dir", "sql")
    watch_dir.mkdir(exist_ok=True)

    print(f"Watching {watch_dir} for .sql files...")
    print(f"Worldserver SOAP: {cfg['soap']['host']}:{cfg['soap']['port']}")
    print(f"World DB: {cfg['mysql']['database']}@{cfg['mysql']['host']}")
    print("Drop a .sql file to apply it live. Ctrl+C to stop.\n")

    # Process any leftover files from before we started
    for existing in sorted(watch_dir.glob("*.sql")):
        process_file(cfg, existing)

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory and event.src_path.endswith(".sql"):
                # Small delay to ensure the file is fully written
                time.sleep(0.3)
                process_file(cfg, Path(event.src_path))

        def on_moved(self, event):
            if not event.is_directory and event.dest_path.endswith(".sql"):
                time.sleep(0.3)
                process_file(cfg, Path(event.dest_path))

    observer = Observer()
    observer.schedule(Handler(), str(watch_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("\nStopped.")


if __name__ == "__main__":
    main()
