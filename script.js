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
