function FetchAndShowContent() {
  $.id("[_]-status").html("Fetching Manga List");
  $.anilist(
    $.state.graphql.user,
    { userId: $.state.page.id, mediaType: "MANGA" },
    (manga) => {
      $.id("[_]-status").html("Fetching Anime List");
      $.anilist(
        $.state.graphql.user,
        { userId: $.state.page.id, mediaType: "ANIME" },
        (anime) => {
          $.id("[_]-status").html("Fetching Processed List");
          $.cookielist(
            $.state.endpoints.api,
            {
              anime: anime,
              manga: manga,
              options: {
                timezone: $.state.options.timezone,
                time_format: $.state.options.time_format,
                date_format: $.state.options.date_format,
                week_start_day: $.state.options.week_start_day,
              },
            },
            (result) => {
              $.id("[container]").html(result);
            }
          );
        }
      );
    }
  );
}
