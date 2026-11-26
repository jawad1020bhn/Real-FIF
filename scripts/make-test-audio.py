#!/usr/bin/env python3
"""Deterministic offline test audio (no ffmpeg, no downloads).
Generates a quiet 220 Hz tone with soft pulses at word starts so the pipeline has
a real WAV to mux. Used by `npm run reel -- --from-json ...` in an offline sandbox."""
import argparse, math, struct, wave

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--duration', type=float, default=10.4)
    ap.add_argument('--rate', type=int, default=16000)
    ap.add_argument('--pulses', default='0.2,0.66,1.22,1.9,3.3,3.76,4.44,4.96,6.4,7.2,7.88')
    a = ap.parse_args()
    pulses = [float(x) for x in a.pulses.split(',') if x.strip()]
    n = int(a.duration * a.rate)
    with wave.open(a.out, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(a.rate)
        buf = bytearray()
        for i in range(n):
            t = i / a.rate
            env = 0.035
            for p in pulses:
                d = t - p
                if 0 <= d < 0.22:
                    env += 0.11 * math.sin(math.pi * d / 0.22) ** 2
            s = int(max(-1.0, min(1.0, env * math.sin(2 * math.pi * 220 * t))) * 32767)
            buf += struct.pack('<h', s)
        f.writeframes(bytes(buf))
    print(f'wrote {a.out} ({a.duration}s, {a.rate} Hz mono)')

if __name__ == '__main__':
    main()
