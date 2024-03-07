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
  AL_CLIENT_ID: "{% env 'AL_CLIENT_ID' %}",
  ANILIST_DEV_ID: "{% env 'ANILIST_DEV_ID' %}",
  BADGE_DEFAULT: "cookielist-default",
  SITE: "{{ SITE_NAME }}",
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
  badge_template: $.storage("__badge_template")
    ? $.storage("__badge_template")
    : $.state.cookielist.BADGE_DEFAULT,
};

$.state.endpoints = {
  api: window.location.origin + "{{ url_for('ApiView:process_data') }}",
  register: window.location.origin + "{{ url_for('ApiView:register_user') }}",
  index: window.location.origin + "{{ url_for('AboutView:index') }}",
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

CookiePopup($.storage("__COOKIES"));

if (!$.storage("__THEME")) {
  if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    $.storage("__THEME", "dark");
  } else {
    $.storage("__THEME", "light");
  }
  SetTheme($.storage("__THEME"));
}

if (!$.storage("__timezone")) {
  $.storage("__timezone", $.state.options.timezone);
}

$(document).keydown(function (e) {
  if (e.key == "\\") {
    SetTheme("toggle");
  }
});
