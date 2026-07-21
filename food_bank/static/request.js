(function () {
  const form = document.getElementById("request-form");
  if (!form) return;

  const i18n = () => window.FoodBankI18n;
  const submitBtn = document.getElementById("submit-requests");
  const inputs = form.querySelectorAll(".category-input");
  const visitInputs = form.querySelectorAll('input[name="expecting_visit"]');
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
    const fb = i18n();
    return fb && typeof fb.t === "function" ? fb.t(key) : fallback;
  }

  function updateSubmitState() {
    const anyChecked = Array.from(inputs).some((input) => input.checked);
    const visitAnswered = visitInputs.length === 0 || Array.from(visitInputs).some((input) => input.checked);
    submitBtn.disabled = !anyChecked || !visitAnswered;
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

  function fillModal(categoryId) {
    const fb = i18n();
    const category = detailsById[categoryId];
    if (!category || !modal) return;

    modalTitle.textContent = fb
      ? fb.planningCategory(categoryId, "name")
      : category.display_name || "";
    modalDescription.textContent = fb
      ? fb.planningCategory(categoryId, "description")
      : category.description || category.donor_friendly_translation || "";

    modalItems.innerHTML = "";
    const items = category.example_items || [];
    if (items.length) {
      modalItemsWrap.hidden = false;
      items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = fb ? fb.exampleItemLabel(item) : typeof item === "string" ? item : item.name;
        modalItems.appendChild(li);
      });
    } else {
      modalItemsWrap.hidden = true;
    }
  }

  function openModal(categoryId) {
    if (!detailsById[categoryId] || !modal) return;
    activeCategoryId = categoryId;
    fillModal(categoryId);
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

  visitInputs.forEach((input) => {
    input.addEventListener("change", updateSubmitState);
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
    if (activeCategoryId) {
      fillModal(activeCategoryId);
    }
    syncModalToggle();
  });

  updateSubmitState();
  syncTileStates();
})();
