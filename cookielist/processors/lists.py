from collections import defaultdict, deque

from cookielist.database import CookieListDatabase, dbconstants
from cookielist.database.database import CookieListDatabaseEntry
from cookielist.processors._pre_process import (
    AniListUser,
    CookieListOptions,
    MediaCollection,
)


class ListProcessor:
    cookiedb = CookieListDatabase()

    def __media_relation_group(
        self, media_ids: list[int]
    ) -> list[list[CookieListDatabaseEntry]]:
        unique_relation_ids = {
            self.cookiedb.relation(media_id)
            for media_id in media_ids
            if media_id in self.cookiedb
        }
        relation_media_groups = [
            [self.cookiedb[media_id] for media_id in relation]
            for relation in [
                self.cookiedb(relation_id) for relation_id in unique_relation_ids
            ]
        ]
        return relation_media_groups

    def calculate(
        self, Media: MediaCollection, User: AniListUser, Options: CookieListOptions
    ) -> dict:

        mediaNameFunction = {
            "english": lambda _: _.nameEnglish,
            "romaji": lambda _: _.nameRomaji,
            "native": lambda _: _.nameNative,
        }.get(Options.mediaTitleLanguage.lower(), lambda _: _.nameEnglish)

        completedMedia = {media.mediaId for media in Media.COMPLETED}
        currentMedia = {media.mediaId for media in Media.CURRENT}
        repeatingMedia = {media.mediaId for media in Media.REPEATING}
        droppedMedia = {media.mediaId for media in Media.DROPPED}
        pausedMedia = {media.mediaId for media in Media.PAUSED}

        watchedMedia = completedMedia | currentMedia | repeatingMedia
        unwatchedMedia = droppedMedia | pausedMedia

        processedResult = defaultdict(
            lambda: dict(groupEntries=deque(), categoryDuration=0, categoryGroupCount=0)
        )

        for mediaGroup in self.__media_relation_group(watchedMedia):

            groupType = mediaGroup[0].mediaType
            groupCategory = "anime" if groupType in {"ANIME", "MUSIC"} else "manga"
            groupDuration = sum(media.duration for media in mediaGroup)
            completedGroupMediaCount = 0
            parsedMediaGroup = list()

            for media in mediaGroup:
                mediaId = media.id

                isMediaWatched = mediaId in watchedMedia
                mediaListStatus = (
                    Media.Statuses[mediaId] if mediaId in Media.Statuses else None
                )
                isMediaAvailableToWatch = (
                    media.mediaStatus in dbconstants.AVAILABLE_STATUS
                )
                isUserGoingToWatch = (
                    False
                    if (isMediaWatched or mediaId in unwatchedMedia)
                    else isMediaAvailableToWatch
                )

                parsedMediaGroup.append(
                    {
                        "mediaId": mediaId,  # id
                        "mediaTitle": mediaNameFunction(media),  # name
                        "mediaCategory": groupCategory,  # category
                        "mediaCover": media.coverImage,  # cover
                        "mediaFormat": media.mediaFormat or "UNKNOWN",  # format
                        "isMediaWatched": isMediaWatched,  # completed
                        "isMediaAvailableToWatch": isMediaAvailableToWatch,  # available
                        "isUserGoingToWatch": isUserGoingToWatch,  # plausible
                        "mediaListStatus": mediaListStatus,
                    }
                )

                if isMediaWatched:
                    completedGroupMediaCount += 1

            groupId = parsedMediaGroup[0]["mediaId"]
            groupName = mediaNameFunction(self.cookiedb[self.cookiedb.series(groupId)])
            isGroupCompleted = not any(
                media["isUserGoingToWatch"] for media in parsedMediaGroup
            )
            completedGroupMedia = [
                media["mediaFormat"]
                for media in parsedMediaGroup
                if media["isMediaWatched"]
            ]
            groupCompletionStatus = {
                dbconstants.FORMAT_ALIAS.get(
                    mediaFormat, mediaFormat
                ): completedGroupMedia.count(mediaFormat)
                for mediaFormat in dbconstants.RELATION_PARSE_PRIORITY_ORDER
                if completedGroupMedia.count(mediaFormat)
            }

            processedResult[groupType]["categoryGroupCount"] += 1
            processedResult[groupType]["categoryDuration"] += groupDuration
            processedResult[groupType]["groupEntries"].append(
                {
                    "mediaGroups": parsedMediaGroup,  # group
                    "groupId": groupId,  # id
                    "groupName": groupName,  # name
                    "groupMediaCount": len(parsedMediaGroup),  # total/length
                    "completedGroupMediaCount": completedGroupMediaCount,  # completed
                    "groupDuration": groupDuration,  # duration
                    "isGroupCompleted": isGroupCompleted,  # watched
                    "groupCompletionStatus": groupCompletionStatus,  # status
                }
            )

        searchIndex = {}
        for groupType, groupEntry in processedResult.items():
            processedResult[groupType]["groupEntries"] = sorted(
                groupEntry["groupEntries"], key=lambda group: group["groupName"].upper()
            )
            searchIndex[groupType] = [
                {
                    "id": entries["groupId"],
                    "name": entries["groupName"],
                }
                for entries in processedResult[groupType]["groupEntries"]
            ]

        ignoredMedia = [
            Media.Map[mediaId]
            for mediaId in watchedMedia
            if mediaId not in self.cookiedb
        ]

        return {
            "listResults": processedResult,
            "ignoredMedia": ignoredMedia,
            "searchIndex": searchIndex,
        }
