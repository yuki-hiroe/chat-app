/*
チャット入力欄 (contenteditable) の制御
- Enterで送信 (IME変換確定のEnterは除外)
- 送信時に hidden input へテキストを詰める
*/

const chatForm = document.getElementById("chat-message-form");
const chatEditor = document.getElementById("message-editor");
const chatHiddenInput = document.getElementById("message");

if (chatForm && chatEditor && chatHiddenInput) {
  chatForm.addEventListener("submit", (e) => {
    const text = chatEditor.innerText.trim();
    if (!text) {
      e.preventDefault();
      return;
    }
    chatHiddenInput.value = text;
  });

  chatEditor.addEventListener("keydown", (e) => {
    // IME変換中のEnter(isComposing / keyCode 229)では送信しない
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) {
      e.preventDefault();
      chatForm.requestSubmit();
    }
  });

  // 全削除時に残る<br>を掃除して :empty のプレースホルダーを復活させる
  chatEditor.addEventListener("input", () => {
    if (chatEditor.textContent.trim() === "" && chatEditor.innerHTML !== "") {
      chatEditor.innerHTML = "";
    }
  });

  // 入力欄ピルのどこをクリックしてもフォーカスが入るように
  chatForm.addEventListener("click", () => chatEditor.focus());
}
