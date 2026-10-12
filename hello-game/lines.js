// 캐릭터와 대사. 게임(index.html)과 목소리 파일 생성기(tools/)가 같이 씁니다.
(function(root){
"use strict";

const CHARS = [
  {id:"rabbit", name:"토끼",  kind:"rabbit",  fur:"#ffffff", inner:"#ffc2d1", group:"animal", pitch:1.5},
  {id:"bear",   name:"곰돌이", kind:"bear",    fur:"#b98458", inner:"#e7b98f", belly:"#f1d3b3", group:"animal", pitch:0.9},
  {id:"dog",    name:"멍멍이", kind:"dog",     fur:"#f5deb3", ear:"#a0673e", group:"animal", pitch:1.3},
  {id:"cat",    name:"야옹이", kind:"cat",     fur:"#ffb366", inner:"#ffd1dc", group:"animal", pitch:1.5},
  {id:"penguin",name:"펭귄",  kind:"penguin", fur:"#2d3142", belly:"#fff", group:"animal", pitch:1.3},
  {id:"lion",   name:"사자",  kind:"lion",    fur:"#ffcf5c", mane:"#d9822b", belly:"#fff1c9", group:"animal", pitch:0.95},
  {id:"minjun", name:"민준",  kind:"kid", style:"boy",  hair:"#3b2a20", shirt:"#5cc8a8", group:"kid", pitch:1.6},
  {id:"seoa",   name:"서아",  kind:"kid", style:"girl", hair:"#4a2e22", shirt:"#ff8fab", ribbon:"#ffd34d", pants:"#8a6bd1", group:"kid", pitch:1.7},
  {id:"jiho",   name:"지호",  kind:"kid", style:"boy",  hair:"#1f1a17", shirt:"#ffb84d", skin:"#f6d2b2", pants:"#3b7bbf", group:"kid", pitch:1.55},
  {id:"teacher",name:"선생님", kind:"kid", style:"teacher", hair:"#5a3a2a", shirt:"#9ec5ff", pants:"#5b4a8a", group:"teacher", pitch:1.15, teacher:true},
];

// 미리 녹음된 목소리 파일은 이 이름 기준으로 만들어집니다.
const DEFAULT_KID = "도빈";

/* 한국어 조사 */
const hasFinal = s => { const c = s.charCodeAt(s.length-1); return c>=0xAC00 && c<=0xD7A3 && (c-0xAC00)%28 !== 0; };
const voc = n => n ? n + (hasFinal(n) ? "아" : "야") : "";          // 도빈아 / 서아야
const iya = n => n + (hasFinal(n) ? "이야" : "야");                    // 펭귄이야 / 토끼야
const subj = n => n ? n + (hasFinal(n) ? "이" : "") : "우리 친구";     // 도빈이

// good은 여러 개 중 하나를 골라 말합니다.
function linesFor(c, kid){
  const k = kid ? voc(kid) + " " : "";
  if(c.teacher){
    const who = c.photo ? c.name : "선생님";
    return {
      intro: `${k}안녕~! ${who}이야. 반가워!`,
      ask:   `${who}한테 "안녕하세요~" 해볼까?`,
      retry: `괜찮아~ 작은 목소리도 좋아. "안녕하세요~"`,
      wave:  `손 흔들어 줬구나! 고마워~ 이번엔 "안녕하세요~" 말해볼까?`,
      good:  [`와~ ${k}인사 정말 잘하네! ${who} 너무 기뻐!`, `우와~ ${subj(kid)} 씩씩하게 인사했네! 최고야!`, `반가워 ${k.trim()}~ 오늘도 재밌게 놀자!`],
      later: `괜찮아~ 다음에 또 인사하자. 손 흔들어줘서 고마워!`
    };
  }
  return {
    intro: `${k}안녕~! 나는 ${iya(c.name)}.`,
    ask:   `나한테도 "안녕~" 해줄래?`,
    retry: `괜찮아~ 작게 해도 돼. 같이 해보자, "안녕~"`,
    wave:  `손 흔들어 줬구나! 고마워~ 이번엔 "안녕~" 말해볼까?`,
    good:  [`와~ ${k}인사 정말 잘한다! 나도 반가워!`, `우와~ ${subj(kid)} 목소리 멋지다! 우리 친구하자!`, `안녕 안녕~ ${k}너랑 인사해서 너무 좋아!`, `${subj(kid)} 최고야! 인사해줘서 고마워~`],
    later: `괜찮아~ 다음에 또 인사하자. 안녕~!`
  };
}

const api = { CHARS, DEFAULT_KID, hasFinal, voc, iya, subj, linesFor };
if(typeof module !== "undefined" && module.exports) module.exports = api;
else root.HelloLines = api;
})(this);
