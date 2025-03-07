import re
from lib.utils import branch_protection_attributes, required_pull_request_reviews_attributes
from st2common.util import isotime

__all__ = [
    'branch_protection_to_dict',
    'issue_to_dict',
    'pull_to_dict',
    'commit_to_dict',
    'label_to_dict',
    'user_to_dict',
    'contents_to_dict',
    'file_response_to_dict',
]


def branch_protection_to_dict(branch_protection):
    result = {}
    for attr in branch_protection_attributes:

        # skip unknown/unsupported attributes
        if not hasattr(branch_protection, attr):
            continue

        # special treatment for some of the attributes
        if attr == 'required_status_checks':
            req_status_checks = branch_protection.required_status_checks
            if req_status_checks:
                result[attr] = {'contexts': req_status_checks.contexts,
                                'strict': req_status_checks.strict}
            else:
                result[attr] = None
        elif attr == 'required_pull_request_reviews':
            req_pr_reviews = branch_protection.required_pull_request_reviews
            if req_pr_reviews:
                result[attr] = {}
                for attr2 in required_pull_request_reviews_attributes:
                    if attr2 == 'dismissal_users':
                        if req_pr_reviews.dismissal_users is not None:
                            users = [user.login for user in req_pr_reviews.dismissal_users]
                        else:
                            users = None
                        result[attr][attr2] = users
                    elif attr2 == 'dismissal_teams':
                        if req_pr_reviews.dismissal_teams is not None:
                            teams = [team.slug for team in req_pr_reviews.dismissal_teams]
                        else:
                            teams = None
                        result[attr][attr2] = teams
                    else:
                        result[attr][attr2] = getattr(req_pr_reviews, attr2)
            else:
                result[attr] = None
        else:
            result[attr] = getattr(branch_protection, attr)

    return result


def issue_to_dict(issue):
    result = {}

    author = user_to_dict(issue.user)
    assignee = user_to_dict(issue.assignee)
    closed_by = user_to_dict(issue.closed_by)

    if issue.pull_request:
        is_pull_request = True
    else:
        is_pull_request = False

    result['id'] = issue.id
    result['repository'] = issue.repository.name
    result['author'] = author
    result['assign'] = assignee
    result['title'] = issue.title
    result['body'] = issue.body
    result['url'] = issue.html_url
    result['state'] = issue.state
    result['is_pull_request'] = is_pull_request

    if issue.labels:
        labels = [label_to_dict(label) for label in issue.labels]
    else:
        labels = []

    result['labels'] = labels

    # Note: We convert it to a serialize type (string)
    if issue.created_at:
        created_at = isotime.format(issue.created_at)
    else:
        created_at = None

    if issue.closed_at:
        closed_at = isotime.format(issue.closed_at)
    else:
        closed_at = None

    result['created_at'] = created_at
    result['closed_at'] = closed_at
    result['closed_by'] = closed_by
    return result


def pull_to_dict(pull):
    result = {}

    author = user_to_dict(pull.user)
    assignee = user_to_dict(pull.assignee)
    merged_by = user_to_dict(pull.merged_by)

    result['id'] = pull.id
    result['pr_id'] = int(re.sub(r'.*/([0-9]+)(#.*)?', r'\1', pull.html_url))
    result['author'] = author
    result['assign'] = assignee
    result['title'] = pull.title
    result['body'] = pull.body
    result['url'] = pull.html_url
    result['base'] = pull.base.ref
    result['head'] = pull.head.ref
    result['state'] = pull.state
    result['merged'] = pull.merged
    # noinspection SpellCheckingInspection
    result['mergeable_state'] = pull.mergeable_state
    result['merge_commit_sha'] = pull.merge_commit_sha

    if pull.labels:
        labels = [label_to_dict(label) for label in pull.labels]
    else:
        labels = []

    result['labels'] = labels

    if pull.get_commits():
        commits = [commit_to_dict(commit) for commit in pull.get_commits()]
    else:
        commits = []

    result['commits'] = commits

    # Note: We convert it to a serialize type (string)
    if pull.created_at:
        created_at = isotime.format(pull.created_at)
    else:
        created_at = None

    if pull.closed_at:
        closed_at = isotime.format(pull.closed_at)
    else:
        closed_at = None

    if pull.merged_at:
        merged_at = isotime.format(pull.merged_at)
    else:
        merged_at = None

    result['created_at'] = created_at
    result['closed_at'] = closed_at
    result['merged_at'] = merged_at
    result['merged_by'] = merged_by
    return result


def commit_to_dict(commit):
    result = {'sha': commit.sha}
    return result


def label_to_dict(label):
    result = {'name': label.name, 'color': label.color, 'url': label.url}

    return result


def user_to_dict(user):
    if not user:
        return None

    result = {'name': user.name, 'login': user.login}
    return result

def event_to_dict(event):
    if not event:
        return None

    result = {'id': event.id, 'type': event.type, 'actor': event.actor, 'repo': event.repo, 'created_at': event.created_at}
    return result

def repo_to_dict(repo):
    if not repo:
        return None

    result = {'id': repo.id, 'name': repo.name, 'full_name': repo.full_name, 'private': repo.private, 'url': repo.url, "pushed_at": repo.pushed_at}
    return result

def release_to_dict(release):
    result = {'author': release.author.login,
     'avatar_url': release.author.avatar_url,
     'html_url': release.html_url,
     'tag_name': release.tag_name,
     'target_commitish': release.target_commitish,
     'name': release.name,
     'body': release.body,
     'draft': release.draft,
     'prerelease': release.prerelease,
     'created_at': release.created_at.strftime('%Y-%m-%d %H:%M:%S'),
     'published_at': release.published_at.strftime('%Y-%m-%d %H:%M:%S'),
     'assets': release.assets,
     'total_assets': len(release.assets)}
    return result

def team_to_dict(team):
    if not team:
        return None

    result = {'id': team.id, 'name': team.name, 'members_count': team.members_count}
    return result


def contents_to_dict(contents, decode=False):
    if not contents:
        return None

    directory = False
    if isinstance(contents, list):
        directory = True
    else:
        contents = [contents]

    result = []
    data = {}

    for item in contents:
        item_type = item.type
        data['type'] = item_type
        if item_type == 'symlink':
            data['target'] = item.target
        elif item_type == 'submodule':
            data['submodule_git_url'] = item.submodule_git_url
        elif not directory:
            data['encoding'] = item.encoding
            data['content'] = item.decoded_content.decode('utf-8') if decode else item.content

        data['size'] = item.size
        data['name'] = item.name
        data['path'] = item.path
        data['sha'] = item.sha
        data['url'] = item.url
        data['git_url'] = item.git_url
        data['html_url'] = item.html_url
        data['download_url'] = item.download_url
        result.append(data)

    if not directory:
        return result[0]
    else:
        return result


def file_response_to_dict(response):
    result = {'commit': response['commit'].sha}
    return result
