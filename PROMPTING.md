# PROMPTING.md — Getting the Most Out of Flux Studio

A practical guide for prompting **FLUX.1-dev** with the **UltraRealistic Amateur V2** LoRA.
No fluff, just what actually works.

---

## How This LoRA Thinks

The UltraRealistic Amateur V2 was trained on 1048 images spanning multiple quality tiers — from crisp mobile phone shots to grainy digital camera photos from the 2000s. That range is the whole point. You're not locked into one aesthetic — you control the quality level entirely through your prompt text.

In V2 you don't need a pile of trigger words like V1 required. Pick a couple that match the look you're after and write a natural, descriptive prompt around them.

---

## Quality Trigger Phrases

These are the quality anchors baked into the training data. Start your prompt with whichever fits your target look.

### Gritty / Amateur Aesthetic
```
Low-resolution, amateur photo shot on digital camera, no visible jpeg artifacts, slightly noisy
```
This is the signature look — dynamic, imperfect, alive. Think candid street photography vibes.

### Clean / Mobile Shot
```
High-resolution photo, shot on a mobile phone, no visible artifacts, clear and sharp
```
Cleaner output, still grounded in realism rather than AI-smooth perfection.

### Cinematic / Dramatic (no quality prefix needed)
```
dramatic cinematic lighting, film grain, shallow depth of field
```
Skip the quality prefix entirely and lean on lighting/lens descriptors. The LoRA adapts.

### High Definition Studio
```
studio lighting, high resolution, professional photography
```
Forces the model toward the polished end of its quality range.

---

## Recommended ComfyUI Settings

These are straight from the creator (Danrisi) — use these as your baseline before tweaking anything.

| Parameter | Value |
|---|---|
| Sampler | `dpmpp_2m` |
| Scheduler | `beta` |
| Steps | `40` |
| CFG | `1` |
| Guidance | `2.5` |
| LoRA Strength | `1.0` (default) |
| Resolution | `768 × 1024` (portrait) or `1024 × 768` (landscape) |

The workflow.json in this repo already has all of these dialed in.

---

## LoRA Strength — When to Change It

**1.0** — Full effect. Default. Use this.

**0.87** — Drop here if hands start looking distorted or anatomy breaks. The LoRA has less influence so FLUX.1-dev's base knowledge fills in more.

**0.8** — More neutral. The LoRA's amateur aesthetic is subtler. Use when you want realism without the "candid camera" feel.

Going below 0.8 makes the LoRA almost pointless — you're just running base FLUX at that point.

---

## Prompt Structure That Works

FLUX.1-dev reads prompts like natural language — don't comma-spam keywords like you would for SD1.5. Write actual descriptive sentences. The model follows them well.

**Template:**
```
[Quality trigger phrase], [subject description], [environment], [lighting], [mood/style]
```

**Example — Portrait, amateur vibe:**
```
Low-resolution, amateur photo shot on digital camera, no visible jpeg artifacts, slightly noisy,
a young woman with dark curly hair, wearing a worn leather jacket, standing in a narrow alley at dusk,
warm orange streetlight from behind, candid expression, slightly motion-blurred background
```

**Example — Clean editorial:**
```
High-resolution photo, shot on a mobile phone, no visible artifacts, clear and sharp,
close-up portrait of a man in his 40s, grey stubble, intense blue eyes, against a plain white wall,
natural window light from the left, neutral expression
```

**Example — Cinematic scene:**
```
dramatic cinematic lighting, film grain, shallow depth of field,
a woman in a red coat walking through a foggy train station at night,
motion blur on moving figures in the background, teal and orange color grading
```

---

## What Each Part of Your Prompt Does

**Subject** — Be specific. Age, hair, clothing, expression. FLUX follows detailed subject descriptions accurately.

**Environment** — Outdoor/indoor, location type, time of day. Don't just say "city" — say "narrow Tokyo side street at 3am."

**Lighting** — This is huge for realism. Name your light source and direction. `warm golden hour side light`, `harsh overhead fluorescent`, `single candle from below`, etc.

**Mood/style** — `candid`, `editorial`, `surveillance camera aesthetic`, `90s disposable camera`, `lomography` — these all steer the LoRA meaningfully.

---

## Negative Prompt Tips

FLUX.1-dev doesn't use negative prompts natively the way SD1.5 does — but you can still use them in ComfyUI via a negative conditioning node. They help at the margins.

Useful negatives for realism:
```
cartoon, painting, illustration, 3d render, cgi, anime, watercolor, oil painting,
oversaturated, plastic skin, airbrushed, overly smooth, symmetrical face,
text, watermark, signature, blurry, out of focus (if sharpness is your goal)
```

If you *want* blur (bokeh, motion), don't put those in negatives obviously.

---

## Fixing Common Issues

**Hands look broken**
Drop LoRA strength to 0.87. Also add `detailed hands, correct anatomy` to your positive prompt. Generating at a slightly higher resolution (1024×1024) also helps FLUX render hands better.

**Face looks AI-smooth / plastic**
Add `pores, skin texture, natural imperfections, subsurface scattering` to your prompt. The LoRA is meant to produce lived-in faces — lean into it.

**Flashlight / blown-out lighting effect at night**
This is a known V1 issue, V2 improved it significantly. If it still appears, specify `no harsh flash, ambient light only, natural low light` in your prompt.

**Too much grain / noise**
Switch your quality trigger to the mobile phone variant or drop in `moderate grain, not overly noisy`. Or lower LoRA strength to 0.85.

**Output looks too AI / too clean**
The LoRA isn't fully activating. Make sure you're using a quality trigger phrase at the start. Also confirm the LoRA file loaded — check ComfyUI's node graph and verify `another_amateur_lora.safetensors` shows in the LoRA loader node.

**Composition is boring**
FLUX follows composition language well. Add things like: `rule of thirds`, `Dutch angle`, `low angle shot looking up`, `extreme close-up`, `wide establishing shot`. Treat it like you're directing a photographer.

---

## Quick Recipes

### Candid Street Portrait
```
Low-resolution, amateur photo shot on digital camera, no visible jpeg artifacts, slightly noisy,
candid shot of a person mid-laugh, street market background slightly out of focus,
natural afternoon light, documentary photography style, shot from hip level
```

### Moody Indoor Scene
```
Low-resolution, amateur photo shot on digital camera, slightly noisy,
a person sitting alone at a kitchen table late at night, single lamp casting warm light,
coffee mug, shadows on wall, quiet and melancholic atmosphere, candid
```

### Clean Fashion/Editorial
```
High-resolution photo, shot on a mobile phone, no visible artifacts, clear and sharp,
full-body shot of a woman in minimalist streetwear, plain concrete wall background,
flat even daylight, fashion editorial, confident pose
```

### Cinematic Action Freeze
```
dramatic cinematic lighting, film grain, motion blur,
a man running through rain-soaked streets at night, neon reflections on wet pavement,
dutch angle, teal shadows, orange highlights, 24mm wide lens
```

### Vintage / Lo-Fi
```
Low-resolution, amateur photo shot on digital camera, slight jpeg artifacts, grainy,
1990s aesthetic, faded colors, chromatic aberration, disposable camera flash,
group of friends at a house party, candid moment
```

---

## Resolution Guide

| Use Case | Width | Height |
|---|---|---|
| Portrait | 768 | 1024 |
| Landscape / scene | 1024 | 768 |
| Square / social | 1024 | 1024 |
| Widescreen / cinematic | 1280 | 720 |

Keep dimensions as multiples of 64. Going above 1280 on a T4 may OOM.

---

## Stacking Another LoRA

The workflow supports adding a second LoRA via the LoraLoader node chain. Good combos:

- **Flux-Super-Realism** (strangerzonehf) — add trigger word `Super Realism`, blend at 0.4–0.6 strength alongside UltraRealistic at 0.8. Pushes detail further.
- **Film grain LoRAs** — blend at low strength (0.3–0.5) to punch up the analog look.

When stacking, total effective LoRA influence adds up — lower each one individually to avoid over-cooking the output.

---

## Resources

- [UltraRealistic Amateur V2 on CivitAI](https://civitai.com/models/796382) — original model page, Danrisi's own usage notes
- [Support Danrisi on Ko-fi](https://ko-fi.com/danrisi) — they're working on a full fine-tuned checkpoint
- [FLUX.1-dev on HuggingFace](https://huggingface.co/black-forest-labs/FLUX.1-dev) — base model card and license info
- [ComfyUI Docs](https://docs.comfy.org) — node reference and workflow help