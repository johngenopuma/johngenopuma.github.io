// Category filters, the photo lightbox, and the contact form.

// Filters: show only photos tagged with the chosen category.
document.querySelectorAll(".filters button").forEach(function (button) {
  button.addEventListener("click", function () {
    var tag = button.dataset.filter;
    document.querySelectorAll(".filters button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b === button));
    });
    document.querySelectorAll(".gallery figure").forEach(function (fig) {
      fig.hidden = tag !== "all" && fig.dataset.tag !== tag;
    });
  });
});

// Lightbox: opens any photo link inside [data-lightbox]; arrows, keys and
// swipes step through the photos currently visible.
(function () {
  var box = document.querySelector(".lightbox");
  if (!box) return;
  var img = box.querySelector("img");
  var title = box.querySelector("strong");
  var caption = box.querySelector("figcaption span");
  var links = [];
  var current = 0;

  function show(i) {
    current = (i + links.length) % links.length;
    var a = links[current];
    img.src = a.href;
    img.alt = a.querySelector("img").alt;
    title.textContent = a.dataset.title || "";
    caption.textContent = a.dataset.caption || "";
    var next = links[(current + 1) % links.length];
    new Image().src = next.href;
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-lightbox] a");
    if (!a || e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    links = Array.prototype.filter.call(
      document.querySelectorAll("[data-lightbox] a"),
      function (l) { return !l.closest("[hidden]"); });
    show(links.indexOf(a));
    box.showModal();
  });

  box.querySelector(".lb-close").addEventListener("click", function () { box.close(); });
  box.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
  box.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
  box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
  box.addEventListener("close", function () {
    // The close event is async; skip if a photo was reopened in the meantime.
    if (!box.open) img.removeAttribute("src");
  });
  box.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") show(current - 1);
    if (e.key === "ArrowRight") show(current + 1);
  });

  var startX = null;
  box.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 40) show(current + (dx < 0 ? 1 : -1));
    startX = null;
  });
})();

// Contact form: send without leaving the page; a plain POST still works
// without JavaScript.
(function () {
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = form.querySelector(".status");
  var button = form.querySelector("button[type=submit]");

  // "Book a shoot" chips jump here with that shoot type picked.
  document.querySelectorAll("[data-shoot]").forEach(function (a) {
    a.addEventListener("click", function () { form.elements.shoot.value = a.dataset.shoot; });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    button.disabled = true;
    status.textContent = "Sending…";
    fetch(form.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {
      method: "POST",
      headers: { Accept: "application/json" },
      body: new FormData(form)
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (String(d.success) !== "true") throw new Error(d.message);
        form.reset();
        status.textContent = "Thanks! Your message was sent.";
      })
      .catch(function () {
        status.textContent = "Sorry, that didn't send. Please try again, or email gracegilhool@gmail.com.";
      })
      .then(function () { button.disabled = false; });
  });
})();
