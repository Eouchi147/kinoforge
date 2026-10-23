"""seats.py: on the runner, before any model is called: which model fills each role, does it exist on OpenRouter today,
what does it cost. Logs the table, writes <job>/seats.json and puts the chosen model per role in status.json.

    python3 films/director/seats.py films/studio/<id>

Paid mode (default): the roles of config.json `paid_seats` (writer, checker, coder, coder2, repair, eyes, crew), each a
fixed, ordered list of models chosen for the job (not a live ranking); ids missing from the live list are skipped, and a
role whose models are all missing falls back to the crew.json seat's live ranking. Free mode: films/director/free.py.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def paid():
    mk = C.agents.market(); out = {}
    if not mk: C.log('the OpenRouter model list could not be read: using the configured models as they are')
    for role, cfg in C.PAID.items():
        rows = []
        for m in cfg['models']:
            p = mk.get(m)
            rows.append({'model': m, 'live': bool(p) if mk else None, 'in_per_m': round(p['in'], 3) if p else None, 'out_per_m': round(p['out'], 3) if p else None,
                         'images': ('image' in p['mods']) if p else None})
        chain = C.role_models(role)
        if mk and not any(r['live'] for r in rows):
            chain = C.agents.seat(cfg['seat']); C.log(f'role {role}: none of {cfg["models"]} is live; falling back to the {cfg["seat"]} seat: {chain[:3]}')
        out[role] = {'chain': chain, 'models': rows}
        C.log(f'role {role:8s} -> {chain[0] if chain else "NONE"}   ' + '; '.join(
            f"{r['model']} {'live' if r['live'] else ('MISSING' if r['live'] is False else '?')}"
            + (f" ${r['in_per_m']}/{r['out_per_m']} per M" if r['in_per_m'] is not None else '') for r in rows))
    if 'eyes' in out and mk and out['eyes']['chain'] and not ('image' in (mk.get(out['eyes']['chain'][0]) or {}).get('mods', ['image'])):
        C.log('WARNING: the first eyes model does not take images')
    return out


def main(d):
    d = os.path.abspath(d.rstrip('/'))
    if C.FREE_ONLY:
        import runpy; sys.argv = ['free.py', d]; runpy.run_path(os.path.join(C.HERE, 'free.py'), run_name='__main__'); return
    roles = paid()
    json.dump({'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'mode': 'paid', 'roles': roles}, open(os.path.join(d, 'seats.json'), 'w'), indent=1)
    st = C.read_status(d)
    C.set_status(d, st.get('stage') or 'script', st.get('state') or 'queued', st.get('message') or 'Seats chosen.',
                 outputs={'seats': {r: (v['chain'][0] if v['chain'] else None) for r, v in roles.items()}})


if __name__ == '__main__':
    main(sys.argv[1])
