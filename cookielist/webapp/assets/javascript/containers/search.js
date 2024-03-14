$.state.__search_ajax_request = null;

function _delay_search(fn, ms = 500) {
  let timer = 0;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(fn.bind(this, ...args), ms || 0);
  };
}

function setSearchResult(response) {
  if (
    response === null ||
    (response.data.Users.users.length === 0 &&
      response.data.Anime.media.length === 0 &&
      response.data.Manga.media.length === 0)
  ) {
    $.storage("__last_search_term", null);
    $.id("[container]-search.search_results_container").mustache(
      $.id("[container]-search@template.search_empty")
    );
  } else {
    $.id("[container]-search.search_results_container").mustache(
      $.id("[container]-search@template.search_results"),
      {
        users: response.data.Users.users,
        anime: response.data.Anime.media,
        manga: response.data.Manga.media,
        fn: {
          mediaTitle() {
            return $.state._modal_mustache_media_title_functions[
              $.state.options.media_language
            ](this.title);
          },
          toHeading() {
            return (text, render) => {
              return render(text)
                .replace(/_/g, " ")
                .toLowerCase()
                .replace(/(^\w{1})|(\s+\w{1})/g, (letter) =>
                  letter.toUpperCase()
                );
            };
          },
          isUserDev() {
            return (
              Number($.state.cookielist.ANILIST_DEV_ID) === Number(this.id)
            );
          },
        },
      }
    );
    $("img[lazyload]").lazyload();
  }
}

function searchQuery(search) {
  if ($.state.__search_ajax_request !== null) {
    $.state.__search_ajax_request.abort();
  }
  $.state.__search_ajax_request = $.anilist(
    $.state.graphql.search,
    { search: search },
    (response) => {
      $.state.__userSearchResults = response;
      $.state.__search_ajax_request = null;
      setSearchResult(response);
    }
  );
}

function SearchInitialize() {
  const last_search = $.storage("__last_search_term");
  if (last_search) {
    if ($.state.__userSearchResults) {
      setSearchResult($.state.__userSearchResults);
    } else {
      searchQuery(last_search);
    }
    $.id("[container]-search.search_box").val(last_search);
  }

  $.id("[container]-search.search_box").keyup(
    _delay_search(() => {
      const search = $.id("[container]-search.search_box").val().trim();
      searchQuery(search);
      $.storage("__last_search_term", search);
    })
  );

  $.id("[container]-search.search_button").on("click", () => {
    const search = $.id("[container]-search.search_box").val().trim();
    searchQuery(search);
    $.storage("__last_search_term", search);
  });
}

window.onpopstate = function (e) {
  if (e.state) {
    if (e.state.pageId) {
      $.refresh("show");
    }
  }
};

function searchUser(id, name) {
  $.state.page.id = id;
  $.state.page.user = name;

  $.state.__comments = {
    details: null,
    comments: [],
    load: true,
    page: 0,
    next: true,
  };
  $.state.__queueState = {
    media: {},
    category: {},
  };
  $.state.__badge_templates = {};
  $.state.__badge_options = {};
  $.state.__badge_ajax_request = null;
  $.state.__is_badge_loading = false;
  $.state.__LASTContainerID = undefined;
  $.state.__EntrySwapID = undefined;
  $.state.__mobile_filters = [];
  $.state._modal_window_history = [];
  $.state.__active_schedule_episode = null;
  $.state.__lastModalContainer = null;
  $.id("[_]-search.fraction").html("");
  $.id("[_]-search")
    .removeClass("animate__animated animate__fadeInUp animate__fadeOutDown")
    .addClass("hidden");
  $.state.__search_initialized = false;
  $("[data-search-filter-active]").attr("data-search-filter-active", "false")
  $.id("[_]-search.content").off("focus.search")
  $.id("[_]-search.content").off("blur.search")
  $.id("[_]-search.lock").off("click.search")
  $("[data-search-filter-class]").off("click.search")
  $(document).off("keyup.search")

  let newTitle = "";
  let newURL = "/" + id;
  if ("undefined" !== typeof history.pushState) {
    history.pushState({ pageId: id }, newTitle, newURL);
  } else {
    window.location.assign(newURL);
  }
  $.id("[container]").mustache(
    $.id("[container]-search@template.pre_search_view"),
    {
      user: name,
      id: id,
    }
  );

  ElapseTimer();
  AnimateSparkle();
  FetchAndShowContent(id);
}
