/**
 * Food bank cart — localStorage persistence and page helpers.
 */
const FoodBankCart = (() => {
  const STORAGE_KEY = "food_bank_cart";
  const HOUSEHOLD_KEY = "food_bank_household";

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
  }

  function clearCart() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(HOUSEHOLD_KEY);
    updateBadge();
  }

  function cartItemCount(cart) {
    return cart.reduce((sum, line) => sum + (line.quantity || 0), 0);
  }

  function updateBadge() {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    const count = cartItemCount(getCart());
    badge.textContent = String(count);
    badge.hidden = count === 0;
  }

  function addToCart(itemId, quantity) {
    const qty = Math.max(1, parseInt(quantity, 10) || 1);
    const cart = getCart();
    const existing = cart.find((line) => line.item_id === itemId);
    if (existing) {
      existing.quantity += qty;
    } else {
      cart.push({ item_id: itemId, quantity: qty });
    }
    saveCart(cart);
  }

  function setLineQuantity(itemId, quantity) {
    const qty = parseInt(quantity, 10);
    let cart = getCart();
    if (!qty || qty < 1) {
      cart = cart.filter((line) => line.item_id !== itemId);
    } else {
      const line = cart.find((l) => l.item_id === itemId);
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
        const category = card.dataset.category || "";
        const matchesCategory = activeCategory === "all" || category === activeCategory;
        const matchesSearch = !query || name.includes(query);
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
        addToCart(itemId, qtyInput.value);
        const btn = e.target.closest(".add-to-cart-btn");
        const original = btn.textContent;
        btn.textContent = "Added!";
        btn.disabled = true;
        setTimeout(() => {
          btn.textContent = original;
          btn.disabled = false;
        }, 900);
      }
    });
  }

  function renderCartLines(cart, catalogById, tbody) {
    tbody.innerHTML = "";
    cart.forEach((line) => {
      const item = catalogById[line.item_id];
      if (!item) return;

      const tr = document.createElement("tr");
      tr.dataset.itemId = line.item_id;
      tr.innerHTML = `
        <td>
          <strong>${escapeHtml(item.name)}</strong>
          <span class="meta">${escapeHtml(item.category)} · ${escapeHtml(item.unit)}</span>
        </td>
        <td>
          <div class="qty-stepper qty-stepper-sm">
            <button type="button" class="qty-btn qty-minus" aria-label="Decrease">−</button>
            <input type="number" class="qty-input cart-qty" value="${line.quantity}" min="1" aria-label="Quantity">
            <button type="button" class="qty-btn qty-plus" aria-label="Increase">+</button>
          </div>
        </td>
        <td>
          <button type="button" class="link-btn link-danger remove-line-btn">Remove</button>
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

    const catalog = getCatalog();
    const catalogById = catalogMap(catalog);
    const cart = getCart();
    const content = document.getElementById("cart-content");
    const empty = document.getElementById("cart-empty");
    const tbody = document.getElementById("cart-lines");
    const householdInput = document.getElementById("household_name");
    const reviewBtn = document.getElementById("review-order-btn");

    const savedHousehold = sessionStorage.getItem(HOUSEHOLD_KEY);
    if (householdInput && savedHousehold) {
      householdInput.value = savedHousehold;
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
        setLineQuantity(itemId, next);
        updateBadge();
        return;
      }
      if (e.target.closest(".qty-plus")) {
        const next = (parseInt(qtyInput.value, 10) || 1) + 1;
        qtyInput.value = next;
        setLineQuantity(itemId, next);
        updateBadge();
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
      setLineQuantity(row.dataset.itemId, e.target.value);
      refresh();
      updateBadge();
    });

    reviewBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      if (!getCart().length) return;
      const name = householdInput?.value.trim() || "";
      sessionStorage.setItem(HOUSEHOLD_KEY, name);
      const params = name ? `?household_name=${encodeURIComponent(name)}` : "";
      window.location.href = `/confirm${params}`;
    });
  }

  function initConfirmPage() {
    updateBadge();

    const catalog = getCatalog();
    const catalogById = catalogMap(catalog);
    const cart = getCart().filter((line) => catalogById[line.item_id]);
    const content = document.getElementById("confirm-content");
    const empty = document.getElementById("confirm-empty");
    const tbody = document.getElementById("confirm-lines");
    const householdEl = document.getElementById("confirm-household");
    const householdHidden = document.getElementById("household_name_hidden");
    const cartJsonHidden = document.getElementById("cart_json_hidden");

    const params = new URLSearchParams(window.location.search);
    const household =
      params.get("household_name")?.trim() ||
      sessionStorage.getItem(HOUSEHOLD_KEY)?.trim() ||
      "";

    if (!cart.length) {
      if (content) content.hidden = true;
      if (empty) empty.hidden = false;
      return;
    }

    if (content) content.hidden = false;
    if (empty) empty.hidden = true;

    if (householdEl && household) {
      householdEl.textContent = `Ordering for: ${household}`;
      householdEl.hidden = false;
    }

    if (householdHidden) householdHidden.value = household;
    if (cartJsonHidden) cartJsonHidden.value = JSON.stringify(cart);

    if (tbody) {
      tbody.innerHTML = "";
      cart.forEach((line) => {
        const item = catalogById[line.item_id];
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${escapeHtml(item.name)} <span class="meta">${escapeHtml(item.unit)}</span></td>
          <td class="num-col"><strong>${line.quantity}</strong></td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  return {
    getCart,
    saveCart,
    clearCart,
    addToCart,
    updateBadge,
    initShopPage,
    initCartPage,
    initConfirmPage,
  };
})();

// Update cart badge on every page load
document.addEventListener("DOMContentLoaded", () => {
  if (typeof FoodBankCart !== "undefined") {
    FoodBankCart.updateBadge();
  }
});
