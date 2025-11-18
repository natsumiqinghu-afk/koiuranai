const map = { A:1,B:2,C:3,D:4,E:5,F:6,G:7,H:8,I:9,
              J:1,K:2,L:3,M:4,N:5,O:6,P:7,Q:8,R:9,
              S:1,T:2,U:3,V:4,W:5,X:6,Y:7,Z:8 };

const meanings = {
  1:{title:"リーダーの数字",love:"情熱的で自信家",advice:"自分を信じて前進"},
  2:{title:"調和の数字",love:"優しい共感型",advice:"人を支えると運気UP"},
  3:{title:"創造の数字",love:"自由で明るい人気者",advice:"好奇心を大切に"},
  4:{title:"安定の数字",love:"誠実で堅実な恋",advice:"焦らず信頼を育てると良い"},
  5:{title:"冒険の数字",love:"刺激を求める恋愛",advice:"変化を恐れない"},
  6:{title:"愛の数字",love:"深く尽くすタイプ",advice:"依存しすぎ注意"},
  7:{title:"探求の数字",love:"神秘的な魅力",advice:"心を開くと安定"},
  8:{title:"豊かさの数字",love:"頼られる力強い恋",advice:"情で動くと吉"},
  9:{title:"完成の数字",love:"包容力のある恋愛",advice:"優しさが運を呼ぶ"}
};

function calc(){
  const text = name.value.trim().toUpperCase();
  if(!text) return alert("名前を入力してください");

  let num = 0;
  for(const c of text){
    if(map[c]) num += map[c];
  }

  while(num > 9)
    num = num.toString().split("").reduce((s,n)=>s + Number(n),0);

  const m = meanings[num];

  result.style.display = "block";
  result.innerHTML = `
    <h2>本質ナンバー：${num}</h2>
    <h3>${m.title}</h3>
    <p><b>恋愛：</b>${m.love}</p>
    <p><b>運気アドバイス：</b>${m.advice}</p>
  `;
}
