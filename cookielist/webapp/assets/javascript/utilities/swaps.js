function SwapContainer(ContainerID) {
  const container = $.id("[container]@content");
  if ($.state.__LASTContainerID !== ContainerID) {
    const activeCSS =
      "!bg-slate-200 !border-slate-300 hover:!bg-gray-200 hover:!border-gray-300 dark:!bg-slate-950 dark:!border-slate-800 dark:hover:!bg-gray-900 dark:hover:!border-gray-800";
    $.id("[sidebar]-" + $.state.__LASTContainerID).removeClass(activeCSS);
    $.id("[sidebar]-" + ContainerID).addClass(activeCSS);

    $.state.__LASTContainerID = ContainerID;
    container.html($.id("[container]-" + ContainerID).html());
    $("img[lazyload]").lazyload();

    if (
      ContainerID === "anime" ||
      ContainerID === "manga" ||
      ContainerID === "music" ||
      ContainerID === "novel"
    ) {
      $("[data-search-filter-active='true']").each(function () {
        $("." + $(this).attr("data-search-filter-class")).addClass("!hidden");
      });
      if (
        $.state.__search_activated &&
        !$.id("[_]-search").hasClass("animate__fadeInUp")
      ) {
        $.id("[_]-search")
          .removeClass("animate__animated animate__fadeOutDown hidden")
          .addClass("animate__animated animate__fadeInUp");
      }
    } else {
      if (
        $.id("[_]-search").hasClass("animate__fadeInUp") &&
        ($.state.__search_locked ||
          $("[data-search-filter-active='true']").length > 0)
      ) {
        $.state.__search_activated = true;
        $.id("[_]-search")
          .removeClass("animate__animated animate__fadeInUp hidden")
          .addClass("animate__animated animate__fadeOutDown");
      } else {
        $.state.__search_activated = false || $.state.__search_activated;
      }
    }
  }
  container.animate({ scrollTop: 0 }, 100);
}

let swapMustacheFunctions = {
  isGroupWatched() {
    return this.group.completedGroupMediaCount == this.group.groupMediaCount;
  },
  secondsToHuman() {
    return (text, render) => {
      let seconds = Number(render(text));
      var num_days = Math.floor(seconds / 86400);
      var num_hours = Math.floor(((seconds % 31536000) % 86400) / 3600);
      var num_minutes = Math.floor(
        (((seconds % 31536000) % 86400) % 3600) / 60
      );
      var num_seconds = (((seconds % 31536000) % 86400) % 3600) % 60;
      if (num_days > 0) {
        if (num_hours > 0) {
          return (
            String(num_days) +
            (num_days === 1 ? " day and " : " days and ") +
            String(num_hours) +
            (num_hours === 1 ? " hour" : " hours")
          );
        }
        return String(num_days) + (num_days === 1 ? " day" : " days");
      }
      if (num_hours > 0) {
        if (num_minutes > 0) {
          return (
            String(num_hours) +
            (num_hours === 1 ? " hour and " : " hours and ") +
            String(num_minutes) +
            (num_minutes === 1 ? " minute" : " minutes")
          );
        }
        return String(num_hours) + (num_hours === 1 ? " hour" : " hours");
      }
      if (num_minutes > 0) {
        if (num_seconds > 0) {
          return (
            String(num_minutes) +
            (num_minutes === 1 ? " minute and " : " minutes and ") +
            String(num_seconds) +
            (num_seconds === 1 ? " second" : " seconds")
          );
        }
        return (
          String(num_minutes) + (num_minutes === 1 ? " minute" : " minutes")
        );
      }
      return String(num_seconds) + (num_seconds === 1 ? " second" : " seconds");
    };
  },
  mediaStatusAction() {
    if (this.isMediaWatched) {
      return "normal";
    }
    if (!this.isMediaAvailableToWatch) {
      return "unavailable";
    }
    if (this.isUserGoingToWatch) {
      return "available";
    }
    if (!this.isMediaWatched) {
      return "not_watching";
    }
    return "normal";
  },
};

function SwapEntryView(ViewID) {
  const entry = $.id("[container]@gutter");
  const group = JSON.parse($.id("[gutter]-block@data." + ViewID).html());
  entry.mustache($.id("[gutter]-block@template"), {
    group: group,
    fn: swapMustacheFunctions,
  });
  entry.animate({ scrollTop: 0 }, 100);
  $("img[lazyload]").lazyload();
}

function CloseSwapEntry() {
  $.id($.state.__EntrySwapID).html($.state.__EntrySwapHTML);
}

function SwapEntryViewMobile(ViewID) {
  if ($.state.__EntrySwapID) {
    $.id($.state.__EntrySwapID).html($.state.__EntrySwapHTML);
  }

  const entry = $.id("[gutter]-content@" + ViewID);

  $.state.__EntrySwapHTML = entry.html();
  $.state.__EntrySwapID = "[gutter]-content@" + ViewID;

  const group = JSON.parse($.id("[gutter]-block@data." + ViewID).html());
  entry.mustache($.id("[gutter]-block@template"), {
    group: group,
    fn: swapMustacheFunctions,
  });
  entry.animate({ scrollTop: 0 }, 100);
  $("img[lazyload]").lazyload();
}

function ShowSchedule(day) {
  const schedule = "[container]-schedule@" + day;
  const animate = "animate__animated animate__fadeIn";

  if (day === $.state.__LastScheduleDay) {
    $.id(schedule).addClass("md:hidden");
    $.id(schedule + ".chevron").removeClass("rotate-180");
    $.state.__LastScheduleDay = null;
  } else {
    if ($.state.__LastScheduleDay) {
      $.id("[container]-schedule@" + $.state.__LastScheduleDay)
        .addClass("md:hidden")
        .removeClass(animate);
      $.id(
        "[container]-schedule@" + $.state.__LastScheduleDay + ".chevron"
      ).removeClass("rotate-180");
    }
    $.state.__LastScheduleDay = day;
    $.id(schedule).addClass(animate).removeClass("md:hidden");
    $.id(schedule + ".chevron").addClass("rotate-180");
  }
}

function searchFilterMobile(object) {
  const element = $(object);
  const active_filter =
    element.attr("data-mobile-search-filter-active") === "true" ? false : true;
  if (active_filter) {
    $("." + element.attr("data-mobile-search-filter-class")).addClass(
      "!hidden"
    );
  } else {
    $("." + element.attr("data-mobile-search-filter-class")).removeClass(
      "!hidden"
    );
  }
  element.attr("data-mobile-search-filter-active", String(active_filter));
  $.state.__mobile_filters = [];
  $("[data-mobile-search-filter-active='true']").each(function () {
    $.state.__mobile_filters.push(
      $(this).attr("data-mobile-search-filter-class")
    );
  });
}

function createSearchDatabase() {
  if (!$.state.__search_database) {
    $.state.__search_database = {};
    const raw_db = JSON.parse($.id("[search]@data").html());
    for (const [mediaType, nameIdPair] of Object.entries(raw_db)) {
      $.state.__search_database[mediaType.toLowerCase()] = new Fuse(
        nameIdPair,
        {
          isCaseSensitive: false,
          includeMatches: true,
          shouldSort: true,
          threshold: 0.5,
          ignoreLocation: true,
          minMatchCharLength: 3,
          keys: [
            {
              name: "name",
              weight: 1,
            },
          ],
        }
      );
    }
  }
}

$.state.__search_locked =
  $.storage("__search_locked") === "true" ? "locked" : false;
$.state.__mobile_filters = [];

function initializeListSearch() {
  $.state.__search_session = {
    session: "",
    update: null,
    focus: false,
    index: 0,
  };
  $.state.__search_history = {
    id: null,
    value: null,
  };
  for (let i = 0; i < $.state.__mobile_filters.length; ++i) {
    $("." + $.state.__mobile_filters[i]).addClass("!hidden");
    $(
      "[data-mobile-search-filter-class='" + $.state.__mobile_filters[i] + "']"
    ).attr("data-mobile-search-filter-active", "true");
  }
  if (!$.state.__search_initialized) {
    $.state.__search_initialized = true;

    if ($.state.__search_locked === "locked") {
      $.id("[_]-search.lock")
        .removeClass("opacity-0")
        .html($.id("[_]-search@template.lock_close").html());
      $.id("[_]-search")
        .addClass("animate__animated animate__fadeInUp")
        .removeClass("hidden");
    }

    $.id("[_]-search.content").on("focus.search", () => {
      $.state.__search_session.focus = true;
    });

    $.id("[_]-search.content").on("blur.search", () => {
      $.state.__search_session.focus = false;
    });

    $.id("[_]-search.lock").on("click.search", () => {
      if ($.state.__search_locked === "locked") {
        $.state.__search_locked = false;
      } else {
        $.state.__search_locked = !$.state.__search_locked;
      }
      $.storage("__search_locked", String($.state.__search_locked));
      if ($.state.__search_locked) {
        $.id("[_]-search.lock")
          .removeClass("opacity-0")
          .html($.id("[_]-search@template.lock_close").html());
      } else {
        $.id("[_]-search.lock")
          .addClass("opacity-0")
          .html($.id("[_]-search@template.lock_open").html());
      }
      if ($.state.__search_session.update === null) {
        $.id("[_]-search")
          .removeClass("animate__animated animate__fadeInUp hidden")
          .addClass("animate__animated animate__fadeOutDown");
      }
    });

    $("[data-search-filter-class]").on("click.search", function () {
      const element = $(this);
      const active_filter =
        element.attr("data-search-filter-active") === "true" ? false : true;
      if (active_filter) {
        $("." + element.attr("data-search-filter-class")).addClass("!hidden");
      } else {
        $("." + element.attr("data-search-filter-class")).removeClass(
          "!hidden"
        );
      }
      element.attr("data-search-filter-active", String(active_filter));
    });

    $(document).on("keyup.search", function (e) {
      if (
        ($.state.__LASTContainerID === "anime" ||
          $.state.__LASTContainerID === "manga" ||
          $.state.__LASTContainerID === "music" ||
          $.state.__LASTContainerID === "novel") &&
        !$.state._modal_window_history.length
      ) {
        if (!$.state.__search_database) {
          $.notification("inform", "Search Database Not Initialized");
          return;
        }
        var word = e.key;
        var navigate = false;
        var valid_input = true;
        if ($.state.__search_session.focus) {
          if (
            e.key === "ArrowRight" ||
            e.key === "ArrowLeft" ||
            e.key === "ArrowDown" ||
            e.key === "ArrowUp"
          ) {
            e.preventDefault();
            valid_input = true;
            navigate = true;
            word = "";
            if (e.key === "ArrowRight" || e.key === "ArrowDown") {
              $.state.__search_session.index++;
            } else {
              $.state.__search_session.index--;
            }
          } else {
            word = $.id("[_]-search.content").val();
            $.state.__search_session.session = "";
            if (word.trim() === "") {
              $.id("[_]-search.search").removeClass(
                "!border-rose-500/50 dark:!border-rose-600/50"
              );
              $.id("[_]-search.fraction").html("");
              valid_input = false;
            }
          }
        } else {
          if (
            !!!~"ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 =-,.'[] \":*!@#&_?(){}".indexOf(
              e.key
            )
          ) {
            valid_input = false;
          }
          if (e.key === "Backspace") {
            word = "";
            valid_input = true;
            if ($.state.__search_session.session === "") {
              $.id("[_]-search.fraction").html("");
              valid_input = false;
            }
            $.state.__search_session.session =
              $.state.__search_session.session.slice(0, -1);
            if ($.state.__search_session.session === "") {
              $.id("[_]-search.fraction").html("");
            }
          }
          if (
            e.key === "ArrowRight" ||
            e.key === "ArrowLeft" ||
            e.key === "ArrowDown" ||
            e.key === "ArrowUp"
          ) {
            valid_input = true;
            navigate = true;
            word = "";
            if (e.key === "ArrowRight" || e.key === "ArrowDown") {
              $.state.__search_session.index++;
            } else {
              $.state.__search_session.index--;
            }
          }
        }
        console.log(e.key);
        if (e.key === "Escape") {
          $.state.__search_session.session = "";
          const _search_menu = $.id("[_]-search");
          if (!_search_menu.hasClass("animate__fadeOutDown")) {
            _search_menu
              .removeClass("animate__animated animate__fadeInUp hidden")
              .addClass("animate__animated animate__fadeOutDown");
          }
          return;
        }
        if (valid_input) {
          const THRESHOLD = 2500;
          const timestamp = new Date().getTime();
          const search_menu = $.id("[_]-search");
          console.log(e.key, word, $.state.__search_session.session);

          if (
            timestamp - $.state.__search_session.update > THRESHOLD &&
            $("#" + $.escapeSelector("[_]-search") + ":hover").length == 0 &&
            !$.state.__search_session.focus &&
            !$.state.__search_locked &&
            $("[data-search-filter-active='true']").length <= 0
          ) {
            $.state.__search_session.session = "";
          }

          $.state.__search_session.session =
            $.state.__search_session.session + word;
          $.state.__search_session.update = timestamp;

          if (navigate && $.state.__search_session.session === "") {
            $.state.__search_session.index = 0;
            return;
          }

          if (!search_menu.hasClass("animate__fadeInUp") && e.key === " ") {
            $.state.__search_session.session = "";
            setTimeout(() => {
              $.id("[_]-search.content").focus();
            }, 20);
          }
          $.id("[_]-search.content").val($.state.__search_session.session);

          if (!search_menu.hasClass("animate__fadeInUp")) {
            search_menu
              .removeClass("animate__animated animate__fadeOutDown hidden")
              .addClass("animate__animated animate__fadeInUp");
          }

          const _close_search_menu = () => {
            const _timestamp = new Date().getTime();
            const _search_menu = $.id("[_]-search");
            const _is_menu_hovered =
              $("#" + $.escapeSelector("[_]-search") + ":hover").length > 0;

            if (
              _timestamp - $.state.__search_session.update > THRESHOLD &&
              !_is_menu_hovered &&
              !$.state.__search_session.focus &&
              !$.state.__search_locked &&
              $("[data-search-filter-active='true']").length <= 0
            ) {
              $.state.__search_session.index = 0;
              $(
                "[search-anchor=" + $.state.__search_history.id + "]>i"
              ).addClass("!bg-transparent");
              setTimeout(() => {
                $("[search-anchor=" + $.state.__search_history.id + "]").html(
                  $.state.__search_history.value
                );
              }, 220);
              $.id("[_]-search.fraction").html("");
              _search_menu
                .removeClass("animate__animated animate__fadeInUp")
                .addClass("animate__animated animate__fadeOutDown");
              if (_search_menu.hasClass("hidden")) {
                setTimeout(() => {
                  _search_menu.removeClass("hidden")
                }, 220)
              }
            } else {
              if (_is_menu_hovered || $.state.__search_session.focus) {
                $.state.__search_session.update = _timestamp - THRESHOLD / 2;
              }
              setTimeout(_close_search_menu, THRESHOLD + 100);
            }
          };
          setTimeout(_close_search_menu, THRESHOLD + 100);

          const matches = $.state.__search_database[
            $.state.__LASTContainerID
          ].search($.state.__search_session.session);

          if ($.state.__search_session.index >= matches.length) {
            $.state.__search_session.index = matches.length - 1;
          }
          if ($.state.__search_session.index < 0) {
            $.state.__search_session.index = 0;
          }

          const match = matches
            ? matches[$.state.__search_session.index]
            : false;

          console.log(JSON.stringify(match));

          if (match && $.state.__search_session.session.trim() !== "") {
            $.id("[_]-search.search").removeClass(
              "!border-rose-500/50 dark:!border-rose-600/50"
            );
            $.id("[_]-search.fraction").html(
              String($.state.__search_session.index + 1) +
                "/" +
                String(matches.length)
            );
            const parent = $.id("[container]@content");
            const child = $.id("[gutter]-content@" + match.item.id);

            let parentHeight = parent.height();
            let childHeight = child.height();
            let parentOffset = parent.scrollTop();
            let childOffset = child.offset();

            const matched_value = match.matches[0].value;
            const matched_indices = match.matches[0].indices;
            var matched_highlight = "";
            let current_index = 0;
            for (let i = 0; i < matched_indices.length; ++i) {
              let start = matched_indices[i][0];
              let end = matched_indices[i][1];
              matched_highlight += matched_value.substring(
                current_index,
                start
              );
              matched_highlight += `<i>${matched_value.substring(
                start,
                end + 1
              )}</i>`;
              current_index = end + 1;
            }
            matched_highlight += matched_value.substring(current_index);
            $("[search-anchor=" + match.item.id + "]").html(matched_highlight);

            if ($.state.__search_history.id !== match.item.id) {
              $("[search-anchor=" + $.state.__search_history.id + "]").html(
                $.state.__search_history.value
              );
            }

            $.state.__search_history.id = match.item.id;
            $.state.__search_history.value = matched_value;

            parent.animate(
              {
                scrollTop:
                  childOffset.top -
                  parentHeight / 2 -
                  childHeight / 2 +
                  parentOffset,
              },
              200
            );

            child
              .css("--animate-duration", "1s")
              .addClass("animate__animated animate__headShake");
            setTimeout(() => {
              child.removeClass("animate__animated animate__headShake");
            }, 1000);
          } else {
            if ($.state.__search_session.session.trim() !== "") {
              $.id("[_]-search.search").addClass(
                "!border-rose-500/50 dark:!border-rose-600/50"
              );
              $.id("[_]-search.fraction").html("0/0");
            }
            $("[search-anchor=" + $.state.__search_history.id + "]>i").addClass(
              "!bg-transparent"
            );
            setTimeout(() => {
              $("[search-anchor=" + $.state.__search_history.id + "]").html(
                $.state.__search_history.value
              );
            }, 220);
          }
        }
      }
    });
  }
}
