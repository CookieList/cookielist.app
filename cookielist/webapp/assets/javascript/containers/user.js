if (!$.storage("__user_id_name_mapping")) {
  $.storage("__user_id_name_mapping", "[]");
}
$.state.__user_id_mapping_pre_load_raw = JSON.parse(
  $.storage("__user_id_name_mapping")
);
$.state.__user_id_mapping_pre_load = Object.fromEntries(
  $.state.__user_id_mapping_pre_load_raw
);

function calculateFetchPages(response) {
  let pages = 0;

  pages += response.data.User.statistics.anime.count;
  pages += response.data.User.statistics.manga.count;

  const incrementPlanningList = (lists) => {
    for (var i = 0; i < lists.length; i++) {
      if (!lists[i].isCustomList) {
        pages += lists[i].entries.length;
      }
    }
  };

  incrementPlanningList(response.data._anime_planning_chunk_1.lists);
  incrementPlanningList(response.data._anime_planning_chunk_2.lists);
  incrementPlanningList(response.data._anime_planning_chunk_3.lists);
  incrementPlanningList(response.data._anime_planning_chunk_4.lists);
  incrementPlanningList(response.data._anime_planning_chunk_5.lists);
  incrementPlanningList(response.data._manga_planning_chunk_1.lists);
  incrementPlanningList(response.data._manga_planning_chunk_2.lists);
  incrementPlanningList(response.data._manga_planning_chunk_3.lists);

  return response.data._anime_planning_chunk_5.hasNextChunk ||
    response.data._manga_planning_chunk_3.hasNextChunk
    ? null
    : Math.floor(pages / 50) + (pages % 50 > 0 ? 1 : 0);
}

function FetchAndShowContent(pageUserId) {
  if (false) {
    $.get({
      url: "/data.json",
      success: (cookielistData) => {
        $.cookielist($.state.endpoints.api, cookielistData, (result) => {
          $.id("[container]").html(result);
        });
      },
    });
    return;
  }
  var cookielistData = {
    user: null,
    list: [],
    options: {
      timezoneName: $.state.options.timezone,
      timeFormatString: $.state.options.time_format,
      dateFormatString: $.state.options.date_format,
      firstDayOfWeek: $.state.options.week_start_day,
      mediaTitleLanguage: $.state.options.media_language,
      badgeTemplate: $.state.options.badge_template,
    },
  };

  var _user_name_match =
    $.state.__user_id_mapping_pre_load[String(pageUserId)] || false;
  if (_user_name_match) {
    $.id("[_]-status.name").html("@" + _user_name_match);
  }

  $.id("[_]-status").html("Accruing Task Information");
  $.anilist(
    $.state.graphql.initialize,
    {
      userId: pageUserId,
    },
    (response) => {
      cookielistData.user = response.data.User;
      if ($.type($.state.page.user) == "null") {
        $.state.page.user = response.data.User.name;
      }
      $.id("[_]-status").html("Fetching Media Lists");
      $.id("[_]-status.name").html("@" + response.data.User.name);

      if (
        !$.state.__user_id_mapping_pre_load[String(pageUserId)] ||
        $.state.__user_id_mapping_pre_load[String(pageUserId)] !==
          response.data.User.name
      ) {
        $.state.__user_id_mapping_pre_load[String(pageUserId)] =
          response.data.User.name;
        $.state.__user_id_mapping_pre_load_raw.unshift([
          String(response.data.User.id),
          response.data.User.name,
        ]);
        $.storage(
          "__user_id_name_mapping",
          JSON.stringify($.state.__user_id_mapping_pre_load_raw.slice(0, 25))
        );
      }

      document.title =
        response.data.User.name + " - " + $.state.cookielist.SITE;

      var _searched_user_history = [];
      if ($.storage("__searched_users_history")) {
        _searched_user_history = JSON.parse(
          $.storage("__searched_users_history")
        );
        if (
          !_searched_user_history.find(
            (history) => history.id === response.data.User.id
          )
        ) {
          _searched_user_history.unshift({
            name: response.data.User.name,
            id: response.data.User.id,
          });
        }
        $.storage(
          "__searched_users_history",
          JSON.stringify(_searched_user_history.slice(0, 6))
        );
      } else {
        $.storage(
          "__searched_users_history",
          JSON.stringify([
            {
              name: response.data.User.name,
              id: response.data.User.id,
            },
          ])
        );
      }

      // var manifest_parameters = "?";
      // $.each(_searched_user_history.slice(0, 5), (index, history) => {
      //   manifest_parameters += $.param(history) + "&";
      // });
      // $("link[rel='manifest']").attr(
      //   "href",
      //   $.state.endpoints.manifest + manifest_parameters
      // );

      const _expire_date = new Date();
      _expire_date.setTime(_expire_date.getTime() + (7*24*60*60*1000));
      document.cookie = "history=" + JSON.stringify(_searched_user_history.slice(0, 6)) + ";expires=" + _expire_date.toUTCString() + ";path=" + $.state.cookielist.manifest + ";SameSite=Lax"

      const fetch_page_count = calculateFetchPages(response);
      const current_page = 1;
      const fetch_page = (page) => {
        $.anilist(
          $.state.graphql.user,
          {
            userId: pageUserId,
            _page_1st: page,
            _page_2nd: page + 1,
            _page_3rd: page + 2,
            _page_4th: page + 3,
          },
          (response) => {
            cookielistData.list.push(response.data._page_1st.mediaList);
            cookielistData.list.push(response.data._page_2nd.mediaList);
            cookielistData.list.push(response.data._page_3rd.mediaList);
            cookielistData.list.push(response.data._page_4th.mediaList);
            if (fetch_page_count !== null) {
              var percent = ((page + 3) * 100) / fetch_page_count;
              $.id("[_]-status.progress.bar").css(
                "--progress-percentage",
                String(percent) + "%"
              );
            }
            if (response.data._page_4th.pageInfo.hasNextPage) {
              fetch_page(page + 4);
            } else {
              setTimeout(() => {
                $.id("[_]-status.progress").html("");
                $.id("[_]-status").html("Downloading Generated Page");
              }, 500);
              $.cookielist($.state.endpoints.api, cookielistData, (result) => {
                $.id("[container]").html(result);
              });
            }
          }
        );
      };
      if (fetch_page_count === null) {
        $.id("[_]-status.progress").html(
          $.id("[_]-status.progress.null_progress").html()
        );
      } else {
        $.id("[_]-status.progress").html(
          $.id("[_]-status.progress.progress_bar").html()
        );
      }
      fetch_page(current_page);
    }
  );
}

function ElapseTimer() {
  const timer = $.id("[_]-status.time_elapsed");
  var start = new Date().getTime();
  const increment = (amount_ms) => {
    var seconds = String(Math.round((amount_ms / 1000) * 100) / 100);
    if (!seconds.includes(".")) {
      seconds += ".00";
    }
    if (seconds.split(".")[1].length == 1) {
      seconds += "0";
    }
    if ($.id("[_]@elapsed").length > 0) {
      $.id("[_]@elapsed").html("generated in " + seconds + " seconds");
      clearInterval(timer_interval);
      return;
    }
    timer.html(seconds + " seconds elapsed");
  };
  const timer_interval = setInterval(() => {
    var now = new Date().getTime();
    increment(now - start);
  }, 50);
}
