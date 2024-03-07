function QueueUpdate(id) {
  if ($.state.session.token) {
    updateProgress(id);
  } else {
    $.notification("inform", "Login before using this feature");
  }
}

function HandleQueueViewChange() {
  if ($.state.__queueState) {
    Object.entries($.state.__queueState.category).forEach(
      ([category, data]) => {
        const category_duration = $(
          '[data-category="' + category + '-duration"]'
        );
        const category_count = $('[data-category="' + category + '-count"]');

        const category_duration_value = Number(
          category_duration.attr("data-value")
        );
        const category_count_value = Number(category_count.attr("data-value"));

        if (category_count_value === 1) {
          $('[data-category="' + category + '-lag"]').html("");
        } else {
          category_count.html(category_count_value - data.count);
        }

        category_duration.html(
          timeFormat(category_duration_value - data.duration)
        );
      }
    );

    Object.entries($.state.__queueState.media).forEach(([id, progress]) => {
      const group = "[container]-queue.group@" + id;

      const queue_active = $.id(group + ".active");
      const queue_inactive = $.id(group + ".inactive");
      const queue_active_text = $.id(group + ".active.progress_text");
      const queue_inactive_text = $.id(group + ".inactive.progress_text");
      const queue_progress_text = $.id(group + ".progress_text");

      const max = Number(queue_active.attr("data-max-progress"));

      const queue_group = $.id(group);
      queue_active.attr("data-progress", progress);
      queue_active_text.html(progress + 1);
      queue_inactive_text.html(progress);
      queue_progress_text.html(progress);

      queue_active.addClass("!hidden");

      if (max !== "none") {
        if (progress >= max) {
          queue_inactive.removeClass("hidden");
          queue_group.removeClass(
            "outline outline-[3px] outline-rose-500 hover:outline-rose-600"
          );
        } else {
          queue_active.removeClass("!hidden");
        }
      } else {
        queue_active.removeClass("!hidden");
      }
    });
  }
}

function updateProgress(id) {
  const group = "[container]-queue.group@" + id;

  const queue_group = $.id(group);
  const queue_active = $.id(group + ".active");
  const queue_inactive = $.id(group + ".inactive");
  const queue_progress_text = $.id(group + ".progress_text");
  const queue_active_text = $.id(group + ".active.progress_text");
  const queue_inactive_text = $.id(group + ".inactive.progress_text");
  const queue_spinner = $.id(group + ".spinner");

  const progress = Number(queue_active.attr("data-progress")) + 1;
  const max = Number(queue_active.attr("data-max-progress"));
  const category = queue_group.attr("data-target-category");

  const category_duration = $('[data-category="' + category + '-duration"]');
  const category_count = $('[data-category="' + category + '-count"]');

  const category_duration_value = Number(category_duration.attr("data-value"));
  const category_count_value = Number(category_count.attr("data-value"));

  if ($.state.__queueState) {
    if (!$.state.__queueState.category[category]) {
      $.state.__queueState.category[category] = {
        count: 0,
        duration: 0,
      };
    }
  } else {
    $.state.__queueState = {
      media: {},
      category: {},
    };
    $.state.__queueState.category[category] = {
      count: 0,
      duration: 0,
    };
  }

  $.state.__queueState.category[category].count =
    $.state.__queueState.category[category].count + 1;

  queue_active.addClass("!hidden");
  queue_spinner.addClass("!flex");

  $.anilist(
    $.state.graphql.queue,
    {
      mediaId: Number(queue_active.attr("data-media-id")),
      progress: progress,
    },
    (response) => {
      $.state.__queueState.media[queue_active.attr("data-media-id")] = progress;

      queue_active.attr("data-progress", progress);
      queue_active_text.html(progress + 1);
      queue_inactive_text.html(progress);
      queue_progress_text.html(progress);
      queue_spinner.removeClass("!flex");

      if (category_count_value === 1) {
        $('[data-category="' + category + '-lag"]').html("");
      } else {
        category_count.html(
          category_count_value - $.state.__queueState.category[category].count
        );
      }

      $.state.__queueState.category[category].duration =
        $.state.__queueState.category[category].duration +
        response.data.SaveMediaListEntry.media.duration;

      if (max !== "none") {
        category_duration.html(
          timeFormat(
            category_duration_value -
              $.state.__queueState.category[category].duration
          )
        );
      }

      if (max !== "none") {
        if (progress >= max) {
          queue_inactive.removeClass("hidden");
          queue_group.removeClass(
            "outline outline-[3px] outline-rose-500 hover:outline-rose-600"
          );
        } else {
          queue_active.removeClass("!hidden");
        }
      } else {
        queue_active.removeClass("!hidden");
      }
    }
  );
}

function timeFormat(__minutes) {
  const __seconds = __minutes * 60;
  const day = Math.floor(__seconds / (3600 * 24));
  const hour = Math.floor((__seconds / 3600) % 24);
  const minute = Math.floor((__seconds % 3600) / 60);

  return day > 0
    ? `${day}d ${hour + (minute > 30 ? 1 : 0)}h`
    : hour > 0
    ? `${hour}h ${minute}m`
    : `${minute}m`;
}
