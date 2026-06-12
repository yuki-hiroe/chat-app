/*
チャンネルを登録するモーダルの制御
*/

export const initCreateChannelModal = () => {
  const createChannelModal = document.getElementById("create-channel-modal");
  const createModalClose = document.getElementById("create-modal-close");
  const createModalOverlay = document.getElementById("create-modal-overlay");
  const createModalCancel = document.querySelector(".create-modal-cancel");
  const createChannelButton = document.getElementById("create-channel-button");

  const openModal = () => {
    if (createChannelModal) createChannelModal.classList.add("modal-open");
  };

  const closeModal = () => {
    if (createChannelModal) createChannelModal.classList.remove("modal-open");
  };

  if (createChannelButton) {
    createChannelButton.addEventListener("click", openModal);
  }

  if (createModalClose) {
    createModalClose.addEventListener("click", closeModal);
  }

  if (createModalOverlay) {
    createModalOverlay.addEventListener("click", closeModal);
  }

  if (createModalCancel) {
    createModalCancel.addEventListener("click", closeModal);
  }

  // モーダル外クリックで閉じる
  addEventListener("click", (e) => {
    if (e.target === createChannelModal) closeModal();
  });

  // Ctrl/Command + Enter で送信
  document.addEventListener("keydown", (e) => {
    if (createChannelModal && !createChannelModal.classList.contains("modal-open")) return;
    if (e.code === "Enter") e.preventDefault();
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const form = document.createChannelForm;
      if (form?.channelTitle?.value?.trim()) form.submit();
    }
  });
};
