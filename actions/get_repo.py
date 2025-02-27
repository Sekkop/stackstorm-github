from lib.base import BaseGithubAction
from lib.formatters import repo_to_dict

__all__ = [
    'GetRepoAction'
]


class GetRepoAction(BaseGithubAction):
    def run(self, user, repo, token_user, github_type, count, event_type_whitelist):
        enterprise = self._is_enterprise(github_type)
        if token_user:
            self._change_to_user_token(token_user, enterprise)

        user = self._client.get_user(user)
        repo = user.get_repo(repo)
        result = repo_to_dict(repo)

        #events.filter(lambda event: event.type in whitelist)


        return result
