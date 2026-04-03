# flux-studio

One-command ComfyUI setup for FLUX.1-dev on Google Colab and Kaggle, with the UltraRealistic Amateur V2 LoRA pre-loaded. The installer auto-detects which platform you're on.

## Getting Started

### Google Colab (Recommended)

The easiest way to run Flux Studio is to use the pre-configured Colab notebook. It will automatically request a T4 GPU and setup the environment for you.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/uzairdeveloper223/flux-studio/blob/main/flux-studio.ipynb)

<details>
<summary><b>Kaggle (Click to expand)</b></summary>
<br>

1. Open [kaggle.com/code](https://www.kaggle.com/code) and create a new notebook.
2. **Enable GPU:** Go to **Settings** → **Accelerator** → select **GPU T4x2**.
3. **Enable Internet:** Toggle **Internet** to **ON** in the settings.
4. **Run this command** in a code cell:

```python
!bash <(wget -qO- https://raw.githubusercontent.com/uzairdeveloper223/flux-studio/main/install.sh)
```

5. **Stop Kaggle from disconnecting you:** Kaggle will pause the notebook if you are inactive. To prevent this, open your browser's Developer Console (F12 or Ctrl+Shift+I) and paste this script to fake mouse movements:

```javascript
setInterval(() => {
    window.dispatchEvent(new MouseEvent('mousemove', {
        bubbles: true,
        clientX: Math.random() * 100,
        clientY: Math.random() * 100
    }));
}, 20000);
```

**Important:** Do not close the Kaggle tab while generating, or the server will stop!

</details>

The script downloads the runner and workflow, then starts ComfyUI. A Cloudflare public URL is printed when the server is ready.

## How it works

The runner script handles everything in sequence:

1. Clones or updates ComfyUI from the official repo
2. Installs ComfyUI-Manager and ComfyUI-GGUF custom nodes
3. Downloads the FLUX.1-dev GGUF model (~9 GB), T5-XXL encoder (~4 GB), CLIP-L, VAE, and the UltraRealistic Amateur V2 LoRA — skipping files already on disk
4. Copies `workflow.json` into ComfyUI's workflow browser
5. Starts a Cloudflare tunnel and prints the public URL
6. Launches ComfyUI

The workflow uses a single LoRA (`UltraRealistic Amateur V2` by Danrisi) at 1.0 strength. Start prompts with `Low-resolution, amateur photo shot on digital camera, no visible jpeg artifacts, slightly noisy` to activate it.

## Platform comparison

| | Google Colab (free) | Kaggle (free) |
|--|--|--|
| GPU | 1x T4 (15.6 GB VRAM) | 2x T4 (16 GB each) |
| RAM | ~12 GB | ~29 GB |
| GPU quota | daily limit (varies) | 30 hours/week |
| Internet | on by default | must enable manually |
| Output path | `/content/ComfyUI/output/` | `/kaggle/working/ComfyUI/output/` |

Both platforms lose all files when the session ends. Download your images before disconnecting.

## Project structure

```
flux-studio/
├── install.sh              auto-detects Colab vs Kaggle
├── run_comfyui.py          Colab runner
├── run_comfyui_kaggle.py   Kaggle runner (internet check, dual-GPU handling)
└── workflow.json           ComfyUI workflow with UltraRealistic Amateur V2 LoRA
```

## Limitations

- Generation at 768x1024 takes roughly 30-60 seconds per image on a T4.
- Models are ~14 GB total. On a fresh session they must be re-downloaded, which takes a few minutes.
- Sessions idle-disconnect after about 90 minutes of inactivity (Colab) or when quota runs out (Kaggle).

## Author

Uzair Mughal — [uzair.is-a.dev](https://uzair.is-a.dev) — contact@uzair.is-a.dev

## License

MIT
