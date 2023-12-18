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
  user: "{{ user }}",
};

$.state.options = {
  timezone: $.storage("__timezone") ? $.storage("__timezone") : "UTC",
  time_format: $.storage("__time_format")
    ? $.storage("__time_format")
    : "hh:mm A",
  date_format: $.storage("__date_format")
    ? $.storage("__date_format")
    : "Do MMMM YYYY",
  week_start_day: $.storage("__week_start")
    ? $.storage("__week_start")
    : "Monday",
  ajax_timeout: 60000,
};

$.state.cookielist = {
  AL_CLIENT_ID: "{% env 'AL_CLIENT_ID' %}",
  ANILIST_DEV_ID: "{% env 'ANILIST_DEV_ID' %}",
};

$.state.endpoints = {
  api: "{{ url_for('ApiView:process_data', _external=True) }}",
  register: "{{ url_for('ApiView:register_user', _external=True) }}",
  index: "{{ url_for('AboutView:index', _external=True) }}",
};

$.state.graphql = {
  feedback: `{{ static('graphql/feedback.graphql') }}`,
  search: `{{ static('graphql/search.graphql') }}`,
  user: `{{ static('graphql/user.graphql') }}`,
  queue: `{{ static('graphql/queue.graphql') }}`,
};

if ($.storage("__FLASH_MODE")) {
  $.notification($.storage("__FLASH_MODE"), $.storage("__FLASH_MESSAGE"));
  $.storage("__FLASH_MODE", null);
  $.storage("__FLASH_MESSAGE", null);
}
