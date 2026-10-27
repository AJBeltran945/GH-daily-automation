
import logging
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Project configuration
BASE_DIR = Path(__file__).resolve().parent
ENTRIES_DIR = BASE_DIR / "entries"
LOG_FILE = BASE_DIR / "logs" / "automation.log"

MIN_COMMITS = 5
MAX_COMMITS = 10

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)


def run_git(*args):
    """Execute a Git command in the project directory."""
    return subprocess.run(
        ["git", *args],
        cwd=BASE_DIR,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )


def create_entry(number):
    """Create a uniquely named daily entry."""
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")

    filename = f"entry_{timestamp}_{number:02d}.md"
    filepath = ENTRIES_DIR / filename

    content = (
        f"# Automated Entry {number}\n\n"
        f"- Created: {now.isoformat()}\n"
        f"- Entry number: {number}\n"
        "- Purpose: Test of the daily Git automation.\n"
    )

    # Exclusive creation prevents accidental overwriting.
    with filepath.open("x", encoding="utf-8") as file:
        file.write(content)

    return filepath


def main():
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)

    count = random.randint(MIN_COMMITS, MAX_COMMITS)
    successful = 0

    logging.info("Starting run: target is %s commits", count)

    for number in range(1, count + 1):
        try:
            filepath = create_entry(number)

            # Stage only the new entry, not unrelated files.
            relative_path = filepath.relative_to(BASE_DIR).as_posix()
            run_git("add", "--", relative_path)

            message = f"chore: add automated entry {number}"

            run_git("commit", "-m", message)

            # Push the new commit to the current branch.
            run_git("push")

            successful += 1
            logging.info("Committed and pushed %s", relative_path)

        except (OSError, subprocess.SubprocessError) as error:
            logging.exception(
                "Entry %s failed: %s", number, error
            )
            break

    logging.info(
        "Run finished: %s/%s commits pushed",
        successful,
        count,
    )

    print(f"Finished: {successful}/{count} commits pushed.")


if __name__ == "__main__":
    main()
