function CookiePopup(choice) {
  if (choice === "yes") {
    $.storage("__cookies", "allowed");
    if ($.id("[container]").length) {
      $.id("[_]-cookies-notice").addClass(
        "animate__animated animate__fadeOutLeft animate__faster"
      );
      setTimeout(() => {
        $.id("[_]-cookies-notice").addClass("!hidden").removeClass("fixed");
      }, 500);
    } else {
      $.refresh();
    }
  } else if (choice === "no") {
    $.storage("__cookies", "no");
    $.id("[container]").remove();
    $.id("[_]-cookies-notice")
      .removeClass("hidden")
      .addClass(
        "fixed !top-1/2 !left-1/2 transform -translate-x-1/2 -translate-y-1/2 transition-all w-11/12"
      );
  } else if (choice === "allowed") {
  } else {
    $.id("[_]-cookies-notice").addClass("fixed").removeClass("hidden");
  }
}
