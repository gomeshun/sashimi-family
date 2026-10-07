"""Use the latest update, with a successful preceding run, to gate expensive CI."""

from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request


def revisions(event_name, event):
    if event_name == "pull_request":
        pull = event["pull_request"]
        # Initial/reopened PRs compare the whole proposal with their base.
        if event.get("action") != "synchronize":
            return pull["base"]["sha"], pull["head"]["sha"]
        return event.get("before"), pull["head"]["sha"]
    if event_name == "push":
        return event.get("before"), event.get("after")
    return None, None  # Manual runs always validate, regardless of changed paths.


def matches(path, patterns):
    return any(
        fnmatch.fnmatchcase(path, pattern)
        for pattern in patterns
        if "/" in pattern or "/" not in path
    )


def needs_validation(paths, patterns, preceding_succeeded):
    return paths is None or not patterns or any(matches(path, patterns) for path in paths) or not preceding_succeeded


def succeeded_before(revision, environment):
    """A docs-only commit must not hide a failed or still-running code check."""
    workflow = environment.get("GITHUB_WORKFLOW_REF", "").split("@", 1)[0].rsplit("/", 1)[-1]
    repository = environment.get("GITHUB_REPOSITORY", "")
    token = environment.get("CI_READ_TOKEN", "")
    if not workflow or not repository or not token:
        return False
    query = urllib.parse.urlencode(dict(head_sha=revision, status="success", per_page=100))
    url = (environment.get("GITHUB_API_URL", "https://api.github.com")
           + f"/repos/{repository}/actions/workflows/{urllib.parse.quote(workflow, safe='')}/runs?{query}")
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            runs = json.load(response)["workflow_runs"]
        # Dispatch may exercise a different job/profile (for example family
        # integration with component regressions skipped), so it cannot prove
        # that the automatic checks passed at this revision.
        return any(
            run["head_sha"] == revision and run["conclusion"] == "success"
            and run.get("event") in {"push", "pull_request"}
            for run in runs
        )
    except (OSError, ValueError, KeyError, urllib.error.URLError):
        return False  # Uncertain history runs the checks rather than skipping them.


def changed_paths(before, after):
    for revision in (before, after):
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision) or revision == "0" * 40:
            return None
        available = subprocess.run(["git", "cat-file", "-e", revision + "^{commit}"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if available.returncode:
            fetched = subprocess.run(["git", "fetch", "--no-tags", "--depth=1", "origin", revision],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if fetched.returncode:
                return None
    output = subprocess.check_output(["git", "diff", "--name-only", "-z", before, after])
    return output.decode("utf-8", errors="surrogateescape").rstrip("\0").split("\0") if output else []


def validated_merge_parent(after, environment):
    """A no-conflict merge need not repeat a successful PR's identical tree."""
    if not isinstance(after, str) or not re.fullmatch(r"[0-9a-f]{40}", after) or after == "0" * 40:
        return None
    commit = subprocess.check_output(["git", "cat-file", "-p", after], text=True)
    parents = [line.split()[1] for line in commit.split("\n\n", 1)[0].splitlines() if line.startswith("parent ")]
    if len(parents) < 2:
        return None
    for parent in parents[1:]:
        if changed_paths(parent, after) == [] and succeeded_before(parent, environment):
            return parent
    return None


def main():
    environment = os.environ
    event = json.loads(Path(environment["GITHUB_EVENT_PATH"]).read_text())
    before, after = revisions(environment["GITHUB_EVENT_NAME"], event)
    equivalent = validated_merge_parent(after, environment) if environment["GITHUB_EVENT_NAME"] == "push" else None
    if equivalent:
        before = equivalent
    patterns = [line.strip() for line in environment["CI_CHANGED_PATHS"].splitlines() if line.strip()]
    paths = changed_paths(before, after) if before else None
    relevant = paths is not None and any(matches(path, patterns) for path in paths)
    preceding_succeeded = bool(before and paths is not None and not relevant and succeeded_before(before, environment))
    changed = needs_validation(paths, patterns, preceding_succeeded)
    if not patterns or paths is None:
        reason = "manual/initial event or unavailable change history"
    elif relevant:
        reason = "relevant files changed"
    elif preceding_succeeded:
        reason = "identical merge tree already validated" if equivalent else "no relevant changes since the preceding successful run"
    else:
        reason = "preceding successful validation could not be confirmed"
    with Path(environment["GITHUB_OUTPUT"]).open("a") as stream:
        stream.write(f"changed={str(changed).lower()}\n")
    print(f"Run validation: {changed} ({reason})")


if __name__ == "__main__":
    main()
