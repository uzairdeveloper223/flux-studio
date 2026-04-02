# flux-studio

One-command ComfyUI setup for FLUX.1-dev on Google Colab, with the Flux Super Realism LoRA pre-loaded.

## Getting Started with Google Colab

1. **Go to Colab:** Open [colab.research.google.com](https://colab.research.google.com/) and create a new notebook.
2. **Enable the T4 GPU:** Go to **Runtime** → **Change runtime type**, select **T4 GPU** under Hardware accelerator, and click **Save**.
3. **Open the terminal:** Look at the bottom left of your screen on desktop.

Run this command in the terminal:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/uzairdeveloper223/flux-studio/main/install.sh)
```

The script downloads `run_comfyui.py` and `workflow.json`, then starts ComfyUI. A Cloudflare public URL is printed when the server is ready.

## How it works

`run_comfyui.py` handles everything in sequence:

1. Clones or updates ComfyUI from the official repo
2. Installs ComfyUI-Manager and ComfyUI-GGUF custom nodes
3. Downloads the FLUX.1-dev GGUF model (~9 GB), T5-XXL encoder (~4 GB), CLIP-L, VAE, and the Super Realism LoRA — skipping files already on disk
4. Copies `workflow.json` into ComfyUI's workflow browser
5. Starts a Cloudflare tunnel and prints the public URL
6. Launches ComfyUI

The workflow uses a single LoRA (`strangerzonehf/Flux-Super-Realism-LoRA`) at 0.75 strength. Start prompts with `Super Realism, RAW photo` to activate it.

## Requirements

- Google Colab with a T4 GPU (free tier works)
- No other setup needed — the script installs everything

## Generated images

Images are saved to `/content/ComfyUI/output/` during the session. Download them before the session ends — Colab does not persist `/content/` across sessions.

## Project structure

```
flux-studio/
├── install.sh        one-command installer
├── run_comfyui.py    setup and launch script
└── workflow.json     ComfyUI workflow with Super Realism LoRA
```

## Limitations

- The free Colab T4 has 15.6 GB VRAM. Generation at 768×1024 takes roughly 30–60 seconds per image.
- The session and all downloaded models are lost when Colab disconnects. The script re-downloads only what is missing on each run, but on a fresh session this means re-downloading ~14 GB.
- Google Colab free-tier sessions idle-disconnect after about 90 minutes of inactivity.

## Author

Uzair Mughal — [uzair.is-a.dev](https://uzair.is-a.dev) — contact@uzair.is-a.dev

## License

MIT
