// Làm nền tăng dần: không có gsap thì trang giữ nguyên, không có class "js".
(function () {
  if (!window.gsap) return;
  document.documentElement.classList.add("js");

  function shouldAnimate() {
    var mq = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
    return !(mq && mq.matches);
  }

  function heroIntro() {
    var tl = gsap.timeline({ defaults: { duration: 0.6, ease: "power2.out" } });
    tl.from("#hero h1", { opacity: 0, y: 24, clearProps: "opacity,transform" })
      .from("#hero .hero-hinh", { opacity: 0, y: 24, clearProps: "opacity,transform" }, "-=0.3");
    return tl;
  }

  // Nút vui: không JS thì nút giữ thuộc tính hidden (không là nút chết).
  function setupToggle() {
    var btn = document.getElementById("luoi-nut");
    if (!btn) return;
    var xanh = document.querySelector("#hero .ghe-xanh");
    var doo = document.querySelector("#hero .ghe-do");
    var ly = document.querySelector("#hero .ly");
    function apply(on) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      btn.textContent = on
        ? btn.getAttribute("data-on") || "Đang lười giúp…"
        : btn.getAttribute("data-off") || "Bấm thử cho vui";
      var move = shouldAnimate() ? gsap.to : gsap.set;
      function opts(o) {
        return shouldAnimate() ? Object.assign({ duration: 0.4, ease: "power2.out" }, o) : o;
      }
      move(xanh, opts({ x: on ? 16 : 0 }));
      move(doo, opts({ x: on ? -16 : 0 }));
      move(ly, opts({ y: on ? -8 : 0 }));
    }
    btn.addEventListener("click", function () {
      apply(btn.getAttribute("aria-pressed") !== "true");
    });
    btn.hidden = false;
  }
  setupToggle();

  window.lazySite = { shouldAnimate: shouldAnimate };
  window.lazySite.heroTimeline = shouldAnimate() ? heroIntro() : null;
})();
