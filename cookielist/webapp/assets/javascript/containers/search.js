function setSearchResult(response) {
  $.id("[container]-search.search_results_container").mustache(
    $.id("[container]-search@template.search_results").html(),
    { users: response.data.Page.users }
  );
}

function searchQuery(search) {
  $.anilist($.state.graphql.search, { search: search }, (response) => {
    $.state.__userSearchResults = response;
    setSearchResult(response);
  });
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
  $.id("[container]-search.search_box").keyup(() => {
    const search = $.id("[container]-search.search_box").val();
    searchQuery(search);
    $.storage("__SEARCH", search);
  });
}
