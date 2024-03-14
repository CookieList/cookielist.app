$.state.session = {
  id: "{{ session.id }}",
  name: "{{ session.name }}",
  avatar: "{{ session.avatar }}",
  token: "{{ session.token }}",
  username: "{{ session.CL_USERNAME }}",
  password: "{{ session.CL_PASSWORD }}",
  key: "{{ session.CL_ADMIN_TOKEN }}",
};

$.state.page = {
  id: "{{ id }}",
  user: "",
  session_id: "{{ g.session_id }}",
};

$.state.cookielist = {
  AL_CLIENT_ID: "{{ env.int('AL_CLIENT_ID') }}",
  ANILIST_DEV_ID: "{{ env.int('ANILIST_DEV_ID') }}",
  BADGE_DEFAULT: "{{ env.string('COOKIELIST_DEFAULT_BADGE_TEMPLATE') }}",
  BADGE_SERVERS: "{{ env.string('COOKIELIST_BADGE_SERVERS') }}"
    .replace(/\s/g, "")
    .split(","),
  SITE: "{{ SITE_NAME }}",
  manifest: "{{ url_for('AboutView:webmanifest') }}",
};

$.state.options = {
  timezone: $.storage("__timezone")
    ? $.storage("__timezone")
    : Intl.DateTimeFormat().resolvedOptions().timeZone,
  time_format: $.storage("__time_format")
    ? $.storage("__time_format")
    : "hh:mm A",
  date_format: $.storage("__date_format")
    ? $.storage("__date_format")
    : "Do MMMM YYYY",
  week_start_day: $.storage("__week_start")
    ? $.storage("__week_start")
    : "Monday",
  media_language: $.storage("__media_language")
    ? $.storage("__media_language")
    : "english",
  ajax_timeout: 60000,
  popup_method: $.storage("__popup_method")
    ? $.storage("__popup_method")
    : "popup",
  badge_template: $.storage("__last_select_badge_template")
    ? $.storage("__last_select_badge_template")
    : $.state.cookielist.BADGE_DEFAULT,
};

$.state.endpoints = {
  api: window.location.origin + "{{ url_for('ApiView:process') }}",
  register: window.location.origin + "{{ url_for('ApiView:login') }}",
  index: window.location.origin + "{{ url_for('AboutView:index') }}",
  manifest: window.location.origin + "{{ url_for('AboutView:webmanifest') }}",
};

$.state.graphql = {
  feedback: `{{ static('graphql/feedback.graphql') }}`,
  search: `{{ static('graphql/search.graphql') }}`,
  initialize: `{{ static('graphql/initialize.graphql') }}`,
  user: `{{ static('graphql/user.graphql') }}`,
  queue: `{{ static('graphql/queue.graphql') }}`,
  media: `{{ static('graphql/media.graphql') }}`,
  favourite: `{{ static('graphql/favourite.graphql') }}`,
  status: `{{ static('graphql/status.graphql') }}`,
  update: `{{ static('graphql/update.graphql') }}`,
  delete: `{{ static('graphql/delete.graphql') }}`,
  comment: `{{ static('graphql/comment.graphql') }}`,
};

if ($.storage("__FLASH_MODE")) {
  $.notification($.storage("__FLASH_MODE"), $.storage("__FLASH_MESSAGE"));
  $.storage("__FLASH_MODE", null);
  $.storage("__FLASH_MESSAGE", null);
}

CookiePopup($.storage("__cookies"));

if (!$.storage("__site_theme")) {
  if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    $.storage("__site_theme", "dark");
  } else {
    $.storage("__site_theme", "light");
  }
  SetTheme($.storage("__site_theme"));
  document.cookie =
    "theme=" + $.storage("__site_theme") + ";path=/;SameSite=Lax";
}

if (!$.storage("__timezone")) {
  $.storage("__timezone", $.state.options.timezone);
}

$(document).keydown(function (e) {
  if (e.key == "\\") {
    SetTheme("toggle");
  }
});

if (navigator.serviceWorker) {
  $(document).ready(() => {
    navigator.serviceWorker.register(
      "{{ url_for('static', filename='sw.js') }}",
      { scope: "/" }
    );
  });
}
