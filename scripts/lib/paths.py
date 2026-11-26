"""Python twin of paths.mjs: locate offline tool binaries without using PATH or keys."""
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODE_MODULES = ROOT / "node_modules"
VENDOR_LIB = ROOT / "vendor" / "bin" / "lib" / "lib"


def _exists(value):
    return bool(value) and Path(value).exists()


def python_bin():
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]
    local = ROOT / ".venv" / "bin" / "python"
    if local.exists():
        return str(local)
    return shutil.which("python3") or "python3"


def ffmpeg_bin():
    for var in ("FFMPEG_PATH", "HYPERFRAMES_FFMPEG_PATH"):
        if _exists(os.environ.get(var)):
            return os.environ[var]
    candidates = [
        NODE_MODULES / "@ffmpeg-installer" / "linux-x64" / "ffmpeg",
        ROOT / "vendor" / "bin" / "ffmpeg",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    try:
        import imageio_ffmpeg
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if _exists(p):
            return p
    except Exception:
        pass
    return shutil.which("ffmpeg")


def ffprobe_bin():
    for var in ("FFPROBE_PATH", "HYPERFRAMES_FFPROBE_PATH"):
        if _exists(os.environ.get(var)):
            return os.environ[var]
    candidates = [
        NODE_MODULES / "@ffprobe-installer" / "linux-x64" / "ffprobe",
        ROOT / "vendor" / "bin" / "ffprobe",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return shutil.which("ffprobe")


def _extract_chromium_libs():
    """@sparticuz/chromium ships NSS/NSPR libs in a Brotli tarball; unpack offline."""
    if (VENDOR_LIB / "libnss3.so").exists():
        os.environ["LD_LIBRARY_PATH"] = f"{VENDOR_LIB}:{os.environ.get('LD_LIBRARY_PATH','')}"
        return True
    br = NODE_MODULES / "@sparticuz" / "chromium" / "bin" / "al2023.tar.br"
    if not br.exists():
        return False
    js = f"""
const fs=require('node:fs'),zlib=require('node:zlib');
const src={str(br)!r}, dst={str(ROOT / 'vendor' / 'bin' / 'al2023.tar')!r};
fs.mkdirSync(require('node:path').dirname(dst),{{recursive:true}});
fs.writeFileSync(dst,zlib.brotliDecompressSync(fs.readFileSync(src)));
"""
    subprocess.run(["node", "-e", js], check=True, capture_output=True, text=True)
    (ROOT / "vendor" / "bin" / "lib").mkdir(parents=True, exist_ok=True)
    with tarfile.open(ROOT / "vendor" / "bin" / "al2023.tar") as t:
        t.extractall(ROOT / "vendor" / "bin" / "lib")
    if (VENDOR_LIB / "libnss3.so").exists():
        os.environ["LD_LIBRARY_PATH"] = f"{VENDOR_LIB}:{os.environ.get('LD_LIBRARY_PATH','')}"
        return True
    return False


def chrome_bin():
    for var in ("HYPERFRAMES_BROWSER_PATH", "CHROME_PATH", "CHROMIUM_PATH"):
        if _exists(os.environ.get(var)):
            return os.environ[var]
    cached = "/tmp/chromium"
    if os.path.exists(cached):
        _extract_chromium_libs()
        return cached
    js = """
(async()=>{const c=(await import('@sparticuz/chromium')).default;console.log(await c.executablePath())})().catch(()=>{});
"""
    r = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, capture_output=True, text=True)
    p = (r.stdout or "").strip().splitlines()[-1] if (r.stdout or "").strip() else ""
    if _exists(p):
        _extract_chromium_libs()
        return p
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome", "chrome-headless-shell"):
        found = shutil.which(name)
        if found:
            return found
    return None


def hf_bin():
    for p in (NODE_MODULES / ".bin" / "hyperframes", NODE_MODULES / "hyperframes" / "bin" / "hyperframes.mjs"):
        if p.exists():
            return str(p)
    return shutil.which("hyperframes")


def run(cmd, check=True, capture=False, env=None):
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run([str(c) for c in cmd], check=check, text=True,
                          capture_output=capture, cwd=ROOT, env=full_env)


def probe_json(fp, path):
    if not fp:
        return {}
    r = subprocess.run([fp, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                       capture_output=True, text=True)
    if r.returncode:
        return {}
    import json
    return json.loads(r.stdout or "{}")
