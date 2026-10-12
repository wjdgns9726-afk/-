"""대사마다 아이 같은 목소리 mp3를 만듭니다. (GitHub Actions 배포 때 실행)

Microsoft Edge 신경망 음성(edge-tts)으로 읽은 뒤, ffmpeg로 음높이와 목소리 결(포먼트)을
함께 올려 어린아이·동물 친구 목소리처럼 만듭니다.

사용법: python make_voices.py lines.json ../voices
"""
import asyncio, hashlib, json, os, subprocess, sys, tempfile

import edge_tts

SUNHI, INJOON = "ko-KR-SunHiNeural", "ko-KR-InJoonNeural"

# voice: 기본 음성, pitch/rate: edge-tts 조절값, shift: 음높이+포먼트를 함께 올리는 배율(1.0 = 그대로)
VOICES = {
    "rabbit":  dict(voice=SUNHI,  pitch="+12Hz", rate="+4%",  shift=1.22),
    "bear":    dict(voice=INJOON, pitch="+8Hz",  rate="-8%",  shift=1.12),
    "dog":     dict(voice=SUNHI,  pitch="+6Hz",  rate="+8%",  shift=1.18),
    "cat":     dict(voice=SUNHI,  pitch="+16Hz", rate="+0%",  shift=1.22),
    "penguin": dict(voice=SUNHI,  pitch="+0Hz",  rate="+2%",  shift=1.2),
    "lion":    dict(voice=INJOON, pitch="+4Hz",  rate="-4%",  shift=1.1),
    "minjun":  dict(voice=SUNHI,  pitch="-10Hz", rate="-4%",  shift=1.18),
    "seoa":    dict(voice=SUNHI,  pitch="+6Hz",  rate="-2%",  shift=1.24),
    "jiho":    dict(voice=SUNHI,  pitch="-16Hz", rate="+0%",  shift=1.16),
    "teacher": dict(voice=SUNHI,  pitch="+0Hz",  rate="-6%",  shift=1.0),
}


def speakable(text):
    # 말풍선용 기호는 빼고 읽힙니다.
    return text.replace('"', "").replace("~", "")


async def make(text, out_path, v):
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.mp3")
        for attempt in range(4):
            try:
                await edge_tts.Communicate(speakable(text), v["voice"], rate=v["rate"], pitch=v["pitch"]).save(raw)
                break
            except Exception as e:  # 일시적인 네트워크 오류는 다시 시도
                if attempt == 3:
                    raise
                print(f"  retry ({e})")
                await asyncio.sleep(2 ** attempt)
        f = v["shift"]
        af = f"asetrate=24000*{f},aresample=24000,atempo={1 / f:.5f}," if f != 1.0 else ""
        af += "silenceremove=start_periods=1:start_threshold=-50dB"
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", af,
             "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", out_path],
            check=True,
        )


async def main(lines_path, out_dir):
    lines = json.load(open(lines_path, encoding="utf-8"))
    manifest = {}
    for cid, texts in lines.items():
        v = VOICES[cid]
        os.makedirs(os.path.join(out_dir, cid), exist_ok=True)
        manifest[cid] = {}
        for text in texts:
            key = json.dumps([text, v], ensure_ascii=False, sort_keys=True)
            name = f"{cid}/{hashlib.sha1(key.encode()).hexdigest()[:12]}.mp3"
            await make(text, os.path.join(out_dir, name), v)
            manifest[cid][text] = name
            print(f"{name}  {text}")
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
