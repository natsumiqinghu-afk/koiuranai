function analyze() {
  const name = document.getElementById("name").value.trim();
  if (!name) return alert("名前を入力してください");

  let energy = 0;
  for (const c of name) energy += c.charCodeAt(0);

  const wave = energy % 100;
  const mind = (energy * 3) % 100;
  const love = (energy * 5) % 100;
  const luck = (energy * 7) % 100;

  const tendencies = [
    "感受性が強く優しい心を持つタイプ",
    "探求心旺盛で職人的なタイプ",
    "自由と好奇心に満ちた冒険家タイプ",
    "みんなを支える縁の下の力持ちタイプ",
    "天才肌・直感が鋭いタイプ",
  ];
  const tendency = tendencies[energy % tendencies.length];

  const result = document.getElementById("result");
  result.style.display = "block";
  result.innerHTML = `
    <h2>波動解析結果</h2>
    <p><strong>${name}</strong> さんの名前が持つ波動エネルギーを解析しました。</p>

    ${makeBar("総合波動レベル", wave)}
    ${makeBar("精神エネルギー", mind)}
    ${makeBar("愛情波動", love)}
    ${makeBar("運気バイブス", luck)}

    <h3 style="margin-top:25px;">性質傾向</h3>
    <p>${tendency}</p>
  `;
}

function makeBar(label, val) {
  return `
    <div class="label">${label}：${val}</div>
    <div class="bar" style="width:${val}%"></div>
  `;
}
