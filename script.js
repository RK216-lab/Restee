console.log("script loaded");
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
  const res = await fetch("https://YOUR-RENDER-URL.onrender.com/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      texts: [text]
    })
  });

  const data = await res.json();
  showResult(data);
}
function showResult(data) {
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
