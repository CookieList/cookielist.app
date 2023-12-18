function SwapContainer(ContainerID) {
  const container = $.id("[container]@content");
  if ($.state.__LASTContainerID !== ContainerID) {
    const activeCSS =
      "!bg-slate-200 !border-slate-300 hover:!bg-gray-200 hover:!border-gray-300 dark:!bg-slate-950 dark:!border-slate-800 dark:hover:!bg-gray-900 dark:hover:!border-gray-800";
    $.id("[sidebar]-" + $.state.__LASTContainerID).removeClass(activeCSS);
    $.id("[sidebar]-" + ContainerID).addClass(activeCSS);

    $.state.__LASTContainerID = ContainerID;
    container.html($.id("[container]-" + ContainerID).html());
  }
  container.animate({ scrollTop: 0 }, 100);
}

function SwapEntryView(ViewID) {
  const entry = $.id("[container]@gutter");
  entry.html($.id("[gutter]-block@" + ViewID).html());
  entry.animate({ scrollTop: 0 }, 100);
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

  entry.html($.id("[gutter]-block@" + ViewID).html());
  entry.animate({ scrollTop: 0 }, 100);
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
