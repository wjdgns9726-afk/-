// 목소리 파일로 만들 대사 목록을 JSON으로 출력합니다: { 캐릭터id: [대사, ...] }
const { CHARS, PHOTO_VOICES, DEFAULT_KID, linesFor } = require("../lines.js");
const out = {};
const photoFriends = PHOTO_VOICES.map(v => ({ id: v.id, photo: true, name: "" }));
for (const c of [...CHARS, ...photoFriends]) {
  const L = linesFor(c, DEFAULT_KID);
  out[c.id] = [...new Set([L.intro, L.ask, L.retry, L.wave, L.later, ...L.good])];
}
process.stdout.write(JSON.stringify(out, null, 2));
