#!/usr/bin/env python3

import os
import re
import sys
import signal
import shutil
import subprocess
import threading
import time
from pathlib import Path


WORKSPACE = Path("/kaggle/working/ComfyUI")
COMFYUI_PORT = 8188

_MODEL_SPECS: list[tuple[str, str, Path, str | None]] = [
    (
        "FLUX.1-dev GGUF Q4_K_S (~9 GB)",
        "https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_K_S.gguf",
        WORKSPACE / "models" / "unet",
        None,
    ),
    (
        "T5-XXL encoder Q4_K_S (~4 GB)",
        "https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/resolve/main/t5-v1_1-xxl-encoder-Q4_K_S.gguf",
        WORKSPACE / "models" / "clip",
        None,
    ),
    (
        "CLIP-L",
        "https://huggingface.co/f5aiteam/CLIP/resolve/main/clip_l.safetensors",
        WORKSPACE / "models" / "clip",
        None,
    ),
    (
        "VAE",
        "https://huggingface.co/f5aiteam/VAE/resolve/main/ae.safetensors",
        WORKSPACE / "models" / "vae",
        None,
    ),
    (
        "LoRA — UltraRealistic Amateur V2",
        "https://civitai.com/api/download/models/890545?type=Model&format=SafeTensor",
        WORKSPACE / "models" / "loras",
        "another_amateur_lora.safetensors",
    ),
]

_WORKFLOW_MAP: dict[str, str] = {
    "workflow.json": "flux_ultra_realistic.json",
}

_SUPPRESS_PATTERNS: tuple[str, ...] = (
    "FETCH ComfyRegistry Data",
    "FETCH DATA from",
    "## ComfyUI-Manager:",
    "[ComfyUI-Manager]",
    "### ",
    "** ",
    "[START]",
    "[DONE]",
    "Prestartup times",
    "seconds: /kaggle/",
    "seconds: /usr/",
    "Import times for custom nodes",
    "Total VRAM",
    "pytorch version:",
    "xformers version:",
    "Python version:",
    "ComfyUI version:",
    "comfy-aimdo version:",
    "comfy-kitchen version:",
    "ComfyUI frontend version:",
    "ComfyUI-GGUF:",
    "WARNING: You need pytorch",
    "Requirement already satisfied",
    "Using Python 3.",
    "Checked ",
    "Restoring [",
    "Install: pip",
    "skip black listed",
    "Starting server",
    "To see the GUI go to",
    "Prompt executed in",
    "Asset seeder",
    "[W]",
    "warnings.warn",
    "UserWarning",
    "FutureWarning",
    "DeprecationWarning",
    "Found comfy_kitchen backend",
    "aimdo: src/control",
    "working around nvidia",
    "Using async weight",
    "Enabled pinned memory",
    "Set vram state",
    "DynamicVRAM",
    "cudaMallocAsync",
    "xformers attention",
    "Checkpoint files will",
    "comfy-aimdo inited",
    "[Prompt Server]",
    "Context impl",
    "Will assume non-transactional",
)

_ERROR_PATTERNS: tuple[str, ...] = (
    "ERROR",
    "Error:",
    "error:",
    "Exception",
    "Traceback",
    "CUDA out of memory",
)

_STARTUP_COMPLETE = "[ComfyUI-Manager] All startup tasks have been completed."
_TUNNEL_URL_RE = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")


def _say(msg: str) -> None:
    print(f"  {msg}", flush=True)


def _run_silent(cmd: str | list[str], cwd: Path | None = None, fatal: bool = True) -> None:
    proc = subprocess.Popen(
        cmd,
        shell=isinstance(cmd, str),
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    while proc.poll() is None:
        print(".", end="", flush=True)
        time.sleep(3)
    print(flush=True)
    if fatal and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)


def _download(url: str, dest_dir: Path, filename: str | None = None) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = str(dest_dir / filename) if filename else None
    cmd = (
        f'wget -q --show-progress -c "{url}" -O "{dest}"'
        if dest
        else f'wget -q --show-progress -c "{url}" -P "{dest_dir}"'
    )
    subprocess.run(cmd, shell=True, check=True)


def _is_cached(dest_dir: Path, filename: str | None, url: str) -> bool:
    name = filename if filename else url.split("/")[-1]
    candidate = dest_dir / name
    return candidate.exists() and candidate.stat().st_size > 1_000


def _detect_gpus() -> list[int]:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True,
        )
        return [int(idx.strip()) for idx in result.stdout.strip().split("\n") if idx.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def _check_internet() -> None:
    try:
        subprocess.run(
            ["wget", "-q", "--spider", "https://huggingface.co", "--timeout=5"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        _say("ERROR: internet is disabled")
        _say("enable it in the Kaggle sidebar: Settings -> Internet -> ON")
        _say("then restart the notebook session")
        sys.exit(1)


def _setup_comfyui() -> None:
    if not WORKSPACE.exists():
        _say("cloning ComfyUI ...")
        subprocess.run(
            f"git clone https://github.com/comfyanonymous/ComfyUI {WORKSPACE}",
            shell=True, check=True,
        )
    else:
        _run_silent("git pull", cwd=WORKSPACE)

    _say("installing Python requirements ...")
    _run_silent(
        "pip install -q xformers!=0.0.18 -r requirements.txt "
        "--extra-index-url https://download.pytorch.org/whl/cu121 "
        "--extra-index-url https://download.pytorch.org/whl/cu118",
        cwd=WORKSPACE,
    )

    manager_dir = WORKSPACE / "custom_nodes" / "ComfyUI-Manager"
    if not manager_dir.exists():
        _say("installing ComfyUI-Manager ...")
        _run_silent(f"git clone https://github.com/ltdrdata/ComfyUI-Manager {manager_dir}")
    else:
        _run_silent("git pull", cwd=manager_dir)

    for script in (
        "check.sh", "scan.sh",
        "node_db/dev/scan.sh",
        "scripts/install-comfyui-venv-linux.sh",
    ):
        p = manager_dir / script
        if p.exists():
            p.chmod(0o755)

    gguf_dir = WORKSPACE / "custom_nodes" / "ComfyUI-GGUF"
    if not gguf_dir.exists():
        _say("installing ComfyUI-GGUF ...")
        _run_silent(f"git clone https://github.com/city96/ComfyUI-GGUF {gguf_dir}")
        _run_silent(f"pip install -q -r {gguf_dir}/requirements.txt")

    _run_silent(
        f"python {WORKSPACE}/custom_nodes/ComfyUI-Manager/cm-cli.py restore-dependencies",
        cwd=WORKSPACE,
        fatal=False,
    )

    _say("setup complete")


def _download_models() -> None:
    total = len(_MODEL_SPECS)
    for idx, (label, url, dest_dir, filename) in enumerate(_MODEL_SPECS, 1):
        prefix = f"[{idx}/{total}]"
        if _is_cached(dest_dir, filename, url):
            _say(f"{prefix} cached    {label}")
        else:
            _say(f"\n  {prefix} downloading  {label} ...")
            _download(url, dest_dir, filename)
            _say(f"{prefix} done")


def _install_workflows(script_dir: Path) -> None:
    workflow_dir = WORKSPACE / "user" / "default" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name in _WORKFLOW_MAP.items():
        src = script_dir / src_name
        if src.exists():
            shutil.copy2(src, workflow_dir / dest_name)
            _say(f"workflow  {src_name} -> {dest_name}")
        else:
            _say(f"warning: {src_name} not found, skipping")


def _install_cloudflared() -> None:
    cf_bin = Path("/tmp/cloudflared")
    if shutil.which("cloudflared") or cf_bin.exists():
        return
    _say("installing cloudflared ...")
    subprocess.run(
        f'wget -q -O {cf_bin} '
        'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64',
        shell=True, check=True,
    )
    cf_bin.chmod(0o755)
    _say("cloudflared ready")


def _start_tunnel() -> None:
    cf_bin = "/tmp/cloudflared" if Path("/tmp/cloudflared").exists() else "cloudflared"
    cf = subprocess.Popen(
        [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{COMFYUI_PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    for raw in cf.stdout:
        m = _TUNNEL_URL_RE.search(raw.decode("utf-8", errors="replace"))
        if m:
            url = m.group(0)
            print(f"\n\n  {'─' * 56}")
            print(f"  ready        {url}")
            print(f"  workflow     Browse Workflows -> flux_ultra_realistic")
            print(f"  output       {WORKSPACE / 'output' }/")
            print(f"  {'─' * 56}")
            print("  stop the session manually when done.\n")
            return


def _is_suppressed(line: str) -> bool:
    return any(pattern in line for pattern in _SUPPRESS_PATTERNS)


def _is_error(line: str) -> bool:
    return any(pattern in line for pattern in _ERROR_PATTERNS)


def _launch_comfyui(gpu_ids: list[int]) -> None:
    env = os.environ.copy()
    if len(gpu_ids) > 1:
        env["CUDA_VISIBLE_DEVICES"] = "0"
        _say(f"detected {len(gpu_ids)} GPUs — pinning ComfyUI to GPU 0")

    proc = subprocess.Popen(
        [sys.executable, "main.py", "--dont-print-server", "--highvram"],
        cwd=str(WORKSPACE),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
        start_new_session=True,
    )

    in_fetch = False
    tunnel_started = False

    for raw_line in proc.stdout:
        line = raw_line.rstrip()

        if "FETCH ComfyRegistry Data:" in line:
            m = re.search(r"(\d+)/(\d+)", line)
            if m:
                cur, total = int(m.group(1)), int(m.group(2))
                filled = int(28 * cur / total)
                bar = "█" * filled + "░" * (28 - filled)
                print(f"\r  plugins  [{bar}] {cur}/{total}", end="", flush=True)
                in_fetch = True
            continue

        if in_fetch:
            print("  done", flush=True)
            in_fetch = False

        if _STARTUP_COMPLETE in line:
            _say("loaded")
            if not tunnel_started:
                tunnel_started = True
                threading.Thread(target=_start_tunnel, daemon=True).start()
            continue

        if _is_error(line):
            _say(f"error  {line}")
            continue

        if _is_suppressed(line):
            continue

        if line.strip():
            _say(line)

    proc.wait()


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    print()
    _say("=== ComfyUI + FLUX Super Realism (Kaggle) ===\n")

    _say("step 1/5  checking internet")
    _check_internet()
    _say("internet ok")

    gpu_ids = _detect_gpus()
    gpu_label = f"{len(gpu_ids)}x GPU" if gpu_ids else "no GPU"
    _say(f"hardware   {gpu_label}, {_get_ram_gb()} GB RAM\n")

    if not gpu_ids:
        _say("ERROR: no GPU detected")
        _say("enable GPU in Kaggle sidebar: Settings -> Accelerator -> GPU T4x2")
        sys.exit(1)

    _say("step 2/5  setup")
    _setup_comfyui()

    _say("\nstep 3/5  models")
    _download_models()

    _say("\nstep 4/5  workflows")
    _install_workflows(Path(__file__).parent.resolve())

    _say("\nstep 5/5  launching")
    _install_cloudflared()
    _say("loading models into GPU memory — this takes a minute ...\n")
    _launch_comfyui(gpu_ids)


def _get_ram_gb() -> int:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) // 1_048_576
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    main()
