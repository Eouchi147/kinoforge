"""status.py: set a job's status.json from the workflow (and commit it when KF_COMMIT=1).

    python3 films/director/status.py films/studio/<id> <stage> <state> "<message>" [key=value ...]

stage: script sound spec check eyes render reflect done; state: queued running done failed skipped.
key=value pairs are added to `outputs` (values that parse as JSON are stored as JSON).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

if __name__ == '__main__':
    d, stage, state, msg = sys.argv[1:5]
    outs = {}
    for kv in sys.argv[5:]:
        k, v = kv.split('=', 1)
        try: outs[k] = json.loads(v)
        except ValueError: outs[k] = v
    C.set_status(d, stage, state, msg, outputs=outs or None)
