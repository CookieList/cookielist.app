$.state._modal_response = {};

function HideModal() {
  $.state._modal_window_history = [];
  $.state.__active_schedule_episode = null;
  $.state.__lastModalContainer = null;
  $.id("[modal]")
    .removeClass("animate__animated animate__fadeIn")
    .addClass("animate__animated animate__fadeOut")
    .css("--animate-duration", "0.12s");
  setTimeout(() => {
    $.id("[modal]").addClass("hidden");
    $.id("[modal]-content").html("");
  }, 120);
}

$.state._modal_window_history = [];
$.state._modal_schedule = {
  year: new Date().getFullYear(),
  month: new Date().getMonth(),
};
$.state.__active_schedule_episode = null;

$.state._modal_mustache_media_title_functions = {
  english: (context) => {
    return context.english || context.romaji || context.native;
  },
  romaji: (context) => {
    return context.romaji || context.english || context.native;
  },
  native: (context) => {
    return context.native || context.romaji || context.english;
  },
};

$.state._modal_mustache_functions = {
  toLowerCase() {
    return (text, render) => {
      return render(text).toLowerCase();
    };
  },
  toHeading() {
    return (text, render) => {
      return render(text)
        .replace(/_/g, " ")
        .toLowerCase()
        .replace(/(^\w{1})|(\s+\w{1})/g, (letter) => letter.toUpperCase());
    };
  },
  monthIntToName() {
    return (text, render) => {
      return {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
      }[Number(render(text))];
    };
  },
  numberToLocaleString() {
    return (text, render) => {
      return Number(render(text)).toLocaleString(); // TODO: make locale choose from settings
    };
  },
  styleHidden() {
    return (text, render) => {
      return !Boolean(Number(render(text)));
    };
  },
  scheduleHead() {
    let _today = new Date(
      $.state._modal_schedule.year,
      $.state._modal_schedule.month
    );
    const _months = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    return _months[_today.getMonth()] + " " + String(_today.getFullYear());
  },
  mediaTitle() {
    return $.state._modal_mustache_media_title_functions[
      $.state.options.media_language
    ](this.media.title);
  },
  _context_relationMediaTitle() {
    return $.state._modal_mustache_media_title_functions[
      $.state.options.media_language
    ](this.node.title);
  },
  _context_recommendationMediaTitle() {
    return $.state._modal_mustache_media_title_functions[
      $.state.options.media_language
    ](this.mediaRecommendation.title);
  },
  _context_isRatingPositive() {
    return Number(this.rating) > 0;
  },
  _context_externalSiteLanguage() {
    return (
      {
        Japanese: "JPN",
        English: "ENG",
        Korean: "KOR",
        Italian: "ITA",
        Spanish: "SPA",
        Portuguese: "POR",
        French: "FRE",
        German: "GER",
        Hebrew: "HEB",
        Hungarian: "HUN",
        Chinese: "CHI",
        Arabic: "ARA",
        Filipino: "FIL",
        Catalan: "CAT",
        Finnish: "FIN",
        Turkish: "TUR",
        Dutch: "DUT",
        Swedish: "SWE",
        Thai: "THA",
        Tagalog: "TGL",
        Malaysian: "MSA",
        Indonesian: "IND",
        Vietnamese: "VIE",
        Nepali: "NEP",
        Hindi: "HIN",
        Urdu: "URD",
      }[this.language] || this.language
    );
  },
  _context_isLinkTypeINFO() {
    return this.type === "INFO";
  },
  _context_isLinkTypeSTREAMING() {
    return this.type === "STREAMING";
  },
  _context_isLinkTypeSOCIAL() {
    return this.type === "SOCIAL";
  },
  _context_mediaHashTags() {
    if (!this.media.hashtag) {
      return [];
    }
    return this.media.hashtag.replace(/#/g, "").split(" ");
  },
  _context_isTrailerEmbedYouTube() {
    if (!this.media.trailer) {
      return false;
    }
    return this.media.trailer.site === "youtube";
  },
  _context_getMediaCalender() {
    let datetimeToday = new Date(
      $.state._modal_schedule.year,
      $.state._modal_schedule.month
    );

    let maxAirLimit = new Date(
      Math.max(
        ...this.media.airingSchedule.nodes.map((item) => item.airingAt)
      ) * 1000
    );
    let minAirLimit = new Date(
      Math.min(
        ...this.media.airingSchedule.nodes.map((item) => item.airingAt)
      ) * 1000
    );

    if (datetimeToday >= maxAirLimit) {
      datetimeToday = maxAirLimit;
      $.state._modal_schedule.year = maxAirLimit.getFullYear();
      $.state._modal_schedule.month = maxAirLimit.getMonth();
    } else if (datetimeToday <= minAirLimit) {
      datetimeToday = minAirLimit;
      $.state._modal_schedule.year = minAirLimit.getFullYear();
      $.state._modal_schedule.month = minAirLimit.getMonth();
    } else {
      datetimeToday = datetimeToday;
    }

    let __dateTimeActualToday = new Date();
    let todayYear = datetimeToday.getFullYear();
    let todayMonth = datetimeToday.getMonth();

    let firstDayOfMonth = new Date(todayYear, todayMonth, 1).getDay();
    let lastDayOfMonth = new Date(todayYear, todayMonth + 1, 0).getDate();
    let lastDayOfMonthWeekNumber = new Date(
      todayYear,
      todayMonth,
      lastDayOfMonth
    ).getDay();
    let lastDateOfPreviousMonth = new Date(todayYear, todayMonth, 0).getDate();

    let calender = [];
    let airingDays = [];
    let currentTimeStamp = Math.floor(__dateTimeActualToday.getTime() / 1000);

    for (let _airingScheduleNode of this.media.airingSchedule.nodes) {
      let airingAt = new Date(_airingScheduleNode.airingAt * 1000);
      let timeUntilAiring =
        Math.floor(airingAt.getTime() / 1000) - currentTimeStamp;
      airingDays.push({
        date: airingAt.getDate(),
        month: airingAt.getMonth(),
        year: airingAt.getFullYear(),
        episode: _airingScheduleNode.episode,
        humanizedAir: timeFormat(Math.abs(timeUntilAiring) / 60),
        isAired: timeUntilAiring <= 0,
      });
    }

    for (let _numeral = firstDayOfMonth; _numeral > 0; _numeral--) {
      let thisMonth = todayMonth === 0 ? 11 : todayMonth - 1;
      let thisYear = todayMonth === 0 ? todayYear - 1 : todayYear;
      calender.push({
        number: lastDateOfPreviousMonth - _numeral + 1,
        isToday: false,
        isActive: false,
        animeAiring: airingDays.find(
          (airingDays) =>
            airingDays.date === lastDateOfPreviousMonth - _numeral + 1 &&
            airingDays.month === thisMonth &&
            airingDays.year === thisYear
        ),
      });
    }

    for (let _numeral = 1; _numeral <= lastDayOfMonth; _numeral++) {
      calender.push({
        number: _numeral,
        isToday:
          _numeral === __dateTimeActualToday.getDate() &&
          __dateTimeActualToday.getMonth() === todayMonth &&
          __dateTimeActualToday.getFullYear() === todayYear,
        isActive: true,
        animeAiring: airingDays.find(
          (airingDays) =>
            airingDays.date === _numeral &&
            airingDays.month === todayMonth &&
            airingDays.year === todayYear
        ),
      });
    }

    for (let _numeral = lastDayOfMonthWeekNumber; _numeral < 6; _numeral++) {
      let thisMonth = todayMonth === 11 ? 0 : todayMonth + 1;
      let thisYear = todayMonth === 11 ? todayYear + 1 : todayYear;
      calender.push({
        number: _numeral - lastDayOfMonthWeekNumber + 1,
        isToday: false,
        isActive: false,
        animeAiring: airingDays.find(
          (airingDays) =>
            airingDays.date === _numeral - lastDayOfMonthWeekNumber + 1 &&
            airingDays.month === thisMonth &&
            airingDays.year === thisYear
        ),
      });
    }

    return calender;
  },
  _context_maxPrevious() {
    let firstAir = new Date(
      Math.min(
        ...this.media.airingSchedule.nodes.map((item) => item.airingAt)
      ) * 1000
    );
    let now = new Date(
      $.state._modal_schedule.year,
      $.state._modal_schedule.month
    );
    if (firstAir.getFullYear() < now.getFullYear()) {
      return false;
    } else {
      if (firstAir.getMonth() < now.getMonth()) {
        return false;
      } else {
        return true;
      }
    }
  },
  _context_maxNext() {
    let lastAir = new Date(
      Math.max(
        ...this.media.airingSchedule.nodes.map((item) => item.airingAt)
      ) * 1000
    );
    let now = new Date(
      $.state._modal_schedule.year,
      $.state._modal_schedule.month
    );
    if (lastAir.getFullYear() > now.getFullYear()) {
      return false;
    } else {
      if (lastAir.getMonth() > now.getMonth()) {
        return false;
      } else {
        return true;
      }
    }
  },
  _context_nextAiring_timeRemaining() {
    if (this.media.nextAiringEpisode) {
      return timeFormat(this.media.nextAiringEpisode.timeUntilAiring / 60);
    } else {
      return "";
    }
  },
  _context_isRankingTypeRATED() {
    return this.type === "RATED";
  },
  _context_normalizedScore() {
    let amount = this.amount;
    return (text, render) => {
      scores = $.state._modal_response[
        Number(render(text).trim())
      ].stats.scoreDistribution.map((item) => item.amount);

      let min = Math.min(...scores);
      let max = Math.max(...scores);

      return ((amount - min) / (max - min)) * 100;
    };
  },
  _context_normalizedStatus() {
    return (text, render) => {
      let id_and_amount = render(text).trim().split("|");
      statusAmount = $.state._modal_response[
        Number(id_and_amount[0])
      ].stats.statusDistribution.map((item) => item.amount);

      let min = Math.min(...statusAmount);
      let max = Math.max(...statusAmount);

      return ((Number(id_and_amount[1]) - min) / (max - min)) * 100 + 1;
    };
  },
  _context_score_POINT_100() {
    return (
      this.media.mediaListEntry.user.mediaListOptions.scoreFormat ===
      "POINT_100"
    );
  },
  _context_score_POINT_10_DECIMAL() {
    return (
      this.media.mediaListEntry.user.mediaListOptions.scoreFormat ===
      "POINT_10_DECIMAL"
    );
  },
  _context_score_POINT_10() {
    return (
      this.media.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_10"
    );
  },
  _context_score_POINT_5() {
    return (
      this.media.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_5"
    );
  },
  _context_score_POINT_3() {
    return (
      this.media.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_3"
    );
  },
  _context_isManga() {
    console.log(this.media.type);
    this.media.type === "MANGA";
  },
  _context_advancedScoringEnabled() {
    return (
      this.media.mediaListEntry.user.mediaListOptions[
        this.media.type === "MANGA" ? "mangaList" : "animeList"
      ].advancedScoringEnabled &&
      (this.media.mediaListEntry.user.mediaListOptions.scoreFormat ===
        "POINT_100" ||
        this.media.mediaListEntry.user.mediaListOptions.scoreFormat ===
          "POINT_10_DECIMAL")
    );
  },
  _context_advancedScoring() {
    let advancedScores = [];
    for (let key in this.media.mediaListEntry.advancedScores) {
      advancedScores.push({
        category: key,
        score: this.media.mediaListEntry.advancedScores[key],
      });
    }
    return advancedScores;
  },
  convert_POINT_10_DECIMAL() {
    return (text, render) => {
      return Number(render(text).trim()) / 10;
    };
  },
  convert_POINT_10() {
    return (text, render) => {
      return Math.floor(Number(render(text).trim()) / 10);
    };
  },
  _context_convert_POINT_5() {
    let amount = this.media.mediaListEntry.score;
    const result = ["inactive", "inactive", "inactive", "inactive", "inactive"];
    if (amount <= 0) {
      return result;
    }
    if (amount < 30) {
      return result.fill("active", 0, 1);
    }
    if (amount < 50) {
      return result.fill("active", 0, 2);
    }
    if (amount < 70) {
      return result.fill("active", 0, 3);
    }
    if (amount < 90) {
      return result.fill("active", 0, 4);
    }
    return result.fill("active", 0, 5);
  },
  _context_convert_POINT_3_HAPPY() {
    let amount = this.media.mediaListEntry.score;
    if (amount >= 61) {
      return "active";
    }
    return "inactive";
  },
  _context_convert_POINT_3_NEUTRAl() {
    let amount = this.media.mediaListEntry.score;
    if (amount >= 36 && amount <= 60) {
      return "active";
    }
    return "inactive";
  },
  _context_convert_POINT_3_SAD() {
    let amount = this.media.mediaListEntry.score;
    if (amount <= 35) {
      return "active";
    }
    return "inactive";
  },
  _context_mediaStartDate() {
    var string = "";
    string += this.media.mediaListEntry.startedAt.year;
    string += "-";
    if (this.media.mediaListEntry.startedAt.month < 10) {
      string += "0";
    }
    string += this.media.mediaListEntry.startedAt.month;
    string += "-";
    if (this.media.mediaListEntry.startedAt.day < 10) {
      string += "0";
    }
    string += this.media.mediaListEntry.startedAt.day;
    return string;
  },
  _context_mediaFinishDate() {
    var string = "";
    string += this.media.mediaListEntry.completedAt.year;
    string += "-";
    if (this.media.mediaListEntry.completedAt.month < 10) {
      string += "0";
    }
    string += this.media.mediaListEntry.completedAt.month;
    string += "-";
    if (this.media.mediaListEntry.completedAt.day < 10) {
      string += "0";
    }
    string += this.media.mediaListEntry.completedAt.day;
    return string;
  },
  _context_mediaInList() {
    return this.media.mediaListEntry !== null;
  },
};

function _bindNumberInput(element) {
  let button = $(element);
  let button_action = button.attr("data-action");
  let button_target = $.id(button.attr("data-target"));

  let target_min =
    button_target.attr("min") == ""
      ? -Infinity
      : Number(button_target.attr("min"));
  let target_max =
    button_target.attr("max") == ""
      ? Infinity
      : Number(button_target.attr("max"));
  let target_step = button_target.attr("step") || 1;

  let _interval = undefined;

  function _setValue() {
    let current_val = Number(
      button_target.val() || button_target.attr("min") || 0
    );
    var value = 0;
    if (button_action === "plus") {
      value = current_val + Number(target_step);
    } else {
      value = current_val - Number(target_step);
    }
    if (value >= target_max) {
      value = target_max;
    }
    if (value <= target_min) {
      value = target_min;
    }
    value = String(Math.round(value * 10) / 10);
    if (button_target.attr("step").includes(".") && !value.includes(".")) {
      value += ".0";
    }
    button_target.val(value).change();
  }

  button.on("mousedown", function () {
    _interval = setInterval(_setValue, 120);
  });
  button.on("mouseup mouseleave", function () {
    clearInterval(_interval);
  });
}

function InitializeModalActions(mediaId) {
  let data = $.state._modal_response[mediaId].mediaListEntry;

  $.id("[modal]-actions.status").val(data.status);

  $("button[number-input-button]").each(function (index, value) {
    _bindNumberInput(this);
  });

  $("span[data-score-star]").each(function (index, value) {
    $(this).on("click", function () {
      setStarScore(index + 1);
    });
  });

  $("span[data-score-smile]").each(function (index, value) {
    $(this).on("click", function () {
      setSmileScore(index);
    });
  });

  $("input[type=number").bind("change keyup", function () {
    let input = $(this);
    let min = input.attr("min") == "" ? -Infinity : Number(input.attr("min"));
    let max = input.attr("max") == "" ? Infinity : Number(input.attr("max"));
    let val = Number(input.val());
    if (val > max) {
      input.val(max);
    }
    if (val < min) {
      input.val(min);
    }
    if (input.is(":invalid")) {
      input.val(input.attr("value") || min);
      $.notification("tell", "Invalid value");
    }
  });

  $("input[data-advance-score-type]").each(function (index, value) {
    $(this).on("change", function () {
      updateAdvancedScore(data.user.mediaListOptions.scoreFormat);
    });
    $(this).keyup(function () {
      updateAdvancedScore(data.user.mediaListOptions.scoreFormat);
    });
  });
}

function updateAdvancedScore(scoreFormat) {
  let score = 0;
  let match = 0;
  $("input[data-advance-score-type]").each(function (index, value) {
    let advancedScore = Number($(this).val());
    if (advancedScore > 0) {
      match += 1;
      score += advancedScore;
    }
  });
  if (match > 0) {
    score = Math.round((score / match) * 10) / 10 || 0;
    if (scoreFormat === "POINT_100") {
      $.id("[modal]-actions.score.point_100").val(Math.floor(score));
    }
    if (scoreFormat === "POINT_10_DECIMAL") {
      $.id("[modal]-actions.score.point_10_decimal").val(score);
    }
  } else {
    $.id("[modal]-actions.score.point_100").val("0");
    $.id("[modal]-actions.score.point_10_decimal").val("0");
  }
}

function setInitialMediaStatus(mediaId, status) {
  if ($.state.session.token) {
    $.anilist(
      $.state.graphql.update,
      { status: status, mediaId: Number(mediaId) },
      (response) => {
        $.state._modal_response[mediaId].mediaListEntry =
          response.data.SaveMediaListEntry;
        $.notification("success", "Media added to " + status);
        setModalContent(mediaId, "list");
      }
    );
  } else {
    $.notification("inform", "Login before using this feature");
  }
}

function deleteMediaListEntry(mediaId, entryId) {
  $.anilist($.state.graphql.delete, { id: Number(entryId) }, (response) => {
    if (response.data.DeleteMediaListEntry.deleted) {
      $.state._modal_response[mediaId].mediaListEntry = null;
      $.notification("success", "Media removed from list");
      setModalContent(mediaId, "list");
    } else {
      $.notification("error", "Could not remove media from list");
    }
  });
}

function saveModalListEdits(mediaId, private = false) {
  var variables = {};
  let data = $.state._modal_response[mediaId];
  variables.mediaId = Number(mediaId);
  variables.status = $.id("[modal]-actions.status").val();

  variables.scoreRaw = null;
  if (data.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_100") {
    variables.scoreRaw = Number($.id("[modal]-actions.score.point_100").val());
  }
  if (
    data.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_10_DECIMAL"
  ) {
    variables.scoreRaw = Math.floor(
      Number($.id("[modal]-actions.score.point_10_decimal").val()) * 10
    );
  }
  if (data.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_10") {
    variables.scoreRaw = Math.floor(
      Number($.id("[modal]-actions.score.point_10").val()) * 10
    );
  }
  if (data.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_5") {
    let stars = $("span[data-score-star='active']").length;
    let mapping = [0, 10, 30, 50, 70, 90];
    variables.scoreRaw = mapping[stars];
  }
  if (data.mediaListEntry.user.mediaListOptions.scoreFormat === "POINT_3") {
    let smile = $("span[data-score-smile='active']").attr("data-smile-type");
    let mapping = {
      HAPPY: 85,
      NEUTRAL: 60,
      SAD: 35,
    };
    variables.scoreRaw = mapping[smile];
  }
  variables.scoreRaw = variables.scoreRaw ?? 0;

  variables.progress =
    Number($.id("[modal]-actions.episode_progress").val()) || 0;
  if (data.type === "MANGA") {
    variables.progressVolumes =
      Number($.id("[modal]-actions.volume_progress").val()) || 0;
  }
  variables.repeat = Number($.id("[modal]-actions.repeat").val()) || 0;
  variables.private = private;
  variables.notes = $.id("[modal]-actions.notes").val().trim();

  variables.customLists = [];
  $("[data-custom-list-name]").each(function (index, value) {
    if ($(this).is(":checked")) {
      variables.customLists.push($(this).attr("data-custom-list-name"));
    }
  });

  if ($.id("[modal]-actions.start_date").val()) {
    let start = new Date($.id("[modal]-actions.start_date").val());
    variables.startedAt = {
      day: start.getDate(),
      month: start.getMonth() + 1,
      year: start.getFullYear(),
    };
  }
  if ($.id("[modal]-actions.finish_date").val()) {
    let complete = new Date($.id("[modal]-actions.finish_date").val());
    variables.completedAt = {
      day: complete.getDate(),
      month: complete.getMonth() + 1,
      year: complete.getFullYear(),
    };
  }
  variables.advancedScores = {};
  $("[data-advance-score-type]").each(function () {
    let input = $(this);
    variables.advancedScores[input.attr("data-advance-score-type")] = Number(
      input.val()
    );
  });

  $.anilist($.state.graphql.update, variables, (response) => {
    $.state._modal_response[mediaId].mediaListEntry =
      response.data.SaveMediaListEntry;
    $.notification("success", "Entry Saved");
    setModalContent(mediaId, "list");
  });
}

function setSmileScore(smile) {
  let reset = $.state._last_smile_score_index === smile;
  $.state._last_smile_score_index = smile;
  if (reset) {
    $.state._last_smile_score_index = undefined;
  }
  $("span[data-score-smile]").each(function (index, value) {
    if (index === smile && !reset) {
      $(this).attr("data-score-smile", "active");
    } else {
      $(this).attr("data-score-smile", "inactive");
    }
  });
}

function setStarScore(star) {
  let reset = $.state._last_star_score_index === star;
  $.state._last_star_score_index = star;
  if (reset) {
    $.state._last_star_score_index = undefined;
  }
  $("span[data-score-star]").each(function (index, value) {
    if (index < star && !reset) {
      $(this).attr("data-score-star", "active");
    } else {
      $(this).attr("data-score-star", "inactive");
    }
  });
}

function ShowModal(mediaId, modalTitle, index = null) {
  $.id("[modal]-content").mustache($.id("[modal]@template.loading-animate"), {
    title: modalTitle,
  });
  $.id("[container]-lists@template.modal_view.sections").animate(
    {
      scrollLeft: 0,
    },
    0
  );

  $.state._modal_schedule = {
    year: new Date().getFullYear(),
    month: new Date().getMonth(),
  };

  if (!$.state._modal_window_history.length) {
    $.id("[modal]")
      .removeClass("animate__animated animate__fadeOut")
      .addClass("animate__animated animate__fadeIn")
      .css("--animate-duration", "0.12s")
      .removeClass("hidden");
    $.state._modal_window_history.push({
      mediaId: mediaId,
      modalTitle: modalTitle,
      index: 1,
    });
  } else {
    if (index) {
      $.state._modal_window_history.splice(
        Number(index) - $.state._modal_window_history.length
      );
    } else {
      $.state._modal_window_history.push({
        mediaId: mediaId,
        modalTitle: modalTitle,
        index: $.state._modal_window_history.at(-1).index + 1,
      });
    }
  }

  $.state.__active_schedule_episode = null;

  if ($.state._modal_response[mediaId]) {
    $.id("[modal]-content").mustache(
      $.id("[container]-lists@template.modal_view"),
      {
        fn: $.state._modal_mustache_functions,
        media: $.state._modal_response[mediaId],
        history: $.state._modal_window_history.slice(0, -1),
        current: $.state._modal_window_history.at(-1),
      }
    );
    setTimeout(() => {
      setModalContent(mediaId, "overview");
    }, 50);
  } else {
    $.anilist($.state.graphql.media, { id: Number(mediaId) }, (response) => {
      $.state._modal_response[mediaId] = response.data.Media;
      $.id("[modal]-content").mustache(
        $.id("[container]-lists@template.modal_view"),
        {
          fn: $.state._modal_mustache_functions,
          media: $.state._modal_response[mediaId],
          history: $.state._modal_window_history.slice(0, -1),
          current: $.state._modal_window_history.at(-1),
        }
      );
      setTimeout(() => {
        setModalContent(mediaId, "overview");
      }, 50);
    });
  }
}

function setModalContent(mediaId, modalTemplate) {
  modalContainer = $.id("[container]-lists@template.modal_view.content");

  if (
    $.state.__lastModalContainer !== modalTemplate ||
    $.state.__lastModalId !== mediaId
  ) {
    const activeCSS = "dark:!bg-slate-950/50 !bg-slate-200";
    $.id(
      "[container]-lists@template.modal_view.section." +
        $.state.__lastModalContainer
    ).removeClass(activeCSS);
    $.id(
      "[container]-lists@template.modal_view.section." + modalTemplate
    ).addClass(activeCSS);

    $.state.__lastModalContainer = modalTemplate;
    $.state.__lastModalId = mediaId;

    if (
      modalTemplate === "overview" ||
      modalTemplate === "schedule" ||
      (modalTemplate === "list" &&
        $.state._modal_response[mediaId].mediaListEntry === null)
    ) {
      modalContainer.addClass("!h-full");
    } else {
      modalContainer.removeClass("!h-full");
    }

    modalContainer.mustache(
      $.id("[container]-lists@template.modal_view." + modalTemplate),
      {
        fn: $.state._modal_mustache_functions,
        media: $.state._modal_response[mediaId],
      }
    );
    $("img[lazyload]").lazyload();
  } else {
    if (modalTemplate === "schedule") {
      modalContainer.mustache(
        $.id("[container]-lists@template.modal_view." + modalTemplate),
        {
          fn: $.state._modal_mustache_functions,
          media: $.state._modal_response[mediaId],
        }
      );
      $("img[lazyload]").lazyload();
    }
    if (modalTemplate === "list") {
      if (!$.state._modal_response[mediaId].mediaListEntry === null) {
        modalContainer.addClass("!h-full");
      } else {
        modalContainer.removeClass("!h-full");
      }
      modalContainer.mustache(
        $.id("[container]-lists@template.modal_view." + modalTemplate),
        {
          fn: $.state._modal_mustache_functions,
          media: $.state._modal_response[mediaId],
        }
      );
      $("img[lazyload]").lazyload();
    }
  }
  modalContainer.animate({ scrollTop: 0 }, 100);
}

function schedulePrevious(mediaId) {
  $.state._modal_schedule = {
    year:
      $.state._modal_schedule.month === 0
        ? $.state._modal_schedule.year - 1
        : $.state._modal_schedule.year,
    month:
      $.state._modal_schedule.month === 0
        ? 11
        : $.state._modal_schedule.month - 1,
  };
  setModalContent(mediaId, "schedule");
}

function scheduleNext(mediaId) {
  $.state._modal_schedule = {
    year:
      $.state._modal_schedule.month === 11
        ? $.state._modal_schedule.year + 1
        : $.state._modal_schedule.year,
    month:
      $.state._modal_schedule.month === 11
        ? 0
        : $.state._modal_schedule.month + 1,
  };
  setModalContent(mediaId, "schedule");
}

function InitializeScheduleHover() {
  let next_airing_text = $.id("[modal]-schedule.airing_text");
  $.state.__schedule_next_airing_text = "";
  if (next_airing_text.attr("data-not-have-airing") === "false") {
    $.state.__schedule_next_airing_text = $.id(
      "[modal]-schedule@template.next_airing_text"
    ).html();
    next_airing_text.html($.state.__schedule_next_airing_text);
  }
  if (!$.state.__active_schedule_episode) {
    $("[episode-airing-day]").each(function () {
      const element = $(this);
      if (
        element.attr("data-next-airing-episode") ===
        element.attr("data-episode")
      ) {
        $("[data-for-episode=" + element.attr("data-episode") + "]").attr(
          "data-is-next-episode",
          "true"
        );
        $.state.__active_schedule_episode = element.attr("data-episode");
      }
    });
  } else {
    $("[data-for-episode=" + $.state.__active_schedule_episode + "]").attr(
      "data-is-next-episode",
      "true"
    );
  }
  $("[episode-airing-day]").on("mouseenter", function () {
    const element = $(this);
    $.id("[modal]-schedule.airing_text").mustache(
      $.id("[modal]-schedule@template.airing_notice"),
      {
        isAired: element.attr("data-is-aired") === "true",
        episode: element.attr("data-episode"),
        timeUntil: element.attr("data-time-until"),
        isNext:
          element.attr("data-next-airing-episode") ===
          element.attr("data-episode"),
      }
    );
  });

  $("[episode-airing-day]").on("click", function () {
    const element = $(this);
    $("[data-for-episode=" + $.state.__active_schedule_episode + "]").attr(
      "data-is-next-episode",
      "false"
    );
    $.state.__active_schedule_episode = element.attr("data-episode");
    $("[data-for-episode=" + element.attr("data-episode") + "]").attr(
      "data-is-next-episode",
      "true"
    );
    $.state.__schedule_next_airing_text = $.mustache(
      $.id("[modal]-schedule@template.airing_notice"),
      {
        isAired: element.attr("data-is-aired") === "true",
        episode: element.attr("data-episode"),
        timeUntil: element.attr("data-time-until"),
        isNext:
          element.attr("data-next-airing-episode") ===
          element.attr("data-episode"),
      }
    );
  });

  $("[episode-airing-day]").on("mouseleave", function () {
    $.id("[modal]-schedule.airing_text").html(
      $.state.__schedule_next_airing_text
    );
  });
}
