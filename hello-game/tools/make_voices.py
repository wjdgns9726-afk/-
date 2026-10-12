"""대사마다 아이 같은 목소리 mp3를 만듭니다. (GitHub Actions 배포 때 실행)

공개 한국어 음성 모델 Supertonic으로 읽은 뒤, ffmpeg로 음높이와 목소리 결(포먼트)을
함께 올려 어린아이·동물 친구 목소리처럼 만듭니다.

사용법: python make_voices.py lines.json ../voices
"""
import hashlib, json, os, subprocess, sys, tempfile

from supertonic import TTS

# voice: Supertonic 기본 목소리(F1~F5 여성, M1~M5 남성), speed: 말 빠르기,
# shift: 음높이+포먼트를 함께 올리는 배율(1.0 = 그대로, 클수록 어린 목소리)
VOICES = {
    "rabbit":  dict(voice="F2", speed=1.05, shift=1.22),
    "bear":    dict(voice="M1", speed=0.95, shift=1.18),
    "dog":     dict(voice="F4", speed=1.1,  shift=1.18),
    "cat":     dict(voice="F3", speed=1.0,  shift=1.24),
    "penguin": dict(voice="F5", speed=1.05, shift=1.2),
    "lion":    dict(voice="M2", speed=0.95, shift=1.15),
    "minjun":  dict(voice="F1", speed=1.0,  shift=1.2),
    "seoa":    dict(voice="F2", speed=1.0,  shift=1.26),
    "jiho":    dict(voice="F4", speed=1.0,  shift=1.17),
    "teacher": dict(voice="F1", speed=0.95, shift=1.0),
    # 사진으로 추가한 친구 (부모님이 고른 목소리)
    "photo-girl": dict(voice="F3", speed=1.0, shift=1.25),
    "photo-boy":  dict(voice="F5", speed=1.0, shift=1.17),
}


def speakable(text):
    # 말풍선용 기호는 빼고 읽힙니다.
    return text.replace('"', "").replace("~", "")


def main(lines_path, out_dir):
    lines = json.load(open(lines_path, encoding="utf-8"))
    tts = TTS(auto_download=True)
    sr = tts.sample_rate
    styles = {}
    manifest = {}
    with tempfile.TemporaryDirectory() as tmp:
        for cid, texts in lines.items():
            v = VOICES[cid]
            style = styles.get(v["voice"]) or styles.setdefault(v["voice"], tts.get_voice_style(voice_name=v["voice"]))
            os.makedirs(os.path.join(out_dir, cid), exist_ok=True)
            manifest[cid] = {}
            for text in texts:
                key = json.dumps([text, v], ensure_ascii=False, sort_keys=True)
                name = f"{cid}/{hashlib.sha1(key.encode()).hexdigest()[:12]}.mp3"
                wav, _ = tts.synthesize(speakable(text), voice_style=style, lang="ko",
                                        speed=v["speed"], total_steps=12)
                raw = os.path.join(tmp, "raw.wav")
                tts.save_audio(wav, raw)
                f = v["shift"]
                af = f"asetrate={sr}*{f},aresample=44100,atempo={1 / f:.5f}," if f != 1.0 else ""
                af += "silenceremove=start_periods=1:start_threshold=-50dB,loudnorm=I=-16:TP=-1.5"
                subprocess.run(
                    ["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", af,
                     "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k",
                     os.path.join(out_dir, name)],
                    check=True,
                )
                manifest[cid][text] = name
                print(f"{name}  {text}", flush=True)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
