import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def ask(q):
    req = urllib.request.Request(
        'http://localhost:5000/api/chat',
        method='POST',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'message': q}).encode()
    )
    r = urllib.request.urlopen(req, timeout=60)
    d = json.loads(r.read().decode())
    conf = round(d.get('confidence', 0) * 100)
    print("Q:", q)
    print("Confidence:", str(conf) + "%")
    print("Sources:", d.get('sources', []))
    print("A:", d.get('answer', '')[:600])
    print("-" * 60)

ask("Who is the CEO of HACA?")
ask("Tell me about the Python Django course")
ask("Who are the mentors for Python Django course?")
ask("What is the fee structure for Python Django course?")
