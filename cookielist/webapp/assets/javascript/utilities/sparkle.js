function AnimateSparkle() {
  let index = 0;
  const interval = 1000;

  const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

  const animate = (star) => {
    $(star).css("--star-left", `${rand(-10, 100)}%`);
    $(star).css("--star-top", `${rand(-40, 80)}%`);

    $(star).css("animation", "none");
    $(star).get(0).offsetHeight;
    $(star).css("animation", "");
  };

  $(".sparkle-icon").each(function () {
    setTimeout(() => {
      animate(this);
      setInterval(() => animate(this), 1000);
    }, index++ * (interval / 3));
  });
}
