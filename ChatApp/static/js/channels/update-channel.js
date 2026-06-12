/*
チャンネルを更新するモーダルの制御
*/

const updateButton = document.getElementById("channel-update-button");
const updateChannelModal = document.getElementById("update-channel-modal");
const updateModalClose = document.getElementById("update-modal-close");
const updateModalOverlay = document.getElementById("update-modal-overlay");
const updateModalCancel = document.querySelector(".update-modal-cancel");

const openModal = () => {
  if (updateChannelModal) updateChannelModal.classList.add("modal-open");
};

const closeModal = () => {
  if (updateChannelModal) updateChannelModal.classList.remove("modal-open");
};

if (updateButton && updateChannelModal) {
  updateButton.addEventListener("click", openModal);
}

if (updateModalClose) {
  updateModalClose.addEventListener("click", closeModal);
}

if (updateModalOverlay) {
  updateModalOverlay.addEventListener("click", closeModal);
}

if (updateModalCancel) {
  updateModalCancel.addEventListener("click", closeModal);
}

addEventListener("click", (e) => {
  if (e.target === updateChannelModal) closeModal();
});

// Ctrl/Command + Enter で送信
document.addEventListener("keydown", (e) => {
  if (updateChannelModal && !updateChannelModal.classList.contains("modal-open")) return;
  if (e.code === "Enter") e.preventDefault();
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    const form = document.updateChannelForm;
    if (form?.channelTitle?.value?.trim()) form.submit();
  }
});
