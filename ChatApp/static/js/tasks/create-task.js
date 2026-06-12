/*
タスク追加モーダルの制御
*/

export const initCreateTaskModal = () => {
  const createTaskModal = document.getElementById("create-task-modal");
  const createTaskModalClose = document.getElementById("create-task-modal-close");
  const createTaskModalOverlay = document.getElementById("create-task-modal-overlay");
  const createTaskModalCancel = document.querySelector(".create-task-modal-cancel");
  const createTaskButton = document.getElementById("tasks-add-btn");
  const taskDueDateInput = document.getElementById("taskDueDate");

  const todayStr = new Date().toISOString().split("T")[0];

  let flatpickrInstance = null;
  const toggleBtn = document.getElementById("taskDueDateToggle");
  if (taskDueDateInput && typeof window.flatpickr !== "undefined") {
    flatpickrInstance = window.flatpickr(taskDueDateInput, {
      dateFormat: "Y-m-d",
      minDate: todayStr,
      locale: window.flatpickr.l10ns.ja,
      clickOpens: true,
    });
    if (toggleBtn) {
      toggleBtn.addEventListener("click", () => taskDueDateInput.focus());
    }
  }

  const openModal = () => {
    if (createTaskModal) createTaskModal.classList.add("modal-open");
    if (taskDueDateInput && !taskDueDateInput.value) {
      taskDueDateInput.value = todayStr;
      if (flatpickrInstance) flatpickrInstance.setDate(todayStr, false);
    }
  };

  const closeModal = () => {
    if (createTaskModal) createTaskModal.classList.remove("modal-open");
  };

  if (createTaskButton) {
    createTaskButton.addEventListener("click", openModal);
  }

  if (createTaskModalClose) {
    createTaskModalClose.addEventListener("click", closeModal);
  }

  if (createTaskModalOverlay) {
    createTaskModalOverlay.addEventListener("click", closeModal);
  }

  if (createTaskModalCancel) {
    createTaskModalCancel.addEventListener("click", closeModal);
  }

  if (createTaskModal) {
    createTaskModal.addEventListener("click", (e) => {
      if (e.target === createTaskModal) closeModal();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (createTaskModal && !createTaskModal.classList.contains("modal-open")) return;
    if (e.code === "Enter") e.preventDefault();
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const form = document.forms.createTaskForm;
      if (form?.title?.value?.trim()) form.submit();
    }
  });
};
