import json,base64,subprocess,urllib.request,sys,os
P="studio-9101802118-8c9a8"; D=os.path.dirname(os.path.abspath(__file__)); OUT=sys.argv[1]
def tok(): return subprocess.check_output("gcloud auth print-access-token",shell=True).decode().strip()
def post(url,body):
    r=urllib.request.Request(url,json.dumps(body).encode(),{"Authorization":"Bearer "+tok(),"Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:1500]); raise
def b64(p): return base64.b64encode(open(p,"rb").read()).decode()
STYLE="2D hand-drawn cartoon, Owl Family style: warm gold and bronze owls with soft painted shading, clean ink outlines, big round circuit-pattern teal eyes, navy-blue shadows, cozy storybook look, flat 2D animation, not 3D, not photoreal, no text, no logos, 9:16 vertical, full-bleed, no borders."
CAST=("Characters, keep IDENTICAL to references 2 and 3 (same 2D painted style): GRAM PA = older grey-silver owl, round thin gold wire glasses, brown knit cardigan sweater, ALWAYS clearly visible and identical in every image. "
 "MOMMA OWL = golden-tan owl, round gold glasses, ALWAYS wearing a soft CREAM knit cardigan. "
 "NICKY = 15-year-old teen OWL (beak, feathers, owl face, NOT a human), headphones with bright ORANGE rims worn around his neck in EVERY image, ALWAYS wearing his teal hoodie. "
 "MORGAN = exactly the owl in reference 1 (golden AI owl in a gold coin-rim circle on dark navy, glowing teal circuit eyes); he appears ONLY on a phone screen when described. "
 "DEVICE RULE: any phone or tablet has its SCREEN facing the character who is using it and its plain BACK facing everyone else; the camera only sees a screen when shooting over the user's shoulder. Never draw a character looking at the back of their own device. Whenever the BACK of a phone or tablet is visible, it shows ONLY a small simple Cyber Owl coin logo (reference 4: bronze coin with a circuit owl) centered like a device maker logo, rim text too small to read; never an Apple or any other brand logo. Reference 4 is ONLY that small device logo, not a character or prop in the scene. Only the characters named in the scene appear. No floating badges or emblems. Phones and tablets are plain, no brand logos, no readable text on screens. Coins are generic with no readable dates, names or numbers. ")
S={
"shot1":"Medium close-up, cozy warm kitchen. Momma Owl stands at the kitchen counter holding a tablet up in front of her: the tablet SCREEN faces Momma and its BACK (with the small Cyber Owl coin logo) faces the camera, while she looks off-screen to her right with a warm, playful smile, mid-sentence.",
"shot2":"Medium shot, slight low angle, cozy kitchen doorway. Nicky stands alone, empty wings (no phone, no devices), head tilted, wings half-shrugged, skeptical puzzled face, orange-rimmed headphones around neck.",
"shot3":"Two-shot in the kitchen, over Nicky's shoulder (we see the back of his head, teal hood and the orange-rimmed headphones around his neck; his wings are empty, no phone) toward Momma Owl, who chuckles and gestures enthusiastically with one wing.",
"shot4":"Solo close-up: ONLY Nicky in frame, nobody else, hands empty, in the kitchen, leaning toward camera with wide excited eyes and a huge goofy toothy grin, wings raised eagerly.",
"shot5":"TWO-CHARACTER SHOT, EXACTLY TWO OWLS IN THE WHOLE IMAGE: Gram Pa (grey owl, brown cardigan) on the right and Nicky (teen owl, teal hoodie, orange-rimmed headphones) on the left foreground seen from behind his shoulder. There is NO golden adult owl, NO Momma, nobody standing in the background; the background is an empty dusty wooden attic with a sunbeam. Gram Pa sits on the floor beside an open old military footlocker of generic coins, proudly holding one coin up. Nicky aims a plain black phone at the coin; the screen faces Nicky (visible over his shoulder), the back faces Gram Pa.",
"shot6":"Extreme close-up insert shot: the frame is filled by a plain black phone screen held in one feathered wing; no owl faces in frame except Morgan on screen. Phone in Nicky's feathered wing in the attic. On screen: Morgan (exactly reference 1) in the upper part, beside a simple catalog card with blank grey placeholder bars and three green checkmarks, a small blurred coin photo thumbnail. No readable text or numbers.",
"shot7":"Close-up of Momma Owl back in the warm kitchen, smiling knowingly and giving a crisp wink directly at the camera.",
}
REFS=["r_morgan_avatar.jpg","prev_shot4.jpg","prev_shot2.jpg","r_cyberowl.jpg"]
os.makedirs(OUT+"/stills",exist_ok=True)
url=f"https://aiplatform.googleapis.com/v1/projects/{P}/locations/global/publishers/google/models/gemini-2.5-flash-image:generateContent"
for k,v in S.items():
    if len(sys.argv)>2 and k not in sys.argv[2:]: continue
    parts=[]
    for i,r in enumerate(REFS): parts+=[{"text":f"Reference {i+1}:"},{"inlineData":{"mimeType":"image/jpeg","data":b64(os.path.join(D,r))}}]
    parts.append({"text":"Create ONE new illustration. "+CAST+"Scene: "+v+" Style: "+STYLE})
    res=post(url,{"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"9:16"}}})
    for p in res["candidates"][0]["content"]["parts"]:
        if "inlineData" in p: open(f"{OUT}/stills/{k}.png","wb").write(base64.b64decode(p["inlineData"]["data"])); print("saved",k)
