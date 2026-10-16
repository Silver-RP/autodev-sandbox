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

  window.lazySite = { shouldAnimate: shouldAnimate };
  window.lazySite.heroTimeline = shouldAnimate() ? heroIntro() : null;
})();
