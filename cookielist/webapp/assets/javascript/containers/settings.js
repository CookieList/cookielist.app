function initializeLoginMenu() {
  if ($.state.session.token) {
    $.id("[container]-settings.login_container.login_button")
      .last()
      .html("Logout");
    $.id("[container]-settings.login_container.logged_in_as").mustache(
      $.id("[container]-settings@template.logged_in_user"),
      {
        id: $.state.session.id,
        name: $.state.session.name,
        avatar: $.state.session.avatar,
      }
    );
    $.id("[container]-settings.login_container.login_button")
      .last()
      .addClass(
        "!bg-rose-500/10 hover:!bg-rose-500/20 !border-rose-500/20 hover:!border-rose-500/30 !text-rose-400 dark:!text-rose-500"
      );
    $.id("[container]-settings.login_container.login_button")
      .last()
      .click(() => {
        $.cookielist($.state.endpoints.register, { action: "logout" }, () => {
          $.storage("__FLASH_MODE", "inform");
          $.storage("__FLASH_MESSAGE", "AniList Logout Successful");
          $.refresh();
        });
      });
  } else {
    $.id("[container]-settings.login_container.login_button")
      .last()
      .click(() => {
        $.storage("__URL", window.location);
        setTimeout(
          () =>
            window.location.replace(
              "https://anilist.co/api/v2/oauth/authorize?response_type=token&client_id=" +
                $.state.cookielist.AL_CLIENT_ID
            ),
          150
        );
      });
  }
}

function SetTheme(Theme) {
  const HTML = $("html");
  var change;
  if (Theme === "toggle") {
    if (HTML.hasClass("dark")) {
      change = "light";
    } else {
      change = "dark";
    }
  } else {
    change = Theme;
  }
  $.storage("__site_theme", change);
  document.cookie = "theme=" + change + ";path=/;SameSite=Lax";
  if (change === "dark") {
    HTML.addClass("dark");
  } else {
    HTML.removeClass("dark");
  }
}

function initializeScheduleMenu() {
  const tz_selection = $.id("[container]-settings.timezone_dropdown");
  const time_format_selection = $.id(
    "[container]-settings.time_format_dropdown"
  );
  const date_format_selection = $.id(
    "[container]-settings.date_format_dropdown"
  );
  const start_weekday_selection = $.id(
    "[container]-settings.start_weekday_dropdown"
  );

  if ($.storage("__timezone")) {
    tz_selection.val($.storage("__timezone"));
  } else {
    tz_selection.val("UTC");
  }

  if ($.storage("__time_format")) {
    time_format_selection.val($.storage("__time_format"));
  } else {
    time_format_selection.val("hh:mm A");
  }

  if ($.storage("__date_format")) {
    date_format_selection.val($.storage("__date_format"));
  } else {
    date_format_selection.val("Do MMMM YYYY");
  }

  if ($.storage("__week_start")) {
    start_weekday_selection.val($.storage("__week_start"));
  } else {
    start_weekday_selection.val("Monday");
  }

  tz_selection.on("change", () => {
    $.storage("__timezone", tz_selection.val());
    $.refresh("show");
  });

  time_format_selection.on("change", () => {
    $.storage("__time_format", time_format_selection.val());
    $.refresh("show");
  });

  date_format_selection.on("change", () => {
    $.storage("__date_format", date_format_selection.val());
    $.refresh("show");
  });

  start_weekday_selection.on("change", () => {
    $.storage("__week_start", start_weekday_selection.val());
    $.refresh("show");
  });
}

function initializeInterfaceMenu() {
  const media_language_selection = $.id(
    "[container]-settings.media_language_dropdown"
  );
  const external_link_selection = $.id(
    "[container]-settings.external_link_dropdown"
  );

  if ($.storage("__media_language")) {
    media_language_selection.val($.storage("__media_language"));
  } else {
    media_language_selection.val("english");
  }
  if ($.storage("__popup_method")) {
    external_link_selection.val($.storage("__popup_method"));
  } else {
    external_link_selection.val("popup");
  }

  media_language_selection.on("change", () => {
    $.storage("__media_language", media_language_selection.val());
    $.refresh("show");
  });
  external_link_selection.on("change", () => {
    $.storage("__popup_method", external_link_selection.val());
  });
}

function InitializeSettings() {
  initializeLoginMenu();
  initializeScheduleMenu();
  initializeInterfaceMenu();
}
