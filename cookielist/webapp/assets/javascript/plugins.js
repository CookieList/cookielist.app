(function ($) {
  $.state = {};
})(jQuery);

(function ($) {
  $.id = function (id) {
    return $("#" + $.escapeSelector(id));
  };
})(jQuery);

(function ($) {
  $.refresh = function (state) {
    if (state === "show") {
      $.id("[_]-refresh")
        .removeClass("hidden animate__animated animate__fadeOutLeft")
        .addClass("flex animate__animated animate__fadeInLeft");
    } else if (state === "hide") {
      $.id("[_]-refresh")
        .removeClass("animate__animated animate__fadeInLeft")
        .addClass("animate__animated animate__fadeOutLeft");
    } else {
      window.location.reload();
    }
  };
})(jQuery);

(function ($) {
  $.notification = function (mode, content, duration = 2600) {
    const entryAnimation = "fadeInDown";
    const exitAnimation = "fadeOutUpBig";

    $.id("[notification]-" + mode + ".content").html(content);
    $.id("[notification]-" + mode)
      .removeClass("hidden animate__animated animate__" + exitAnimation)
      .addClass("!flex animate__animated animate__" + entryAnimation);

    setTimeout(() => {
      $.id("[notification]-" + mode)
        .removeClass("animate__animated animate__" + entryAnimation)
        .addClass("animate__animated animate__" + exitAnimation);
    }, duration);
  };
})(jQuery);

(function ($) {
  $.fn.mustache = function (template, variables = {}) {
    this.html(Mustache.render(template, variables));
    return this;
  };
})(jQuery);

(function ($) {
  $.storage = function (key, value = false) {
    if (value) {
      localStorage.setItem(key, value);
    } else if ($.type(value) == "null") {
      localStorage.removeItem(key);
    } else {
      return localStorage.getItem(key);
    }
  };
})(jQuery);

(function ($) {
  $.anilist = function (query, variables = {}, onsuccess = () => {}) {
    var headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if ($.state.session.token) {
      headers["Authorization"] = "Bearer " + $.state.session.token;
    }

    $.post({
      url: "https://graphql.anilist.co",
      timeout: $.state.options.ajax_timeout,
      headers: headers,
      data: JSON.stringify({ query: query, variables: variables }),
      error: (jqXHR, textStatus, errorThrown) => {
        AjaxError(jqXHR, textStatus, errorThrown);
      },
      success: onsuccess,
    });
  };
})(jQuery);

(function ($) {
  $.cookielist = function (url, data = {}, onsuccess = () => {}) {
    $.post({
      url: url,
      timeout: $.state.options.ajax_timeout,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      data: JSON.stringify(data),
      error: (jqXHR, textStatus, errorThrown) => {
        AjaxError(jqXHR, textStatus, errorThrown);
      },
      success: onsuccess,
    });
  };
})(jQuery);
