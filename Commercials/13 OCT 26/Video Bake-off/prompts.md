# Numista.Ai Video Bake-off — "Morgan on the Phone" (30s script, shot 3 moment)
Test: same stills + same prompts in Grok Imagine and Google Veo (image-to-video, one clip per shot, edit together).
Judge: (1) character consistency, (2) action makes sense, (3) 2D Owl Family look holds.
Rules: one action per clip; no on-screen text from the generator (captions added in editor); no coin values/prices; no PII; no brand marks (no Apple logo); brand = "Numista.Ai".
Refs: morgan_avatar.png (style master), 1 SEP 26\Momma Owl.jpg, Son Owl.jpg, storyboard panel 3 (attic + chest).

## Shared STYLE block (append to every prompt)
2D hand-drawn cartoon, Owl Family style: warm gold and bronze owls with soft painted shading, clean ink outlines, big round circuit-pattern teal eyes, navy-blue shadows, cozy storybook look, flat 2D animation, not 3D, not photoreal, no text, no logos, 9:16 vertical.

## CAST block
Gram Pa: older grey-silver owl, round wire glasses, cardigan. Momma Owl: golden-tan owl, gold round glasses, leaf-pattern wing. Nicky: teen golden owl, headphones around neck, teal hoodie. Morgan: friendly golden AI owl inside a gold coin-rim circle on a dark navy background, glowing teal circuit eyes (match morgan_avatar.png exactly).

## Shot 1 — Attic discovery (6s)
Still: Wide shot, dusty attic, sunbeam through a small window. Gram Pa, Momma Owl and Nicky gather around an open wooden chest full of generic old coins (no readable dates or values). Gram Pa holds one coin up, puzzled.
Motion prompt: Slow push-in on the family around the open coin chest. Gram Pa tilts the coin in the sunbeam and scratches his head with one wing. Dust motes drift. Nobody else moves much. Camera: static wide, gentle dolly in. [STYLE]

## Shot 2 — Nicky offers the phone (5s)
Still: Medium two-shot. Nicky holds a plain black phone (no logo) toward Gram Pa; screen glows teal. Momma Owl leans in behind.
Motion prompt: Nicky turns the phone toward Gram Pa and the screen lights up with soft teal glow. Gram Pa leans forward, eyebrows raised. One action only. Camera: locked medium shot, eye level. [STYLE]

## Shot 3 — Morgan appears (5s) [hero shot]
Still: Over-the-shoulder close-up on the phone screen in Gram Pa's wing; Morgan (exact morgan_avatar.png look, inside gold coin rim) fills the screen.
Motion prompt: On the phone screen, Morgan pops in with a small bounce, blinks his glowing teal circuit eyes, and gives a friendly one-wing salute. Gram Pa's wing holding the phone stays still. Camera: static close-up over Gram Pa's shoulder. [STYLE]
Note: in final edit, composite the real morgan_avatar.png onto the screen if the generator drifts.

## Shot 4 — Family reacts (5s)
Still: Medium-wide, attic. Gram Pa, Momma Owl and Nicky look at the phone together, smiling; chest of coins in foreground.
Motion prompt: The three owls lean in toward the glowing phone, then Gram Pa smiles and nods slowly. Sunbeam stays steady. Camera: slow pull-back from medium to medium-wide. [STYLE]

## Veo settings (Vertex, when auth is restored)
model veo-3.1-fast-generate-001 (or lite), image-to-video, durationSeconds 5–6, aspectRatio 9:16, sampleCount 1, generateAudio false, no upscaling. One clip per still.
