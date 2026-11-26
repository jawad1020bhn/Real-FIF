#!/usr/bin/env python3
"""Prefetch ASR + alignment weights ONCE on a machine with Hugging Face access.

No API keys / no tokens. Run outside this sandbox, then copy models/ (or point
HF_HOME at the cache). For a single speaker diarization is never used.
"""
import argparse, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', choices=['ar','en'], required=True)
    ap.add_argument('--model', default='large-v3')
    a = ap.parse_args()
    cache = os.path.join(os.path.dirname(__file__),'..','models')
    os.makedirs(cache, exist_ok=True)
    os.environ.setdefault('HF_HOME', cache)
    print(f'HF_HOME={os.environ["HF_HOME"]}')
    try:
        from huggingface_hub import snapshot_download
        if a.lang == 'ar':
            snapshot_download('jonatasgrosman/wav2vec2-large-xlsr-53-arabic')
            print('cached Arabic wav2vec2 alignment model')
        else:
            import torchaudio
            torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H.get_model()
            print('cached English torchaudio alignment model')
        snapshot_download(f'Systran/faster-whisper-{a.model}')
        print(f'cached faster-whisper {a.model}')
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {e}', file=sys.stderr)
        print('Hugging Face is blocked in some sandboxes. Run this on a normal machine,', file=sys.stderr)
        print('or use the offline --from-json path.', file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
