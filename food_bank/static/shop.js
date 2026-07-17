/**
 * Food bank cart — localStorage persistence and page helpers.
 */
const FoodBankCart = (() => {
  const STORAGE_KEY = "food_bank_cart";

  function i18n(key, vars = {}) {
    if (typeof FoodBankI18n !== "undefined") return FoodBankI18n.t(key, vars);
    return key;
  }

  function itemLabel(itemId, fallback = "") {
    if (typeof FoodBankI18n !== "undefined") return FoodBankI18n.itemName(itemId, fallback);
    return fallback;
  }

  function categoryLabel(cat) {
    if (typeof FoodBankI18n !== "undefined") return FoodBankI18n.categoryName(cat);
    return cat;
  }

  function unitLabel(unit) {
    if (typeof FoodBankI18n !== "undefined") return FoodBankI18n.unitName(unit);
    return unit;
  }

  function itemImageSrc(itemId) {
    return `/static/images/items/${itemId}.svg`;
  }

  function weightLabel() {
    return typeof FoodBankI18n !== "undefined" && FoodBankI18n.getLang() === "zh" ? "磅" : "lb";
  }

  function getOrderWeightLimit() {
    const el = document.getElementById("order-weight-limit");
    if (!el) return 10;
    const val = parseFloat(el.textContent);
    return Number.isFinite(val) ? val : 10;
  }

  function getCart() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function saveCart(cart) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    updateBadge();
    updateWeightDisplay();
  }

  function clearCart() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(HOUSEHOLD_KEY);
    updateBadge();
    updateWeightDisplay();
  }

  function cartItemCount(cart) {
    return cart.reduce((sum, line) => sum + (line.quantity || 0), 0);
  }

  function computeCartWeight(cart, catalogById) {
    let total = 0;
    cart.forEach((line) => {
      const item = catalogById[line.item_id];
      if (!item) return;
      const weight = parseFloat(item.weight_lb) || 0;
      total += (line.quantity || 0) * weight;
    });
    return Math.round(total * 100) / 100;
  }

  function wouldExceedLimit(cart, catalogById, itemId, addQty) {
    const limit = getOrderWeightLimit();
    const item = catalogById[itemId];
    if (!item) return false;
    const unitWeight = parseFloat(item.weight_lb) || 0;
    const current = computeCartWeight(cart, catalogById);
    const extra = unitWeight * addQty;
    return current + extra > limit + 0.001;
  }

  function showWeightMessage(message, isError) {
    let el = document.getElementById("weight-limit-message");
    if (!el) {
      el = document.createElement("p");
      el.id = "weight-limit-message";
      el.className = "weight-limit-message";
      const badge = document.getElementById("cart-weight-badge");
      if (badge?.parentNode) {
        badge.parentNode.insertBefore(el, badge.nextSibling);
      }
    }
    el.textContent = message;
    el.classList.toggle("weight-limit-error", !!isError);
    el.hidden = !message;
    if (message) {
      setTimeout(() => {
        if (el.textContent === message) el.hidden = true;
      }, 4000);
    }
  }

  function updateWeightDisplay() {
    const catalog = getCatalog();
    const catalogById = catalogMap(catalog);
    const cart = getCart();
    const weight = computeCartWeight(cart, catalogById);
    const limit = getOrderWeightLimit();
    const text = `${weight.toFixed(1)} / ${limit} lb`;

    document.querySelectorAll("#cart-weight-badge, .cart-weight-display").forEach((el) => {
      el.textContent = text;
      el.classList.toggle("weight-over", weight > limit);
      el.hidden = cart.length === 0 && el.id === "cart-weight-badge";
    });

    const placeBtn = document.getElementById("place-order-btn");
    if (placeBtn) {
      placeBtn.disabled = weight > limit;
      placeBtn.title =
        weight > limit ? `Cart exceeds ${limit} lb limit` : "";
    }

    const reviewBtn = document.getElementById("review-order-btn");
    if (reviewBtn) {
      reviewBtn.disabled = weight > limit;
    }
  }

  function updateBadge() {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    const count = cartItemCount(getCart());
    badge.textContent = String(count);
    badge.hidden = count === 0;
  }

  function addToCart(itemId, quantity, catalogById) {
    const qty = Math.max(1, parseInt(quantity, 10) || 1);
    const cart = getCart();
    if (!catalogById) catalogById = catalogMap(getCatalog());

    if (wouldExceedLimit(cart, catalogById, itemId, qty)) {
      const limit = getOrderWeightLimit();
      showWeightMessage(i18n("weight_over_msg", { limit }), true);
      return false;
    }

    const existing = cart.find((line) => line.item_id === itemId);
    if (existing) {
      const newTotal = existing.quantity + qty;
      if (wouldExceedLimit(cart, catalogById, itemId, qty)) {
        const limit = getOrderWeightLimit();
        showWeightMessage(i18n("weight_over_msg", { limit }), true);
        return false;
      }
      existing.quantity = newTotal;
    } else {
      cart.push({ item_id: itemId, quantity: qty });
    }
    saveCart(cart);
    return true;
  }

  function setLineQuantity(itemId, quantity, catalogById) {
    const qty = parseInt(quantity, 10);
    let cart = getCart();
    if (!catalogById) catalogById = catalogMap(getCatalog());

    if (!qty || qty < 1) {
      cart = cart.filter((line) => line.item_id !== itemId);
    } else {
      const line = cart.find((l) => l.item_id === itemId);
      const oldQty = line ? line.quantity : 0;
      const delta = qty - oldQty;
      if (delta > 0 && wouldExceedLimit(cart, catalogById, itemId, delta)) {
        const limit = getOrderWeightLimit();
        showWeightMessage(i18n("weight_over_msg", { limit: getOrderWeightLimit() }), true);
        return cart;
      }
      if (line) line.quantity = qty;
    }
    saveCart(cart);
    return cart;
  }

  function removeLine(itemId) {
    const cart = getCart().filter((line) => line.item_id !== itemId);
    saveCart(cart);
    return cart;
  }

  function getCatalog() {
    const el = document.getElementById("catalog-data");
    if (!el) return [];
    try {
      return JSON.parse(el.textContent);
    } catch {
      return [];
    }
  }

  function catalogMap(catalog) {
    return Object.fromEntries(catalog.map((item) => [item.id, item]));
  }

  function initShopPage() {
    updateBadge();
    updateWeightDisplay();

    const catalog = getCatalog();
    const catalogById = catalogMap(catalog);
    const grid = document.getElementById("item-grid");
    const searchInput = document.getElementById("item-search");
    const tabs = document.getElementById("category-tabs");
    const emptyState = document.getElementById("shop-empty");
    const clearFiltersBtn = document.getElementById("clear-filters-btn");

    let activeCategory = "all";

    function applyFilters() {
      const query = (searchInput?.value || "").trim().toLowerCase();
      const cards = grid?.querySelectorAll(".item-card") || [];
      let visible = 0;

      cards.forEach((card) => {
        const name = card.dataset.name || "";
        const itemId = card.dataset.itemId || "";
        const translated = itemLabel(itemId, name).toLowerCase();
        const category = card.dataset.category || "";
        const matchesCategory = activeCategory === "all" || category === activeCategory;
        const matchesSearch = !query || name.includes(query) || translated.includes(query);
        const show = matchesCategory && matchesSearch;
        card.hidden = !show;
        if (show) visible += 1;
      });

      if (emptyState) emptyState.hidden = visible > 0;
      if (grid) grid.hidden = visible === 0;
    }

    tabs?.addEventListener("click", (e) => {
      const btn = e.target.closest(".category-tab");
      if (!btn) return;
      tabs.querySelectorAll(".category-tab").forEach((t) => t.classList.remove("active"));
      btn.classList.add("active");
      activeCategory = btn.dataset.category || "all";
      applyFilters();
    });

    searchInput?.addEventListener("input", applyFilters);

    clearFiltersBtn?.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      activeCategory = "all";
      tabs?.querySelectorAll(".category-tab").forEach((t) => {
        t.classList.toggle("active", t.dataset.category === "all");
      });
      applyFilters();
    });

    grid?.addEventListener("click", (e) => {
      const card = e.target.closest(".item-card");
      if (!card) return;

      const itemId = card.dataset.itemId;
      const qtyInput = card.querySelector(".qty-input");

      if (e.target.closest(".qty-minus")) {
        qtyInput.value = Math.max(1, (parseInt(qtyInput.value, 10) || 1) - 1);
        return;
      }
      if (e.target.closest(".qty-plus")) {
        qtyInput.value = (parseInt(qtyInput.value, 10) || 1) + 1;
        return;
      }
      if (e.target.closest(".add-to-cart-btn")) {
        const added = addToCart(itemId, qtyInput.value, catalogById);
        const btn = e.target.closest(".add-to-cart-btn");
        if (added) {
          const btn = e.target.closest(".add-to-cart-btn");
          const original = btn.textContent;
          btn.textContent = i18n("added");
          btn.disabled = true;
          setTimeout(() => {
            btn.textContent = i18n("add_to_cart");
            btn.disabled = false;
          }, 900);
        }
      }
    });

    document.addEventListener("foodbank:langchange", () => {
      if (typeof FoodBankI18n !== "undefined") FoodBankI18n.applyToElements();
      applyFilters();
    });
  }

  function renderCartLines(cart, catalogById, tbody) {
    tbody.innerHTML = "";
    const wLabel = weightLabel();
    cart.forEach((line) => {
      const item = catalogById[line.item_id];
      if (!item) return;
      const lineWeight = ((parseFloat(item.weight_lb) || 0) * line.quantity).toFixed(1);
      const displayName = itemLabel(line.item_id, item.name);

      const tr = document.createElement("tr");
      tr.dataset.itemId = line.item_id;
      tr.innerHTML = `
        <td>
          <div class="cart-item-cell">
            <img class="item-thumb" src="${itemImageSrc(line.item_id)}" alt="" width="40" height="40">
            <div>
              <strong>${escapeHtml(displayName)}</strong>
              <span class="meta">${escapeHtml(categoryLabel(item.category))} · ${escapeHtml(unitLabel(item.unit))} · ${lineWeight} ${wLabel}</span>
            </div>
          </div>
        </td>
        <td>
          <div class="qty-stepper qty-stepper-sm">
            <button type="button" class="qty-btn qty-minus" aria-label="${escapeHtml(i18n("decrease"))}">−</button>
            <input type="number" class="qty-input cart-qty" value="${line.quantity}" min="1" aria-label="${escapeHtml(i18n("quantity"))}">
            <button type="button" class="qty-btn qty-plus" aria-label="${escapeHtml(i18n("increase"))}">+</button>
          </div>
        </td>
        <td>
          <button type="button" class="link-btn link-danger remove-line-btn">${escapeHtml(i18n("remove"))}</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function initCartPage() {
    updateBadge();
    updateWeightDisplay();

    const catalog = getCatalog();
    const catalogById = catalogMap(catalog);
    const content = document.getElementById("cart-content");
    const empty = document.getElementById("cart-empty");
    const tbody = document.getElementById("cart-lines");
    const reviewBtn = document.getElementById("review-order-btn");

    function updateCartSubtitle() {
      const el = document.getElementById("cart-subtitle-weight");
      if (!el) return;
      const catalog = getCatalog();
      const weight = computeCartWeight(getCart(), catalogMap(catalog)).toFixed(1);
      const limit = getOrderWeightLimit();
      const wLabel = weightLabel();
      el.textContent = i18n("cart_subtitle", { weight: `${weight} / ${limit} ${wLabel}` });
    }

    function refresh() {
      const currentCart = getCart().filter((line) => catalogById[line.item_id]);
      if (currentCart.length !== getCart().length) saveCart(currentCart);

      const hasItems = currentCart.length > 0;
      if (content) content.hidden = !hasItems;
      if (empty) empty.hidden = hasItems;

      if (hasItems && tbody) {
        renderCartLines(currentCart, catalogById, tbody);
      }
      updateWeightDisplay();
      updateCartSubtitle();
    }

    refresh();

    tbody?.addEventListener("click", (e) => {
      const row = e.target.closest("tr");
      if (!row) return;
      const itemId = row.dataset.itemId;
      const qtyInput = row.querySelector(".cart-qty");

      if (e.target.closest(".qty-minus")) {
        const next = Math.max(1, (parseInt(qtyInput.value, 10) || 1) - 1);
        qtyInput.value = next;
        setLineQuantity(itemId, next, catalogById);
        refresh();
        return;
      }
      if (e.target.closest(".qty-plus")) {
        const next = (parseInt(qtyInput.value, 10) || 1) + 1;
        setLineQuantity(itemId, next, catalogById);
        qtyInput.value = getCart().find((l) => l.item_id === itemId)?.quantity || next;
        refresh();
        return;
      }
      if (e.target.closest(".remove-line-btn")) {
        removeLine(itemId);
        refresh();
      }
    });

    tbody?.addEventListener("change", (e) => {
      if (!e.target.classList.contains("cart-qty")) return;
      const row = e.target.closest("tr");
      if (!row) return;
      setLineQuantity(row.dataset.itemId, e.target.value, catalogById);
      refresh();
    });

    reviewBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      if (!getCart().length) return;
      const weight = computeCartWeight(getCart(), catalogById);
      const limit = getOrderWeightLimit();
      if (weight > limit) {
        showWeightMessage(i18n("weight_over_cart", { weight: weight.toFixed(1), limit }), true);
        return;
      }
      window.location.href = "/confirm";
    });

    document.addEventListener("foodbank:langchange", () => {
      if (typeof FoodBankI18n !== "undefined") FoodBankI18n.applyToElements();
      refresh();
    });
  }

  function initConfirmPage() {
    updateBadge();
    updateWeightDisplay();

    const catalog = getCatalog();
    const catalogById = catalogMap(catalog);
    const cart = getCart().filter((line) => catalogById[line.item_id]);
    const content = document.getElementById("confirm-content");
    const empty = document.getElementById("confirm-empty");
    const tbody = document.getElementById("confirm-lines");
    const cartJsonHidden = document.getElementById("cart_json_hidden");
    const placeBtn = document.getElementById("place-order-btn");

    if (!cart.length) {
      if (content) content.hidden = true;
      if (empty) empty.hidden = false;
      return;
    }

    const weight = computeCartWeight(cart, catalogById);
    const limit = getOrderWeightLimit();
    const overLimit = weight > limit;

    if (content) content.hidden = false;
    if (empty) empty.hidden = true;

    if (cartJsonHidden) cartJsonHidden.value = JSON.stringify(cart);

    if (placeBtn) {
      placeBtn.disabled = overLimit;
    }

    function renderConfirmLines() {
      if (!tbody) return;
      const wLabel = weightLabel();
      tbody.innerHTML = "";
      cart.forEach((line) => {
        const item = catalogById[line.item_id];
        const lineWeight = ((parseFloat(item.weight_lb) || 0) * line.quantity).toFixed(1);
        const displayName = itemLabel(line.item_id, item.name);
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <div class="cart-item-cell">
              <img class="item-thumb" src="${itemImageSrc(line.item_id)}" alt="" width="40" height="40">
              <div>${escapeHtml(displayName)} <span class="meta">${escapeHtml(unitLabel(item.unit))} · ${lineWeight} ${wLabel}</span></div>
            </div>
          </td>
          <td class="num-col"><strong>${line.quantity}</strong></td>
        `;
        tbody.appendChild(tr);
      });
    }

    renderConfirmLines();

    if (overLimit) {
      showWeightMessage(i18n("weight_over_cart", { weight: weight.toFixed(1), limit }), true);
    }

    document.addEventListener("foodbank:langchange", () => {
      if (typeof FoodBankI18n !== "undefined") FoodBankI18n.applyToElements();
      renderConfirmLines();
    });
  }

  return {
    getCart,
    saveCart,
    clearCart,
    addToCart,
    updateBadge,
    updateWeightDisplay,
    initShopPage,
    initCartPage,
    initConfirmPage,
  };
})();

document.addEventListener("DOMContentLoaded", () => {
  if (typeof FoodBankCart !== "undefined") {
    FoodBankCart.updateBadge();
    FoodBankCart.updateWeightDisplay();
  }
});
