class MediaFormats:
    TV = "TV"
    TV_SHORT = "TV_SHORT"
    MOVIE = "MOVIE"
    SPECIAL = "SPECIAL"
    OVA = "OVA"
    ONA = "ONA"
    MANGA = "MANGA"
    ONE_SHOT = "ONE_SHOT"
    NOVEL = "NOVEL"
    MUSIC = "MUSIC"


class MediaType:
    ANIME = "ANIME"
    MANGA = "MANGA"
    MUSIC = "MUSIC"
    NOVEL = "NOVEL"


class MediaStatus:
    FINISHED = "FINISHED"
    RELEASING = "RELEASING"
    HIATUS = "HIATUS"
    CURRENT = "CURRENT"
    COMPLETED = "COMPLETED"
    REPEATING = "REPEATING"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"


class MediaRelation:
    ADAPTATION = "ADAPTATION"
    PREQUEL = "PREQUEL"
    SEQUEL = "SEQUEL"
    PARENT = "PARENT"
    SIDE_STORY = "SIDE_STORY"
    CHARACTER = "CHARACTER"
    SUMMARY = "SUMMARY"
    ALTERNATIVE = "ALTERNATIVE"
    SPIN_OFF = "SPIN_OFF"
    OTHER = "OTHER"
    SOURCE = "SOURCE"
    COMPILATION = "COMPILATION"
    CONTAINS = "CONTAINS"


class dbconstants:
    ANIME_FORMATS = [
        MediaFormats.TV,
        MediaFormats.TV_SHORT,
        MediaFormats.MOVIE,
        MediaFormats.SPECIAL,
        MediaFormats.OVA,
        MediaFormats.ONA,
    ]
    MANGA_FORMATS = [
        MediaFormats.MANGA,
        MediaFormats.ONE_SHOT,
    ]
    NOVEL_FORMAT = MediaFormats.NOVEL
    MUSIC_FORMAT = MediaFormats.MUSIC

    MEDIA_TYPES = [MediaType.ANIME, MediaType.MANGA, MediaType.MUSIC, MediaType.NOVEL]

    READ_TYPES = [NOVEL_FORMAT] + MANGA_FORMATS
    WATCH_TYPES = ANIME_FORMATS + [MUSIC_FORMAT]

    RELATION_PARSE_PRIORITY_ORDER = WATCH_TYPES + READ_TYPES

    FORMAT_ALIAS = {
        MediaFormats.TV: "S",
        MediaFormats.TV_SHORT: "SHORT",
        MediaFormats.SPECIAL: "SPE",
        MediaFormats.ONE_SHOT: "PILOT",
        MediaFormats.NOVEL: "LN",
    }

    ALLOWED_RELATIONS = {
        MediaRelation.ADAPTATION,
        MediaRelation.PREQUEL,
        MediaRelation.SEQUEL,
        MediaRelation.SIDE_STORY,
        MediaRelation.SUMMARY,
        MediaRelation.ALTERNATIVE,
        MediaRelation.SOURCE,
        MediaRelation.COMPILATION,
        MediaRelation.CONTAINS,
    }

    AVAILABLE_STATUS = {MediaStatus.FINISHED, MediaStatus.RELEASING, MediaStatus.HIATUS}

    POSITIVE_STATUS = {
        MediaStatus.CURRENT,
        MediaStatus.COMPLETED,
        MediaStatus.REPEATING,
    }
    NEGATIVE_STATUS = {MediaStatus.DROPPED, MediaStatus.PAUSED}

    DB_ENTRY_TABLE = [
        "ID",
        "NAME_ENGLISH",
        "NAME_ROMAJI",
        "NAME_NATIVE",
        "COVER",
        "FORMAT",
        "STATUS",
        "TYPE",
        "COUNT",
        "DURATION",
        "START",
        "RELATIONS",
    ]
    DB_ENTRY_TABLE_INDEX = dict(
        (key, index) for index, key in enumerate(DB_ENTRY_TABLE)
    )
