(function () {
  const form = document.getElementById("request-form");
  if (!form) return;

  const submitBtn = document.getElementById("submit-requests");
  const inputs = form.querySelectorAll(".category-input");

  function updateSubmitState() {
    const anyChecked = Array.from(inputs).some((input) => input.checked);
    submitBtn.disabled = !anyChecked;
  }

  inputs.forEach((input) => {
    input.addEventListener("change", updateSubmitState);
  });

  updateSubmitState();
})();
