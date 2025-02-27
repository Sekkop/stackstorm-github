from lib.base import BaseGithubAction
from lib.formatters import event_to_dict

__all__ = [
    'GetEventsAction'
]


class GetEventsAction(BaseGithubAction):
    def run(self, user, repo, token_user, github_type, count, event_type_whitelist):
        enterprise = self._is_enterprise(github_type)
        if token_user:
            self._change_to_user_token(token_user, enterprise)

        user = self._client.get_user(user)
        repo = user.get_repo(repo)
        repository_events = repo.get_events()
        events = list(repository_events[:count]) \
            if repository_events.totalCount > count else list(repository_events)
        events.sort(key=lambda _event: _event.id, reverse=False)

        result = [event_to_dict(event) for event in events]
        #result = [event_to_dict(event) for event in events if event.type in event_type_whitelist]
        for item in result:
            print(item)

        #events.filter(lambda event: event.type in whitelist)


        return result
