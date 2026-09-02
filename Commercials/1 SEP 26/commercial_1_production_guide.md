# Numista.AI — Cartoon Commercial #1: "The Footlocker & The V-Bucks"

## Production Strategy & Best Google Products

### 1. Primary Recommendation: **Google Veo 2 / VideoFX (Vertex AI & Google Labs)**
- **Why Google Veo**: Veo is Google DeepMind's flagship generative video model. It natively supports **Image-to-Video generation**, cinematic camera movements (push-in, orbit, zoom), character emotional performance (eye-rolls, winks, toothy grins), and high visual consistency.
- **Workflow**: Upload `morgan_avatar.png` (or Imagen 3 character turns) as the starting keyframe and run scene-by-scene prompts with cinematic tags.

### 2. Supporting Tool: **Google Imagen 3 (ImageFX / Vertex AI)**
- **Purpose**: Create character consistency turnarounds (Momma Owl, Nicky Owl with gaming headphones) before animating in Veo.

### 3. Voice & Audio: **Google Cloud Text-to-Speech (Journey & Studio Voices)**
- **Purpose**: Generate high-fidelity conversational character audio with natural speech cadence and emotional delivery.

---

## Character Model Prompts (Imagen 3 / ImageFX)

### Momma Owl
> `3D stylized character portrait of a friendly Momma Owl, Pixar animation style, warm golden-brown feathered plumage, big expressive glowing aquamarine eyes, subtle stylish reading spectacles resting on beak, perched comfortably in a warm cozy rustic-modern kitchen, soft studio lighting, ultra-detailed textures, matching the artistic style of morgan_avatar.png --ar 1:1`

### Nicky Owl (Age 15)
> `3D stylized character portrait of a 15-year-old teenage cartoon boy owl named Nicky, Pixar animation style, slightly scruffy golden-brown feathers, cool gaming headphones worn around his neck, big bright curious eyes, funny expressive adolescent grin, warm ambient room lighting, ultra-detailed feathers, matching the artistic style of morgan_avatar.png --ar 1:1`

---

## Shot-by-Shot Prompts for Google Veo (VideoFX / Vertex AI)

### Shot 1: The Pitch (Momma Owl)
- **Duration**: ~4 seconds
- **Camera**: Medium close-up, warm natural push-in
- **Veo Prompt**:
> `Cinematic 3D animation, Pixar style. A charming Momma Owl perched at a kitchen counter holding a tablet showing a coin app. She talks to her teenage son off-screen with a warm, playful expression, pausing to do a humorous, affectionate eye-roll. Warm golden kitchen lighting, crisp feather detail, fluid micro-expressions, 4k 24fps.`
- **Voiceover**:
> *(Momma)*: "I know you use AI to help with your homework... and I think it would be good for you to help Gram Pa organize that footlocker of old coins. It’d be fun for him to show you all the stuff he’s collected over the years!"

---

### Shot 2: The Teen Skepticism (Nicky)
- **Duration**: ~3 seconds
- **Camera**: Medium shot, slight low angle
- **Veo Prompt**:
> `Cinematic 3D animation, Pixar style. Nicky, a 15-year-old cartoon teenage owl with gaming headphones around his neck, looking puzzled. He tilts his head slightly and shrugs his wings skeptically while talking. Cozy wood-paneled room background, smooth fluid animation, 4k 24fps.`
- **Voiceover**:
> *(Nicky)*: "I don't think Gram Pa knows how to use AI, Ma..."

---

### Shot 3: The Solution (Momma Explains)
- **Duration**: ~3 seconds
- **Camera**: Two-shot / over-the-shoulder
- **Veo Prompt**:
> `Cinematic 3D animation, Pixar style. Momma owl chuckles warmly, shaking her head affectionately with a gentle smile. She makes an enthusiastic wing gesture explaining the concept. Warm vibrant lighting, high-end animation studio quality, 4k 24fps.`
- **Voiceover**:
> *(Momma)*: "No silly! He tells you all about the coin, and YOU enter it into Numista.AI for him!"

---

### Shot 4: The V-Bucks Angle (Nicky's Big Grin)
- **Duration**: ~3 seconds
- **Camera**: Dynamic close-up zoom
- **Veo Prompt**:
> `Cinematic 3D animation, Pixar style. Nicky the teenage owl suddenly perks up with wide excited glowing eyes, leaning forward with an enormous funny toothy grin and excited wing gestures, eagerly negotiating. High energy, comedy timing, 4k 24fps.`
- **Voiceover**:
> *(Nicky)*: "Oh, ok, that sounds cool! Can you get me some V-Bucks so I can buy this really cool new skin in Fortnite?!"

---

### Shot 5: The Deal & Outro (Momma's Wink & Logo Reveal)
- **Duration**: ~4 seconds
- **Camera**: Close-up on Momma Owl transitioning to spinning Coin Medallion Logo
- **Veo Prompt**:
> `Cinematic 3D animation. Momma owl smiles knowingly, giving a charming, crisp wink directly toward the camera. Smooth cinematic match-cut transition into the official Numista.AI Morgan Owl circular gold coin medallion avatar shining with glowing teal circuitry. Elegant 3D motion graphic end screen, 4k 24fps.`
- **Voiceover**:
> *(Momma)*: "Help Gram Pa first... and we'll see."
> *(Narrator / Brand Tag)*: "Numista.AI — Ancient wisdom meets modern AI. Start cataloging today."
