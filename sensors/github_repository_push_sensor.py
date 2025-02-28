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


class GithubRepositoryPushSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(GithubRepositoryPushSensor, self).__init__(sensor_service=sensor_service,
                                                     config=config,
                                                     poll_interval=poll_interval)
        self._trigger_ref = 'github.repository_push_event'
        self._logger = self._sensor_service.get_logger(__name__)

        self._client = None
        self._repositories = []
        self._last_pushed_at = {}
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

        repository_push_sensor = self._config.get('repository_push_sensor', None)
        if repository_push_sensor is None:
            raise ValueError('"repository_push_sensor" config value is required.')

        repositories = repository_push_sensor.get('repositories', None)
        if not repositories:
            raise ValueError('GithubRepositoryPushSensor should have at least 1 repository.')

        for repository_dict in repositories:
            self._repositories.append((repository_dict['user'], repository_dict['name']))

    def poll(self):
        for repository_user, repository_name in self._repositories:
            self._logger.info('GithubRepositoryPushSensor - Processing repository "%s/%s"' %
                               (repository_user, repository_name))
            repository_obj = self._client.get_user(repository_user).get_repo(repository_name)
            self._process_repository(name=repository_name,
                                     repository=repository_obj)

    def _process_repository(self, name, repository):
        """
        Retrieve events for the provided repository and dispatch triggers for
        new events.

        :param name: Repository name.
        :type name: ``str``

        :param repository: Repository object.
        :type repository: :class:`Repository`
        """
        assert(isinstance(name, six.text_type))
        last_pushed_at = self._get_last_pushed_at(name)
        self._logger.info(f'GithubRepositoryPushSensor - Comparing {repository.pushed_at} with {last_pushed_at}' )
        if repository.pushed_at == last_pushed_at:
            return
        self._dispatch_trigger_for_repository(repository)
        self._set_last_pushed_at(name, repository.pushed_at)



    def _dispatch_trigger_for_repository(self, repository):
        trigger = self._trigger_ref

        # Common attributes
        payload = {
            'full_name': repository.full_name,
            'pushed_at': repository.pushed_at.strftime(DATE_FORMAT_STRING),
            'created_at': repository.created_at.strftime(DATE_FORMAT_STRING),
        }

        self._sensor_service.dispatch(trigger=trigger, payload=payload)

    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

    def _get_last_pushed_at(self, name):
        """
        :param name: Repository name.
        :type name: ``str``
        """
        if not self._last_pushed_at.get(name, None) and hasattr(self._sensor_service, 'get_value'):
            key_name = 'last_pushed_at.%s' % (name)
            self._logger.info(f'GithubRepositoryPushSensor - key name - {key_name}')
            self._last_pushed_at[name] = self._sensor_service.get_value(name=key_name)

        return self._last_pushed_at.get(name, None)

    def _set_last_pushed_at(self, name, last_pushed_at):
        """
        :param name: Repository name.
        :type name: ``str``
        """
        self._last_pushed_at[name] = last_pushed_at

        if hasattr(self._sensor_service, 'set_value'):
            key_name = 'last_pushed_at.%s' % (name)
            self._sensor_service.set_value(name=key_name, value=last_pushed_at)

