const micBtn = document.getElementById("micBtn");
const micHint = document.getElementById("micHint");
const appMessage = document.getElementById("appMessage");
const userSpeech = document.getElementById("userSpeech");
const statusText = document.getElementById("statusText");
const progressBar = document.getElementById("progressBar");
const resultModal = document.getElementById("resultModal");
const resultContent = document.getElementById("resultContent");

// 対話管理
let turn = 1;
const maxTurns = 3;
const userTexts = [];
let isRecording = false;

// システムからの問いかけ文
const appPrompts = [
  "", // 1ターン目は初期表示
  "お話しいただきありがとうございます。今日一日の過ごし方や、今どんな作業をしていたかも教えてもらえますか？",
  "なるほど、お疲れ様です。最後に、今一番しんどいと感じる部分（頭が重い、心がもやもやする、体がだるいなど）を教えてください。"
];

// 音声認識（Web Speech API）の設定
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "ja-JP";
recognition.interimResults = true; // リアルタイムに文字を表示させて体感を良くする
recognition.continuous = false;

// 音声録音（openSMILE用のバイナリ取得用）
let mediaRecorder;
let audioChunks = [];

// マイクと録音の初期化
navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };
}).catch(err => console.error("マイクの許可がありません:", err));

// 進捗バーの更新
function updateProgress() {
  const pct = ((turn - 1) / maxTurns) * 100;
  progressBar.style.width = `${pct}%`;
  statusText.innerText = `${turn} / ${maxTurns} ターン目`;
}
updateProgress();

// マイクボタンクリック時
micBtn.onclick = () => {
  if (isRecording) return;
  
  isRecording = true;
  audioChunks = [];
  userSpeech.innerText = "聞き取り中...";
  userSpeech.classList.remove("hidden");
  micBtn.classList.add("pulse", "bg-red-500");
  micHint.innerText = "お話しください（話し終えると自動で進みます）";

  recognition.start();
  if (mediaRecorder && mediaRecorder.state === "inactive") {
    mediaRecorder.start();
  }
};

// リアルタイム認識中
recognition.onresult = (event) => {
  let interimTranscript = "";
  let finalTranscript = "";

  for (let i = event.resultIndex; i < event.results.length; ++i) {
    if (event.results[i].isFinal) {
      finalTranscript += event.results[i][0].transcript;
    } else {
      interimTranscript += event.results[i][0].transcript;
    }
  }
  userSpeech.innerText = finalTranscript || interimTranscript;
};

// 話し終わり
recognition.onend = () => {
  isRecording = false;
  micBtn.classList.remove("pulse", "bg-red-500");
  micHint.innerText = "ボタンを押して話しかけてね";

  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }

  const recognizedText = userSpeech.innerText.trim();
  if (!recognizedText || recognizedText === "聞き取り中...") {
    userSpeech.innerText = "うまく聞き取れませんでした。もう一度ボタンを押してね。";
    return;
  }

  // テキストを保存
  userTexts.push(recognizedText);

  // ターンを進める
  if (turn < maxTurns) {
    setTimeout(() => {
      appMessage.innerText = appPrompts[turn];
      turn++;
      updateProgress();
      userSpeech.classList.add("hidden");
    }, 1000);
  } else {
    // 3ターン終了 -> サーバーへ送信
    progressBar.style.width = "100%";
    statusText.innerText = "分析中...";
    appMessage.innerText = "お話を総合して、あなたの疲労度を分析しています。少しお待ちくださいね...";
    userSpeech.classList.add("hidden");
    
    // 録音が完全に止まるのを少し待ってから送信
    setTimeout(() => {
      sendToAPI();
    }, 600);
  }
};

// バックエンドへの送信（FormDataを使用）
async function sendToAPI() {
  const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
  const formData = new FormData();
  
  // テキスト配列と音声ファイルをセット
  formData.append("texts", JSON.stringify(userTexts));
  formData.append("audio", audioBlob, "user_voice.webm");

  try {
    const res = await fetch("https://YOUR-RENDER.onrender.com/analyze", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    showResult(data);
  } catch (error) {
    console.error(error);
    appMessage.innerText = "エラーが発生しました。接続を確認してください。";
  }
}

// 結果の表示
function showResult(data) {
  resultModal.classList.remove("hidden");
  
  // スコアに応じたカラーリング設定
  const getColor = (val) => val > 60 ? "text-red-500" : (val > 30 ? "text-yellow-600" : "text-green-600");

  resultContent.innerHTML = `
    <div class="space-y-3 bg-[#F4F7F5] p-4 rounded-2xl">
      <div>
        <div class="flex justify-between text-sm font-bold mb-1">
          <span>🧠 脳疲労 (情報過多)</span>
          <span class="${getColor(data.score.brain)}">${data.score.brain}点</span>
        </div>
        <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
          <div class="bg-blue-400 h-full" style="width: ${data.score.brain}%"></div>
        </div>
      </div>

      <div>
        <div class="flex justify-between text-sm font-bold mb-1">
          <span>❤️ 精神疲労 (ストレス・心)</span>
          <span class="${getColor(data.score.mental)}">${data.score.mental}点</span>
        </div>
        <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
          <div class="bg-purple-400 h-full" style="width: ${data.score.mental}%"></div>
        </div>
      </div>

      <div>
        <div class="flex justify-between text-sm font-bold mb-1">
          <span>💪 身体疲労 (だるさ・コリ)</span>
          <span class="${getColor(data.score.body)}">${data.score.body}点</span>
        </div>
        <div class="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
          <div class="bg-orange-400 h-full" style="width: ${data.score.body}%"></div>
        </div>
      </div>
    </div>

    <div class="text-center p-4 border border-dashed border-[#739072] rounded-2xl">
      <div class="text-xs text-gray-500 font-bold">総合疲労度</div>
      <div class="text-4xl font-bold text-[#4F6F52] my-1">${data.score.total}<span class="text-lg"> / 100</span></div>
      <div class="text-sm font-medium text-[#739072] mt-2">タイプ: <span class="capitalize font-bold text-[#2C3E2B]">${data.score.category}</span></div>
    </div>

    <div>
      <h3 class="font-bold text-[#4F6F52] mb-2 flex items-center gap-1">🌱 あなたに贈る休養デザイン</h3>
      <div class="space-y-2">
        ${data.recommendations.map(v => `
          <div class="p-3 bg-[#F4F7F5] rounded-xl border-l-4 border-[#739072] text-sm font-medium">
            ${v}
          </div>
        `).join("")}
      </div>
    </div>
  `;
}
