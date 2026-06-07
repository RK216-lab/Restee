const micBtn = document.getElementById("micBtn");
const textEl = document.getElementById("text");
const resultEl = document.getElementById("result");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = "ja-JP";
recognition.interimResults = false;

micBtn.onclick = () => {
  recognition.start();
};

recognition.onresult = (event) => {
  const text = event.results[0][0].transcript;
  textEl.innerText = text;

  sendToAPI(text);
};

async function sendToAPI(text) {
  // ⚠️ 以下の URL を、あなたの Render の本当の URL に必ず書き換えてください！
  // 例: https://restee-backend.onrender.com/analyze
  const RENDER_URL = "https://YOUR-RENDER.onrender.com/analyze"; 

  try {
    const res = await fetch(RENDER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // 配列ではなく、現在のサーバーが受け取れる形（{ "texts": [text] }）で正しく送信します
      body: JSON.stringify({ texts: [text] })
    });

    if (!res.ok) {
      throw new Error(`サーバーエラー: ${res.status}`);
    }

    const data = await res.json();
    showResult(data);
  } catch (error) {
    console.error("通信エラー詳細:", error);
    resultEl.innerHTML = `<p style="color: red;">エラーが発生しました。接続を確認してください。<br>（詳細: ${error.message}）</p>`;
  }
}

function showResult(data) {
  // サーバーから返ってくるデータ構造 (data.score) に合わせて画面を更新
  resultEl.innerHTML = `
    <h3>疲労スコア</h3>
    脳: ${data.score.brain}<br>
    精神: ${data.score.mental}<br>
    身体: ${data.score.body}<br>
    合計: ${data.score.total}<br><br>

    <h3>おすすめ</h3>
    ${data.recommendations.map(v => `<p>・${v}</p>`).join("")}
  `;
}
