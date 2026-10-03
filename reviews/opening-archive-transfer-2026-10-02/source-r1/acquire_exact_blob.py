"""Read one immutable Git blob; preserve bytes only. Never extract or execute it."""
import base64
import hashlib
import http.client
import json
import os
import pathlib
import re
import resource
import shutil
import signal
import ssl
import sys
import time

REPOSITORY = "evangjones99-gif/Roguelike-deckbuilder"
REF = "refs/heads/codex/lanternbound-production"
WORKFLOW = REPOSITORY + "/.github/workflows/recover-opening-evidence.yml@" + REF
BLOB_SHA1 = "f768057141601502417dc8e31ba7e9cf678b616b"
ARCHIVE_SHA256 = "8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8"
ARCHIVE_BYTES = 5085419
ARCHIVE_NAME = "evidence-" + ARCHIVE_SHA256 + ".tar.gz"
API_PATH = "/repos/" + REPOSITORY + "/git/blobs/" + BLOB_SHA1
API_URL = "https://api.github.com" + API_PATH
RESPONSE_CAP = 8 * 1048576
RECEIPT_CAP = 4096
OUTPUT_CAP = ARCHIVE_BYTES + RECEIPT_CAP


def require(condition):
    if not condition:
        raise ValueError("Exact immutable transfer requirement failed")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def expired(_signal, _frame):
    raise TimeoutError("Whole transfer deadline")


def write_fresh(directory, name, body):
    fd = os.open(directory / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as output:
        require(output.write(body) == len(body))
        output.flush()
        os.fsync(output.fileno())


def main():
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1048576, 128 * 1048576))
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_FSIZE, (ARCHIVE_BYTES, ARCHIVE_BYTES))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(60)
    started = time.monotonic()
    require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY)
    require(os.environ.get("GITHUB_REF") == REF)
    require(os.environ.get("GITHUB_WORKFLOW_REF") == WORKFLOW)
    require(os.environ.get("GITHUB_EVENT_NAME") in ("push", "workflow_dispatch"))
    commit = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None)
    require(re.fullmatch(r"[0-9]{1,20}", run_id) is not None)
    require(re.fullmatch(r"[0-9]{1,6}", attempt) is not None)
    temporary = pathlib.Path(os.environ["RUNNER_TEMP"])
    require(temporary.is_absolute() and temporary.is_dir() and not temporary.is_symlink())
    require(shutil.disk_usage(temporary).free >= 32 * 1048576)
    directory = temporary / ("opening-evidence-" + run_id + "-" + attempt)
    # Token is exposed only to this step and a fixed authenticated HTTPS GET.
    # No redirects/proxy handlers, arbitrary URL, shell interpolation or log of errors/headers.
    token = os.environ.pop("GITHUB_TOKEN", "")
    require(0 < len(token) <= 4096 and "\r" not in token and "\n" not in token)
    connection = http.client.HTTPSConnection("api.github.com", 443, timeout=10, context=ssl.create_default_context())
    try:
        connection.request("GET", API_PATH, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "hollowpact-exact-opening-evidence-transfer",
            "Accept-Encoding": "identity",
        })
        response = connection.getresponse()
        require(response.status == 200)  # 3xx refused, never followed.
        require(response.getheader("Content-Type", "").split(";", 1)[0].strip() == "application/json")
        require(response.getheader("Content-Encoding", "identity") == "identity")
        declared = response.getheader("Content-Length")
        if declared is not None:
            require(declared.isdecimal() and 0 < int(declared) <= RESPONSE_CAP)
        raw = bytearray()
        while True:
            chunk = response.read(min(65536, RESPONSE_CAP - len(raw) + 1))
            if not chunk:
                break
            require(len(raw) + len(chunk) <= RESPONSE_CAP)
            raw.extend(chunk)
        if declared is not None:
            require(len(raw) == int(declared))
        response_bytes = len(raw)
        payload = json.loads(raw, object_pairs_hook=unique_object)
        del raw
    finally:
        connection.close()
        token = ""
    require(isinstance(payload, dict))
    require(payload.get("sha") == BLOB_SHA1 and payload.get("size") == ARCHIVE_BYTES)
    require(payload.get("encoding") == "base64" and payload.get("url") == API_URL)
    encoded = payload.get("content")
    require(isinstance(encoded, str) and 0 < len(encoded) <= RESPONSE_CAP)
    encoded = encoded.replace("\n", "")  # Only GitHub's LF wrapping is permitted.
    require(len(encoded) == ((ARCHIVE_BYTES + 2) // 3) * 4)
    body = base64.b64decode(encoded, validate=True)
    del payload, encoded
    require(len(body) == ARCHIVE_BYTES)
    blob_hash = hashlib.sha1(b"blob " + str(ARCHIVE_BYTES).encode("ascii") + b"\0" + body).hexdigest()
    archive_hash = hashlib.sha256(body).hexdigest()
    require(blob_hash == BLOB_SHA1 and archive_hash == ARCHIVE_SHA256)
    directory.mkdir(mode=0o700, exist_ok=False)  # New directory/inode; no historical path restoration.
    write_fresh(directory, ARCHIVE_NAME, body)
    del body
    digest = hashlib.sha256()
    count = 0
    with (directory / ARCHIVE_NAME).open("rb") as archive:
        while chunk := archive.read(65536):
            count += len(chunk)
            require(count <= ARCHIVE_BYTES)
            digest.update(chunk)
    require(count == ARCHIVE_BYTES and digest.hexdigest() == ARCHIVE_SHA256)
    receipt = {
        "status": "EXACT_IMMUTABLE_ARCHIVE_BYTES_VERIFIED_ONLY",
        "repository": REPOSITORY, "ref": REF, "workflowCommit": commit,
        "runID": run_id, "runAttempt": attempt,
        "blobSHA1": blob_hash, "archiveSHA256": archive_hash, "archiveBytes": count,
        "apiJSONBytes": response_bytes, "apiResponseCapBytes": RESPONSE_CAP,
        "wholeSecondsBeforeReceipt": time.monotonic() - started,
        "wholeDeadlineSeconds": 60, "cpuSecondsCap": 20, "addressSpaceCapBytes": 128 * 1048576,
        "outputCapBytes": OUTPUT_CAP, "diskFreeFloorBytesBeforeTransfer": 32 * 1048576,
        "fullStoredArchiveSHA256Readback": True, "extractedOrExecutedArchive": False,
        "historicalFilesystemMetadataRestored": False,
        "qualification": "Byte transfer only; no runtime/build/gameplay/art/default/fun acceptance. Transport ZIP/hosted artifact lifetime are external. Official upload action resources are governed by job/step timeout, not this Python process limit.",
    }
    receipt_body = (json.dumps(receipt, separators=(",", ":")) + "\n").encode("utf-8")
    require(len(receipt_body) <= RECEIPT_CAP)
    require(ARCHIVE_BYTES + len(receipt_body) <= OUTPUT_CAP)
    write_fresh(directory, "VERIFICATION.json", receipt_body)
    require(sorted(p.name for p in directory.iterdir()) == sorted([ARCHIVE_NAME, "VERIFICATION.json"]))
    require(sum(p.stat().st_size for p in directory.iterdir()) <= OUTPUT_CAP)
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    require(time.monotonic() - started < 60)
    signal.alarm(0)
    print("Exact immutable opening archive bytes verified; no archive execution.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # No traceback, token, HTTP error body, response headers or arbitrary server text.
        print("Immutable opening evidence transfer refused.", file=sys.stderr)
        sys.exit(1)
