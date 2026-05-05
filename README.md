# flux-studio

One-command ComfyUI setup for **FLUX.1-dev** on Google Colab and Kaggle, with the **UltraRealistic Amateur V2** LoRA by [Danrisi](https://civitai.com/models/796382) pre-loaded and ready to generate.

The installer auto-detects which platform you're on and handles everything — models, nodes, tunnels, the works.

---

## Quick Start

### Google Colab (Recommended)

Click the badge, wait for the tunnel URL, generate.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/uzairdeveloper223/flux-studio/blob/main/flux-studio.ipynb)

> Free T4 GPU · ~14 GB models downloaded on first run · Cloudflare tunnel for UI access

<details>
<summary><b>Kaggle setup (click to expand)</b></summary>
<br>

> **Warning:** Kaggle aggressively kills UI tunnels. Sessions drop the moment you open the Cloudflare URL in many cases. **Use Colab if you can.** Kaggle is here as a fallback for when your Colab GPU quota runs out.

1. Go to [kaggle.com/code](https://www.kaggle.com/code) → create a new notebook.
2. **Settings → Accelerator → GPU T4x2**
3. **Settings → Internet → ON**
4. Run in a code cell:

```python
!bash <(wget -qO- https://raw.githubusercontent.com/uzairdeveloper223/flux-studio/main/install.sh)
```

5. Paste the keep-alive script in your browser console (F12) to stop Kaggle from disconnecting you:

```javascript
function keepAlive() {
    let event = new KeyboardEvent('keydown', { key: 'Shift', code: 'ShiftLeft', bubbles: true });
    document.body.dispatchEvent(event);
    document.body.click();
}
setInterval(keepAlive, 20000);
```

Keep the Kaggle tab open while generating — closing it kills the server.

</details>

Once the server is up, a public URL is printed. Open it to access ComfyUI.

---

## What Gets Installed

The runner handles everything in order:

1. Clones / updates ComfyUI from the official repo
2. Installs ComfyUI-Manager and ComfyUI-GGUF custom nodes
3. Downloads all required model files (skips anything already cached):
   - FLUX.1-dev GGUF Q5_K_S — ~7.7 GB
   - T5-XXL text encoder Q4_K_S — ~2.6 GB
   - CLIP-L — ~246 MB
   - VAE — ~335 MB
   - UltraRealistic Amateur V2 LoRA — ~2 GB
4. Copies `workflow.json` into ComfyUI's workflow browser
5. Starts a Cloudflare (Colab) or Pinggy (Kaggle) tunnel and prints the URL
6. Launches ComfyUI

---

## Platform Comparison

| | Google Colab (free) | Kaggle (free) |
|---|---|---|
| GPU | 1× T4 (15.6 GB VRAM) | 2× T4 (16 GB each) |
| RAM | ~12 GB | ~29 GB |
| Weekly GPU quota | Daily limit (varies) | 30 hrs/week |
| Tunnel | Cloudflare (stable) | Pinggy (fragile) |
| Output path | `/content/ComfyUI/output/` | `/kaggle/working/ComfyUI/output/` |

Both platforms wipe all files when the session ends. Download your images before disconnecting.

---

## The LoRA — UltraRealistic Amateur V2

Made by **Danrisi**, trained on 1048 images spanning a wide range of quality gradations — from clean mobile shots to grainy digital camera photos. The V2 brings better anatomy (especially hands), improved stability, and the ability to dial in quality level purely through prompting rather than needing a wall of trigger words.

The pre-loaded workflow uses the LoRA at **strength 1.0** with Danrisi's own recommended settings.

For a full prompting guide — trigger phrases, quality tiers, sampler settings, and what to tweak when things go wrong — see [PROMPTING.md](./PROMPTING.md).

---

## Gallery

Some examples generated out of the box with the pre-loaded workflow and no prompt changes.

![Example 1](assets/ComfyUI_00001_.png)
![Example 2](assets/ComfyUI_00002_.png)
![Example 3](assets/ComfyUI_00003_.png)

---

## Project Structure

```
flux-studio/
├── install.sh                  detects Colab vs Kaggle, fetches the right runner
├── run_comfyui.py              Colab runner
├── run_comfyui_kaggle.py       Kaggle runner (internet check, dual-GPU handling)
├── workflow.json               ComfyUI workflow with UltraRealistic Amateur V2
├── flux-studio.ipynb           Colab notebook (one-click)
├── PROMPTING.md                Full prompting guide for the LoRA + FLUX
└── assets/                     Gallery images
```

---

## Known Limitations

- Generation at 768×1024 takes roughly 30–60 seconds per image on a T4.
- Models are ~14 GB total. Fresh sessions re-download them — expect a few minutes on first run.
- Colab sessions idle-disconnect after ~90 minutes of inactivity.
- Complex lighting scenes and extreme poses can still produce anatomy issues — see PROMPTING.md for fixes.

---

## Author

Uzair Mughal — [uzair.is-a.dev](https://uzair.is-a.dev) — contact@uzair.is-a.dev

LoRA by [Danrisi](https://civitai.com/models/796382) — support them on [Ko-fi](https://ko-fi.com/danrisi).

## License

MIT — see [LICENSE](./LICENSE)