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
  if (true) {
    $.get({
      url: '/data.json',
      success: (cookielistData) => {
        $.cookielist($.state.endpoints.api, cookielistData, (result) => {
          $.id("[container]").html(result);
        });
      }
    })
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

  $.id("[_]-status").html("Accruing Task Information");
  $.anilist($.state.graphql.initialize, { userId: pageUserId }, (response) => {
    cookielistData.user = response.data.User;
    $.id("[_]-status").html("Fetching Media Lists");
    $.id("[_]-status.name").html("@" + response.data.User.name);

    document.title = response.data.User.name + " - " + $.state.cookielist.SITE

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
  });
}
