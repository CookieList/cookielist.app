$.state.__badge_templates = {};
$.state.__badge_options = {};
$.state.__badge_ajax_request = null;
$.state.__is_badge_loading = false;

function InitializeProfilePage() {
  if ($.state.__badge_ajax_request !== null) {
    $.state.__badge_ajax_request.abort();
  }

  $.state.__page_badge_data = JSON.parse(
    $.id("[container]-profile.status_badge_data").html()
  );
  $.state.__page_user_options = JSON.parse(
    $.id("[container]-profile.user_options").html()
  );

  $("[data-badge-snippet]").each(function () {
    const element = $(this);
    element.html(
      $.mustache(_snippet_mustache(element.attr("data-badge-snippet")), {
        pageUrl: window.location.origin + window.location.pathname,
        badgeUrl: location.protocol + "//__generating_svg_uri__/",
      })
    );
  });

  const badge_template_selection = $.id(
    "[container]-settings.badge_template_dropdown"
  );

  if ($.state.__page_user_options.badgeTemplate) {
    badge_template_selection.val($.state.__page_user_options.badgeTemplate);
    changeBadgeTemplate($.state.__page_user_options.badgeTemplate);
  } else if ($.storage("__last_select_badge_template")) {
    var template = $.storage("__last_select_badge_template");
    badge_template_selection.val(template);
    changeBadgeTemplate(template);
    $.storage("__last_select_badge_template", template);
  } else {
    badge_template_selection.val($.state.cookielist.BADGE_DEFAULT);
    changeBadgeTemplate($.state.cookielist.BADGE_DEFAULT);
  }

  badge_template_selection.on("change", () => {
    changeBadgeTemplate(badge_template_selection.val());
  });
}

function _snippet_mustache(snippet_language) {
  return $.unescapeString(
    $.id("[snippet]-language.template@" + snippet_language)
      .html()
      .trim()
  )
    .replace(/&_lt/g, "&lt;")
    .replace(/&_gt/g, "&gt;");
}

function _badge_uri(
  template,
  parameters = {},
  format = "xml-uri",
  json = false
) {
  let server = $.state.__page_badge_data.__server;
  let id = String($.state.page.id);
  let uri = location.protocol + "//" + server + "/";
  if (json) {
    uri += "*/";
  }
  uri += id + "." + format + "?";
  if (typeof parameters !== "object" && parameters === null) {
    parameters = {};
  }
  parameters.template = template;
  uri = uri + $.param(parameters);
  return uri.replace(/\(/g, "%28").replace(/\)/g, "%29");
}

function changeBadgeTemplate(template, resumed = false) {
  $.state.__is_badge_loading = true;
  if (!resumed) {
    $.id("[container]-profile.status_badge").html(
      $.id("[container]-profile@template.badge_loading").html()
    );
  }

  if (!$.state.__has_synced_badge) {
    setTimeout(() => {
      changeBadgeTemplate(template, (resumed = true));
    }, 100);
    return;
  }
  if ($.state.__badge_templates[template]) {
    $.id("[container]-profile.status_badge").html(
      $("<img>").attr("src", $.state.__badge_templates[template])
    );
    $.state.__is_badge_loading = false;
  } else {
    $.cookielist(
      _badge_uri(
        template,
        $.state.__page_badge_data.__options[template],
        "xml-uri",
        (json = true)
      ),
      {},
      (response) => {
        $.state.__badge_templates[template] = response.response;
        $.state.__badge_options[template] = response.options;
        $.id("[container]-profile.status_badge").html(
          $("<img>").attr("src", $.state.__badge_templates[template])
        );
        $.state.__is_badge_loading = false;
      },
      () => {},
      "GET"
    );
  }
  $.id("[snippet]-language.badge_url").html(
    _badge_uri(template, $.state.__page_badge_data.__options[template], "svg")
  );
  $.state.options.badge_template = template;
}

const custom_window_mustache_functions = {
  badgeUrl() {
    return $.state.__badge_templates[$.state.options.badge_template];
  },
  menuTheme() {
    return $.storage("__customize_menu_theme")
      ? $.storage("__customize_menu_theme")
      : "dark";
  },
  badgeTemplate() {
    return $.state.options.badge_template;
  },
  badgeTemplateOptions() {
    return $.state.__badge_options[$.state.options.badge_template];
  },
  languageMode() {
    return $.storage("__customize_menu_snippet")
      ? $.storage("__customize_menu_snippet")
      : "markdown";
  },
  optionValue() {
    var options =
      $.state.__page_badge_data.__options[$.state.options.badge_template];
    if (typeof options === "object" && options !== null) {
      return options[this.id];
    }
  },
  userTemplateOptions() {
    return $.state.__page_user_options.userOptionFormatted;
  },
};

function showCustomizeWindow() {
  if ($.state.__is_badge_loading) {
    $.notification("tell", "Please wait for the badge to be generated.");
    return;
  }
  $.id("[customize]-content").mustache($.id("[customize]@template.content"), {
    badge: $.state.__page_badge_data,
    options: $.state.__page_user_options,
    fn: custom_window_mustache_functions,
  });
  $.id("[customize]")
    .removeClass("animate__animated animate__fadeOut")
    .addClass("animate__animated animate__fadeIn")
    .css("--animate-duration", "0.12s")
    .removeClass("hidden");
}

function InitializeCustomWindow() {
  $("[data-badge-argument]").keyup(
    _delay_badge_update(() => {
      if ($.state.__badge_ajax_request !== null) {
        $.state.__badge_ajax_request.abort();
      }
      updateBadgeArguments();
    })
  );
  $("[data-badge-setting]").keyup(
    _delay_badge_update(() => {
      UpdateCustomizeWindowSettings();
    })
  );
  UpdateCustomizeWindowSnippet();
  UpdateCustomizeWindowSettings();
}

function closeCustomizeWindow() {
  $.id("[customize]")
    .removeClass("animate__animated animate__fadeIn")
    .addClass("animate__animated animate__fadeOut")
    .css("--animate-duration", "0.12s");
  setTimeout(() => {
    $.id("[customize]").addClass("hidden");
    $.id("[customize]-content").html("");
  }, 120);
}

function changeCustomizeWindowTheme(theme) {
  $("[data-customize-menu-theme]").attr("data-customize-menu-theme", theme);
  $.storage("__customize_menu_theme", theme);
}

function _delay_badge_update(fn, ms = 500) {
  let timer = 0;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(fn.bind(this, ...args), ms || 0);
  };
}

function getCustomWindowArguments() {
  var arguments = {};
  arguments["template"] = $.storage("__last_select_badge_template")
    ? $.storage("__last_select_badge_template")
    : $.state.cookielist.BADGE_DEFAULT;

  $("[data-badge-argument]").each((index, element) => {
    value = $(element).val().trim();
    if (value) {
      arguments[$(element).attr("data-badge-argument")] = value;
    }
  });
  return arguments;
}

function updateBadgeArguments() {
  let arguments = getCustomWindowArguments();
  $.id("[customize]-content.badge_image").html(
    $.id("[customize]@template.loading_badge").html()
  );
  $.state.__badge_ajax_request = $.ajax({
    url: _badge_uri($.state.options.badge_template, arguments),
    method: "GET",
    timeout: $.state.options.ajax_timeout,
    error: (jqXHR, textStatus, errorThrown) => {
      if (textStatus !== "abort") {
        AjaxError(jqXHR, textStatus, errorThrown);
      }
    },
    success: (response) => {
      $.state.__badge_ajax_request = null;
      $.id("[customize]-content.badge_image").html(
        $("<img>").attr("src", response)
      );
    },
  });
  UpdateCustomizeWindowSnippet(arguments);
}

function UpdateCustomizeWindowSnippet(arguments = null) {
  $.id("[customize]-snippet@badge").html(
    $.mustache(
      _snippet_mustache(
        $.storage("__customize_menu_snippet")
          ? $.storage("__customize_menu_snippet")
          : "markdown"
      ),
      {
        pageUrl: window.location.origin + window.location.pathname,
        badgeUrl: _badge_uri(
          $.state.options.badge_template,
          arguments !== null ? arguments : getCustomWindowArguments(),
          "svg"
        ),
      }
    )
  );
}

function UpdateCustomizeWindowSettings() {
  var settings = {};

  $("[data-badge-setting]").each((index, element) => {
    value = $(element).val().trim();
    if (value) {
      settings[$(element).attr("data-badge-setting")] = value;
    }
  });

  if (Object.keys(settings).length > 0) {
    $.id("[customize]-snippet@setting").html(
      $.mustache(_snippet_mustache("settings"), {
        settings: JsonURL.stringify(settings, {
          impliedObject: true,
          noEmptyComposite: true,
          AFQ: true,
        }),
      })
    );
  } else {
    $.id("[customize]-snippet@setting").html("");
  }
}

function changeCustomizeMenuSnippetLanguage(language) {
  $("[data-current-snippet-language]").attr(
    "data-current-snippet-language",
    language
  );
  $.storage("__customize_menu_snippet", language);
  UpdateCustomizeWindowSnippet();
}

function changeCustomizeMenuSnippetLanguageMobile(action) {
  const languages = {
    markdown: 0,
    html: 1,
    anilist: 2,
  };
  const current = $.storage("__customize_menu_snippet")
    ? $.storage("__customize_menu_snippet")
    : "markdown";

  var position = languages[current];

  if (action === "previous") {
    position = position - 1;
    if (position < 0) {
      position = 2;
    }
  }
  if (action === "next") {
    position = position + 1;
    if (position > 2) {
      position = 0;
    }
  }

  var language = Object.keys(languages)[position];

  $("[data-current-snippet-language]").attr(
    "data-current-snippet-language",
    language
  );
  $.storage("__customize_menu_snippet", language);
  UpdateCustomizeWindowSnippet();
}

function copyCustomWindowCode() {
  $.id("[customize]-snippet.copy_button").html("Copied...");
  const trace = $("<textarea></textarea>")
    .html(
      "~~~\n" +
        $.id("[customize]-snippet@badge").text() +
        "\n\n" +
        $.id("[customize]-snippet@setting").text() +
        "\n~~~"
    )
    .text();
  ClipboardJS.copy(trace);
  $.notification("tell", "Copied To Clipboard");
  setTimeout(() => {
    $.id("[customize]-snippet.copy_button").html("Copy Code");
  }, 1500);
}
