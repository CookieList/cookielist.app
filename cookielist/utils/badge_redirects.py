from cookielist.environment import env

servers = env.list("COOKIELIST_BADGE_SERVERS")
if servers:
    REDIRECTS = {
        str(id): server.strip("/")
        for server, ids in zip(
            servers,
            (
                lambda div=len(range(0, 10)) // len(servers), mod=len(
                    range(0, 10)
                ) % len(servers), parts=list(range(0, 10)): [
                    parts[
                        index * div
                        + min(index, mod) : (index + 1) * div
                        + min(index + 1, mod)
                    ]
                    for index in range(len(servers))
                ]
            )(),
        )
        for id in ids
    }
else:
    REDIRECTS = {}
