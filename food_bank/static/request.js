(function () {
  const form = document.getElementById("request-form");
  if (!form) return;

  const submitBtn = document.getElementById("submit-requests");
  const inputs = form.querySelectorAll(".category-input");
  const modal = document.getElementById("category-modal");
  const modalTitle = document.getElementById("category-modal-title");
  const modalDescription = document.getElementById("category-modal-description");
  const modalItems = document.getElementById("category-modal-items");
  const modalItemsWrap = document.getElementById("category-modal-items-wrap");
  const modalToggle = document.getElementById("category-modal-toggle");
  const detailsEl = document.getElementById("category-details-json");

  let categoryDetails = [];
  let activeCategoryId = null;

  if (detailsEl) {
    try {
      categoryDetails = JSON.parse(detailsEl.textContent || "[]");
    } catch (_err) {
      categoryDetails = [];
    }
  }

  const detailsById = Object.fromEntries(categoryDetails.map((cat) => [cat.id, cat]));

  function t(key, fallback) {
    if (window.FoodBankI18n && typeof window.FoodBankI18n.t === "function") {
      return window.FoodBankI18n.t(key);
    }
    return fallback;
  }

  function updateSubmitState() {
    const anyChecked = Array.from(inputs).some((input) => input.checked);
    submitBtn.disabled = !anyChecked;
  }

  function syncTileStates() {
    form.querySelectorAll(".category-tile").forEach((tile) => {
      const input = tile.querySelector(".category-input");
      tile.classList.toggle("is-selected", Boolean(input && input.checked));
    });
  }

  function syncModalToggle() {
    if (!activeCategoryId || !modalToggle) return;
    const input = form.querySelector(`.category-input[value="${activeCategoryId}"]`);
    const checked = input && input.checked;
    modalToggle.textContent = checked
      ? t("request_modal_remove", "Remove from my needs")
      : t("request_modal_add", "Add to my needs");
    modalToggle.classList.toggle("btn-muted", checked);
    modalToggle.classList.toggle("btn-primary", !checked);
  }

  function openModal(categoryId) {
    const category = detailsById[categoryId];
    if (!category || !modal) return;

    activeCategoryId = categoryId;
    modalTitle.textContent = category.display_name || "";
    modalDescription.textContent = category.description || category.donor_friendly_translation || "";

    modalItems.innerHTML = "";
    const items = category.example_items || [];
    if (items.length) {
      modalItemsWrap.hidden = false;
      items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        modalItems.appendChild(li);
      });
    } else {
      modalItemsWrap.hidden = true;
    }

    syncModalToggle();
    modal.hidden = false;
    document.body.classList.add("modal-open");
    modalToggle.focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    activeCategoryId = null;
  }

  inputs.forEach((input) => {
    input.addEventListener("change", () => {
      updateSubmitState();
      syncTileStates();
      syncModalToggle();
    });
  });

  form.querySelectorAll(".category-open-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      openModal(btn.dataset.categoryId);
    });
  });

  if (modalToggle) {
    modalToggle.addEventListener("click", () => {
      if (!activeCategoryId) return;
      const input = form.querySelector(`.category-input[value="${activeCategoryId}"]`);
      if (!input) return;
      input.checked = !input.checked;
      input.dispatchEvent(new Event("change", { bubbles: true }));
      syncModalToggle();
    });
  }

  modal.querySelectorAll("[data-close-modal]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal && !modal.hidden) {
      closeModal();
    }
  });

  document.addEventListener("foodbank:langchange", () => {
    syncModalToggle();
  });

  updateSubmitState();
  syncTileStates();
})();
