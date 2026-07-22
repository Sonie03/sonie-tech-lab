"""
Applause / celebration sound player for DevBuddy AI.
Uses winsound (stdlib, zero dependencies) to play a WAV file.
Falls back silently if unavailable.
"""
import threading
import os

# Path to bundled applause WAV (generated programmatically if missing)
_SOUND_DIR  = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
_CLAP_PATH  = os.path.join(_SOUND_DIR, "applause.wav")


def _generate_beep_wav(path: str):
    """
    Generate a simple celebratory multi-tone WAV file using only stdlib.
    Writes a 1-second chord (440 Hz + 554 Hz + 659 Hz) at 22050 Hz, 16-bit mono.
    """
    import struct, math, wave
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sample_rate = 22050
    duration    = 1.2          # seconds
    num_samples = int(sample_rate * duration)
    freqs       = [440, 554, 659, 880]   # A4 chord

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            # Mix tones with gentle fade-out envelope
            envelope = max(0.0, 1.0 - t / duration)
            val = sum(math.sin(2 * math.pi * f * t) for f in freqs)
            val = int((val / len(freqs)) * 28000 * envelope)
            wf.writeframes(struct.pack("<h", val))


def play_applause():
    """Play the applause/celebration sound in a daemon thread (non-blocking)."""
    def _play():
        try:
            import winsound
            if not os.path.exists(_CLAP_PATH):
                _generate_beep_wav(_CLAP_PATH)
            winsound.PlaySound(_CLAP_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"[Sound] Could not play applause: {e}")

    threading.Thread(target=_play, daemon=True).start()
