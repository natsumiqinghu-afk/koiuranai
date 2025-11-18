function calcName(str){
  return [...str].reduce((s,c)=>s + c.charCodeAt(0), 0);
}
function calcBirth(b){
  if(!b) return 0;
  return b.replace(/-/g,"").split("").reduce((s,c)=>s + Number(c),0);
}

function check(){
  const n1 = calcName(name1.value);
  const n2 = calcName(name2.value);
  const b1 = calcBirth(birth1.value);
  const b2 = calcBirth(birth2.value);

  const raw = Math.abs((n1 + b1) - (n2 + b2));
  const score = 100 - (raw % 100);

  let rank = "C";
  if (score > 85) rank = "S";
  else if(score > 70) rank = "A";
  else if(score > 50) rank = "B";

  result.style.display = "block";
  result.innerHTML = `
    <h2>相性：${score}%（ランク ${rank}）</h2>
    <p>・名前エネルギー差：${Math.abs(n1 - n2)}</p>
    <p>・誕生日数値差：${Math.abs(b1 - b2)}</p>
    <p>・総合マッチング指数：${raw}</p>
  `;
}
