(function () {
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll("[data-easter-snurki]").forEach(function (card) {
    var audio = card.querySelector("[data-easter-audio]");
    var playing = false;
    var cooldown = false;

    function playOnce() {
      if (!audio || reduced || cooldown) return;
      cooldown = true;
      try {
        audio.currentTime = 0;
        var p = audio.play();
        if (p && p.catch) p.catch(function () {});
        playing = true;
      } catch (e) {}
      window.setTimeout(function () {
        cooldown = false;
      }, 1200);
    }

    function stopAudio() {
      if (!audio || !playing) return;
      try {
        audio.pause();
        audio.currentTime = 0;
      } catch (e) {}
      playing = false;
    }

    card.addEventListener("mouseenter", function () {
      card.classList.add("is-easter-on");
      playOnce();
    });
    card.addEventListener("mouseleave", function () {
      card.classList.remove("is-easter-on");
      stopAudio();
    });
    card.addEventListener("focusin", function () {
      card.classList.add("is-easter-on");
      playOnce();
    });
    card.addEventListener("focusout", function (e) {
      if (!card.contains(e.relatedTarget)) {
        card.classList.remove("is-easter-on");
        stopAudio();
      }
    });
  });
})();
