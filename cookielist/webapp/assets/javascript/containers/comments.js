$.state.__comments = {
  details: null,
  comments: [],
  load: true,
  page: 0,
  next: true,
};

var __relative_time_format = new Intl.RelativeTimeFormat("en", {
  numeric: "auto",
});

var __relative_time_format_units = {
  year: 24 * 60 * 60 * 1000 * 365,
  month: (24 * 60 * 60 * 1000 * 365) / 12,
  day: 24 * 60 * 60 * 1000,
  hour: 60 * 60 * 1000,
  minute: 60 * 1000,
  second: 1000,
};

const mustache_functions = {
  isOwner() {
    return $.state.__comments.details.userId === this.user.id;
  },
  commentedAgo() {
    var elapsed = this.createdAt * 1000 - +new Date();
    for (var unit in __relative_time_format_units) {
      if (
        Math.abs(elapsed) > __relative_time_format_units[unit] ||
        unit == "second"
      ) {
        return __relative_time_format.format(
          Math.round(elapsed / __relative_time_format_units[unit]),
          unit
        );
      }
    }
  },
};

function filterHTML(html) {
  var element = $(html);
  element.find("a").each(function () {
    var elm = $(this);
    if (elm.attr("href")) {
      elm.attr("onclick", "$.popup('" + elm.attr("href") + "')");
    }
    elm.attr("href", null);
    elm.attr("target", null);
  });
  element.find("img").each(function () {
    var elm = $(this);
    if (!elm.attr("data-src")) {
      elm.attr("data-src", elm.attr("src"));
      elm.attr("lazyload", "");
      elm.attr("src", null);
    }
  });
  return element;
}

function renderAndAppendComments(comments) {
  const comments_section = $.id("[container]-comments.section.comments");
  const template = $.id("[container]-comments@template.comment");
  var __header_added = false;
  for (var i = 0; i < comments.length; i++) {
    var comment = comments[i];
    comment["fn"] = mustache_functions;
    if (comments_section.attr("data-initial-comment") === "true") {
      $.state.__comments.details["fn"] = mustache_functions;
      comments_section.html(
        filterHTML($.mustache(template, $.state.__comments.details))
      );
      delete $.state.__comments.details["fn"];
      comments_section.append(filterHTML($.mustache(template, comment)));
      comments_section.attr("data-initial-comment", "false");
      __header_added = true;
    } else {
      comments_section.append(filterHTML($.mustache(template, comment)));
    }
  }
  if (!__header_added) {
    $.state.__comments.details["fn"] = mustache_functions;
    comments_section.html(
      filterHTML($.mustache(template, $.state.__comments.details))
    );
    delete $.state.__comments.details["fn"];
    comments_section.attr("data-initial-comment", "false");
  }
  $.id("[container]-comments.loading").remove();
  $("img[lazyload]").lazyload();
}

function updateDetails() {
  const details_section = $.id("[container]-comments.details");
  if (details_section.attr("data-initial-update") === "true") {
    $.state.__comments.details.replyCount++;
    details_section.mustache(
      $.id("[container]-comments@template.details"),
      $.state.__comments.details
    );
    details_section.attr("data-initial-update", "false");
  } else {
    null;
  }
}

function InitializeCommentsSection(activity_id) {
  const populateComments = () => {
    $.state.__comments.load = false;
    $.anilist(
      $.state.graphql.comment,
      { activity: activity_id, page: $.state.__comments.page + 1 },
      (response) => {
        $.state.__comments.details = response.data.activity;
        $.state.__comments.comments.push(
          ...response.data.replies.activityReplies
        );
        renderAndAppendComments(response.data.replies.activityReplies);
        $.state.__comments.load = true;
        $.state.__comments.page = response.data.replies.pageInfo.currentPage;
        $.state.__comments.next = response.data.replies.pageInfo.hasNextPage;
        updateDetails();
      }
    );
  };

  if ($.state.__comments.details === null) {
    populateComments();
  } else {
    renderAndAppendComments($.state.__comments.comments);
    updateDetails();
  }

  const section = $.id("[container]-comments.section");

  section.scroll(function () {
    var section_scroll_top = section.scrollTop();
    if (
      section_scroll_top + section.height() / 10 >=
        section.get(0).scrollHeight - section.get(0).clientHeight &&
      $.state.__comments.load &&
      $.state.__comments.next
    ) {
      $.id("[container]-comments.section.comments").append(
        $.id("[container]-comments@template.loading").html()
      );
      populateComments();
    }

    const details_section = $.id("[container]-comments.details");
    if (section_scroll_top === 0) {
      details_section
        .removeClass("animate__animated animate__fadeOut hidden")
        .addClass("animate__animated animate__fadeIn");
      setTimeout(() => {
        details_section.removeClass("hidden");
      }, 500);
    } else {
      details_section
        .removeClass("animate__animated animate__fadeIn")
        .addClass("animate__animated animate__fadeOut");
      setTimeout(() => {
        details_section.addClass("hidden");
      }, 500);
    }
  });
}