// Làm nền tăng dần: không có gsap thì trang giữ nguyên, không có class "js".
(function () {
  if (!window.gsap) return;
  document.documentElement.classList.add("js");
})();
