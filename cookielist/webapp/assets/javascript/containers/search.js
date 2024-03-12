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
    $.storage("__SEARCH", null);
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
  const last_search = $.storage("__SEARCH");
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
      $.storage("__SEARCH", search);
    })
  );

  $.id("[container]-search.search_button").on("click", () => {
    const search = $.id("[container]-search.search_box").val().trim();
    searchQuery(search);
    $.storage("__SEARCH", search);
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
  $.state.__LASTContainerID = null;
  ElapseTimer();
  AnimateSparkle();
  FetchAndShowContent(id);
}
