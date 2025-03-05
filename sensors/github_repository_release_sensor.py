from multiprocessing.managers import dispatch

import six
import eventlet
from github import Github

from st2reactor.sensor.base import PollingSensor

eventlet.monkey_patch(
    os=True,
    select=True,
    socket=True,
    thread=True,
    time=True)

DATE_FORMAT_STRING = '%Y-%m-%d %H:%M:%S'
# Default Github API url
DEFAULT_API_URL = 'https://api.github.com'

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
     'total_assets': len(release.assets)}
    return result


class GithubRepositoryReleaseSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(GithubRepositoryReleaseSensor, self).__init__(sensor_service=sensor_service,
                                                     config=config,
                                                     poll_interval=poll_interval)
        self._trigger_ref = 'github.repository_release_event'
        self._logger = self._sensor_service.get_logger(__name__)

        self._client = None
        self._repositories = []
        self._last_published_at = {}
        self.EVENT_TYPE_WHITELIST = []

    def setup(self):
        # Empty string '' is not ok but None is fine. (Sigh)
        github_type = self._config.get('github_type', None)
        if github_type == 'online':
            config_base_url = DEFAULT_API_URL
        else:
            config_base_url = self._config.get('base_url', None) or None

        config_token = self._config.get('token', None) or None
        self._client = Github(config_token or None, base_url=config_base_url)

        repository_release_sensor = self._config.get('repository_release_sensor', None)
        if repository_release_sensor is None:
            raise ValueError('"repository_release_sensor" config value is required.')

        repositories = repository_release_sensor.get('repositories', None)
        if not repositories:
            raise ValueError('GithubRepositoryReleaseSensor should have at least 1 repository.')

        for repository_dict in repositories:
            self._repositories.append((repository_dict['user'], repository_dict['name']))

    def poll(self):
        for repository_user, repository_name in self._repositories:
            self._logger.info('GithubRepositoryReleaseSensor - Processing repository "%s/%s"' %
                               (repository_user, repository_name))
            repository_obj = self._client.get_user(repository_user).get_repo(repository_name)
            try:
                last_release = repository_obj.get_latest_release()
            except Exception as e:
                self._logger.error('GithubRepositoryReleaseSensor - Error retrieving latest release for repository "%s/%s": %s' %
                                   (repository_user, repository_name, str(e)))
                continue
            full_name = repository_user + '/' + repository_name
            self._process_release(name=full_name,
                                     release=last_release)

    def _process_release(self, name, release):
        """
        Retrieve events for the provided repository and dispatch triggers for
        new events.

        :param name: Repository name.
        :type name: ``str``

        :param repository: Repository object.
        :type repository: :class:`Repository`
        """
        assert(isinstance(name, six.text_type))
        last_published_at = self._get_last_release_published_at(name)
        self._logger.info(f'GithubRepositoryReleaseSensor - Comparing {release.published_at} with {last_published_at}' )
        if release.published_at == last_published_at:
            return
        self._dispatch_trigger_for_release(name, release)
        self._set_last_release_published_at(name, release.published_at)



    def _dispatch_trigger_for_release(self, name, release):
        trigger = self._trigger_ref

        # Common attributes
        payload = release_to_dict(release)
        payload['repository'] = name

        self._sensor_service.dispatch(trigger=trigger, payload=payload)

    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

    def _get_last_release_published_at(self, name):
        """
        :param name: Repository name.
        :type name: ``str``
        """
        if not self._last_published_at.get(name, None) and hasattr(self._sensor_service, 'get_value'):
            key_name = 'last_release_published_at.%s' % (name)
            self._logger.info(f'GithubRepositoryReleaseSensor - key name - {key_name}')
            self._last_published_at[name] = self._sensor_service.get_value(name=key_name)

        return self._last_published_at.get(name, None)

    def _set_last_release_published_at(self, name, last_published_at):
        """
        :param name: Repository name.
        :type name: ``str``
        """
        self._last_published_at[name] = last_published_at

        if hasattr(self._sensor_service, 'set_value'):
            key_name = 'last_release_published_at.%s' % (name)
            self._sensor_service.set_value(name=key_name, value=last_published_at)

