import calendar
import zoneinfo
from collections import defaultdict

import arrow
import jmespath
from dotted_dict import DottedDict


class ScheduleProcessor:
    def __init__(self) -> None:
        self.weeks = {index: day for index, day in enumerate(calendar.day_name)} | {
            day: index for index, day in enumerate(calendar.day_name)
        }

        self.watching_anime_query = jmespath.compile(
            "data.MediaListCollection.lists[?isCustomList == `false` && status == 'CURRENT'].entries[].media.id"
        )

        self.airing_anime_query = jmespath.compile(
            "data.MediaListCollection.lists[?isCustomList == `false`].entries[] | @[?media.nextAiringEpisode != `null`].media"
        )

    def __weeks(
        self, start_day: str = "Monday", timezone: zoneinfo.ZoneInfo = "UTC"
    ) -> list[str]:
        if start_day == "Today":
            start_day = self.weeks[arrow.now(timezone).weekday()]
        elif start_day == "Yesterday":
            today = arrow.now(timezone).weekday()
            start_day = self.weeks[today - 1 if today != 0 else 6]

        week_day_int = self.weeks.get(start_day, 0)
        for day_int in range(week_day_int, 7):
            yield self.weeks[day_int]
        for day_int in range(week_day_int):
            yield self.weeks[day_int]

    def calculate(self, data: DottedDict) -> dict:
        schedule = defaultdict(lambda: defaultdict(list))

        timezone = zoneinfo.ZoneInfo(data.options.timezone)
        week_span = arrow.now(data.options.timezone).shift(days=-1), arrow.now(
            data.options.timezone
        ).shift(weeks=1)

        airing_anime = self.airing_anime_query.search(
            data.anime, jmespath.Options(dict_cls=DottedDict)
        )

        for day_entry in sorted(
            airing_anime, key=lambda entry: entry.nextAiringEpisode.airingAt
        ):
            tz_start_time = arrow.Arrow.fromtimestamp(
                day_entry.nextAiringEpisode.airingAt, tzinfo=timezone
            )
            schedule[self.weeks[tz_start_time.weekday()]][
                tz_start_time.format(data.options.time_format)
                if tz_start_time.is_between(*week_span)
                else tz_start_time.format(data.options.date_format)
            ].append(
                dict(
                    id=day_entry.id,
                    name=day_entry.title.english or day_entry.title.romaji,
                    cover=day_entry.coverImage.large,
                    episode=day_entry.nextAiringEpisode.episode,
                    time=tz_start_time,
                )
            )

        return dict(
            schedule={
                day: schedule[day]
                for day in self.__weeks(data.options.week_start_day, timezone)
                if schedule[day]
            },
            today=self.weeks[arrow.now(timezone).weekday()],
            watching=self.watching_anime_query.search(data.anime),
        )
