import json,base64,subprocess,time,urllib.request,sys,os
P="studio-9101802118-8c9a8"; D=os.path.dirname(os.path.abspath(__file__))
OUT=sys.argv[1]; STEP=sys.argv[2]
def tok(): return subprocess.check_output("gcloud auth print-access-token",shell=True).decode().strip()
def post(url,body):
    r=urllib.request.Request(url,json.dumps(body).encode(),{"Authorization":"Bearer "+tok(),"Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=600))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:1500]); raise
def b64(p): return base64.b64encode(open(p,"rb").read()).decode()
STYLE="2D hand-drawn cartoon, Owl Family style: warm gold and bronze owls with soft painted shading, clean ink outlines, big round circuit-pattern teal eyes, navy-blue shadows, cozy storybook look, flat 2D animation, not 3D, not photoreal, no text, no logos, 9:16 vertical."
CAST=("Characters (keep identical in every image): GRAM PA = older grey-silver owl, round thin gold wire glasses, brown knit cardigan, teal circuit-pattern eyes (from reference 4, but redrawn 2D). "
 "MOMMA OWL = golden-tan owl, round gold glasses, leaf pattern on her wing (reference 2, redrawn 2D). "
 "NICKY = teen golden owl, black headphones around his neck, teal hoodie (reference 3, redrawn 2D, no game items). "
 "MORGAN = the exact owl from reference 1 (golden AI owl inside a gold coin-rim circle on dark navy, glowing teal circuit eyes). "
 "Morgan must NOT appear anywhere except inside a phone screen when a phone screen is described; no floating badges, emblems, medallions or logos in the scene. Nicky is an OWL with a beak, feathers and owl face, not a human child. Full-bleed image, no borders or frames. Render everything in the flat 2D painted style of reference 1, NOT the 3D style of references 2-4. ")
STILLS={
"shot1":"Wide shot, dusty wooden attic, a sunbeam through a small window. Gram Pa, Momma Owl and Nicky gather around an open wooden chest full of generic old coins with no readable dates or numbers. Gram Pa holds one coin up, puzzled.",
"shot2":"Medium two-shot in the same attic. Nicky (teen owl, beak, feathers) holds a plain black smartphone with no logo toward Gram Pa; the screen glows soft teal. Momma Owl leans in behind them. Coin chest partly visible.",
"shot3":"Over-the-shoulder close-up from behind Gram Pa's grey shoulder: his grey wing holds a plain black smartphone; Morgan (exactly as reference 1, inside the gold coin rim) fills the phone screen, smiling. Attic softly blurred behind.",
"shot4":"Medium-wide shot in the attic. Gram Pa, Momma Owl and Nicky look together at a plain black phone held by Gram Pa, smiling warmly; the open coin chest in the foreground.",
}
MOTION={
"shot1":"Slow push-in on the family around the open coin chest. Gram Pa tilts the coin in the sunbeam and scratches his head with one wing. Dust motes drift. Nobody else moves much. Camera: static wide, gentle dolly in.",
"shot2":"Nicky turns the phone toward Gram Pa and the screen lights up with soft teal glow. Gram Pa leans forward, eyebrows raised. One action only. Camera: locked medium shot, eye level.",
"shot3":"On the phone screen, Morgan pops in with a small bounce, blinks his glowing teal circuit eyes, and gives a friendly one-wing salute. Gram Pa's wing holding the phone stays still. Camera: static close-up over Gram Pa's shoulder.",
"shot4":"The three owls lean in toward the glowing phone, then Gram Pa smiles and nods slowly. Sunbeam stays steady. Camera: slow pull-back from medium to medium-wide.",
}
REFS=["r_morgan_avatar.jpg","r_momma_owl.jpg","son_crop.jpg","panel3_grampa.jpg"]
if STEP=="stills":
    os.makedirs(OUT+"/stills",exist_ok=True)
    url=f"https://aiplatform.googleapis.com/v1/projects/{P}/locations/global/publishers/google/models/gemini-2.5-flash-image:generateContent"
    for k,v in STILLS.items():
        if len(sys.argv)>3 and k not in sys.argv[3:]: continue
        parts=[{"text":f"Reference {i+1}:"} for i in range(0)]
        for i,r in enumerate(REFS):
            parts+= [{"text":f"Reference {i+1}:"},{"inlineData":{"mimeType":"image/jpeg","data":b64(os.path.join(D,r))}}]
        parts.append({"text":"Create ONE new illustration. "+CAST+"Scene: "+v+" Style: "+STYLE+" Do not include any text, numbers, watermarks or the storyboard number."})
        res=post(url,{"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"9:16"}}})
        print(k,"usage",res.get("usageMetadata"))
        for p in res["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                open(f"{OUT}/stills/{k}.png","wb").write(base64.b64decode(p["inlineData"]["data"])); print("saved",k)
if STEP=="veo":
    os.makedirs(OUT+"/Veo",exist_ok=True)
    M="veo-3.1-fast-generate-001"; base=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{P}/locations/us-central1/publishers/google/models/{M}"
    ops={}
    for k in STILLS:
        if len(sys.argv)>3 and k not in sys.argv[3:]: continue
        body={"instances":[{"prompt":MOTION[k]+" "+STYLE+" Keep characters exactly as in the start image.","image":{"bytesBase64Encoded":b64(f"{OUT}/stills/{k}.png"),"mimeType":"image/png"}}],
              "parameters":{"aspectRatio":"9:16","durationSeconds":6,"sampleCount":1,"generateAudio":False,"resolution":"720p","negativePrompt":"3D render, photorealistic, text, logos, extra characters"}}
        ops[k]=post(base+":predictLongRunning",body)["name"]; print(k,ops[k])
    while ops:
        time.sleep(15)
        for k in list(ops):
            r=post(base+":fetchPredictOperation",{"operationName":ops[k]})
            if r.get("done"):
                del ops[k]
                if "error" in r: print(k,"ERR",r["error"]); continue
                vids=r["response"].get("videos",[]); print(k,"filtered",r["response"].get("raiMediaFilteredCount"))
                for v in vids: open(f"{OUT}/Veo/{k}.mp4","wb").write(base64.b64decode(v["bytesBase64Encoded"])); print("saved",k)
