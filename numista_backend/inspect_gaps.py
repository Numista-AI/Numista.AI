import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
fs = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

coins_ref = fs.collection('users').document('jseaman1204@gmail.com').collection('coins')
all_coins = list(coins_ref.stream())
gaps = [c for c in all_coins if not (c.to_dict().get('image_url_obverse') or '').strip()]

print(f'Remaining gaps: {len(gaps)}')
print()
for coin in sorted(gaps, key=lambda c: c.to_dict().get('Program/Series','') or ''):
    d = coin.to_dict()
    ref    = str(d.get('Personal Ref #', '') or '')
    year   = str(d.get('Year', '') or '')
    series = str(d.get('Program/Series', '') or '(blank)')
    denom  = str(d.get('Denomination', '') or '')
    theme  = str(d.get('Theme/Subject', '') or '')
    print(f"  Ref#{ref:>6}  {year:<6}  {series:<40}  {denom:<20}  {theme}")
