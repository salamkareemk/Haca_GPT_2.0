import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

req = urllib.request.Request(
    'http://localhost:5000/api/chat',
    method='POST',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'message': 'Who is the Tech School Faculty? List all of them.'}).encode()
)
try:
    r = urllib.request.urlopen(req, timeout=60)
    d = json.loads(r.read().decode())
    print('A:', d.get('answer', ''))
    print('Sources:', d.get('sources', []))
except Exception as e:
    print('Error:', e)
