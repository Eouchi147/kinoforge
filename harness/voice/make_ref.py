"""make_ref.py JOB.json OUT.wav — a clean Kokoro reference clip of the job's narrator (runs in its own small venv)."""
import sys, json, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
job = json.load(open(sys.argv[1])); d = os.environ.get('KOKORO_DIR', 'models/kokoro')
k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
voice = job.get('kokoro_ref', 'bm_fable'); lang = 'en-gb' if voice.startswith('b') else 'en-us'
text = job.get('ref_text', "Long ago, when the hills were young, the lanterns of the valley were lit by hand, one by one, every single evening.")
s, sr = k.create(text, voice=voice, speed=0.92, lang=lang); sf.write(sys.argv[2], np.asarray(s, dtype=np.float32), sr); print('reference', sys.argv[2], len(s) / sr, 's')
