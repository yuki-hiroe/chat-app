/*
各チャンネル詳細ページ内、ページ読み込み時に自動で下までスクロールする
*/

const element = document.getElementById("message-area");
if (element) {
  element.scrollTop = element.scrollHeight;
}

