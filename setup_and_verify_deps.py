import subprocess
import sys
import os

REQUIRED = [
    ("earthengine-api", "ee"),
    ("aiohttp", "aiohttp"),
    ("Pillow", "PIL"),
    ("requests", "requests"),
    ("openai", "openai"),
]

def run(cmd):
    print("$", " ".join(cmd))
    return subprocess.run(cmd, check=True)

def ensure_pip():
    run([sys.executable, "-m", "pip", "--version"])

def install(packages):
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
    run(cmd)

def verify_import(module_name):
    code = f"import {module_name}; print('OK:{module_name}')"
    run([sys.executable, "-c", code])

def main():
    print("Python:", sys.executable)
    ensure_pip()
    # set proxy from environment if present
    for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if os.environ.get(k):
            print(f"env {k} = {os.environ.get(k)}")

    pkgs = [p for p, _ in REQUIRED]
    install(pkgs)

    print("\n=== Verify imports ===")
    for _, mod in REQUIRED:
        verify_import(mod)

    # Extra: minimal GEE init check (no auth popup here)
    try:
        import ee
        ee.Initialize(project='data-center-location-analysis')
        print("GEE Initialize OK")
    except Exception as e:
        print("GEE Initialize skipped/failed:", e)

if __name__ == "__main__":
    main()


