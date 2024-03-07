(function ($) {
  $.state = {};
})(jQuery);

(function ($) {
  $.id = function (id) {
    return $("#" + $.escapeSelector(id));
  };
})(jQuery);

(function ($) {
  $.popup = function (url) {
    let method = $.storage("__popup_method") || $.state.options.popup_method;
    if (method === "popup") {
      let window_options =
        "toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes,resizable=no,copyhistory=no";
      var window_width = window.innerWidth / 1.5;
      var window_height = window.innerHeight / 1.3;
      var window_left =
        window.innerWidth / 2 -
        window_width / 2 +
        (screen.width - window.innerWidth);
      var window_top =
        window.innerHeight / 2 -
        window_height / 2 +
        (screen.height / 2 - window.innerHeight / 2);
      window_options =
        window_options +
        ",width=" +
        window_width +
        ",height=" +
        window_height +
        ",top=" +
        window_top +
        ",left=" +
        window_left;
      return window.open(url, "popup", window_options);
    }
    if (method === "blank") {
      window.open(url, "_blank");
    }
    if (method === "parent") {
      window.open(url, "_self");
    }
  };
})(jQuery);

(function ($) {
  $.unescapeString = function (string) {
    return string
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&");
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
  $.mustache = function (template, variables = {}) {
    var template_string;
    if ($.type(template) === "string") {
      template_string = template;
    } else {
      template_string = $.unescapeString(template.html());
    }
    return Mustache.render(template_string, variables, {}, ["<%", "%>"]);
  };
})(jQuery);

(function ($) {
  $.fn.mustache = function (template, variables = {}) {
    this.html($.mustache(template, variables));
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
  $.anilist = function (
    query,
    variables = {},
    onsuccess = () => {},
    onerror = () => {}
  ) {
    var headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if ($.state.session.token) {
      headers["Authorization"] = "Bearer " + $.state.session.token;
    }

    return $.ajax({
      url: "https://graphql.anilist.co",
      method: "POST",
      timeout: $.state.options.ajax_timeout,
      headers: headers,
      data: JSON.stringify({ query: query, variables: variables }),
      error: (jqXHR, textStatus, errorThrown) => {
        AjaxError(jqXHR, textStatus, errorThrown);
        onerror();
      },
      success: onsuccess,
    });
  };
})(jQuery);

(function ($) {
  $.cookielist = function (
    url,
    data = {},
    onsuccess = () => {},
    onerror = () => {},
    method = "POST"
  ) {
    return $.ajax({
      url: url,
      method: method,
      timeout: $.state.options.ajax_timeout,
      headers: {
        "Content-Type": "application/json",
        Accept: "text/html,application/json,*/*;q=0.8",
      },
      data: JSON.stringify(data),
      error: (jqXHR, textStatus, errorThrown) => {
        AjaxError(jqXHR, textStatus, errorThrown);
        onerror();
      },
      success: onsuccess,
    });
  };
})(jQuery);
