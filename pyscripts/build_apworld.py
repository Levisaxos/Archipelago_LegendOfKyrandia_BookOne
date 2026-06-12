"""Package apworld/kyrandia/ into apworld/kyrandia.apworld (a zip).

Run from anywhere; paths resolve relative to the repo root.
"""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG_DIR = os.path.join(REPO, "apworld")
PKG = "kyrandia"
OUT = os.path.join(PKG_DIR, "kyrandia.apworld")


def build() -> str:
    src = os.path.join(PKG_DIR, PKG)
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _dirnames, filenames in os.walk(src):
            if "__pycache__" in dirpath:
                continue
            for fn in filenames:
                if fn.endswith(".pyc"):
                    continue
                abs_path = os.path.join(dirpath, fn)
                # Archive path uses the package folder as root: kyrandia/...
                arc = os.path.relpath(abs_path, PKG_DIR).replace(os.sep, "/")
                z.write(abs_path, arc)
    return OUT


if __name__ == "__main__":
    out = build()
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    print(f"wrote {out} ({len(names)} files)")
    for n in names:
        print("  ", n)
