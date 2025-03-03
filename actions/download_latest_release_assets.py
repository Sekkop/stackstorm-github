import time
import datetime
import os
from lib.base import BaseGithubAction


class DownloadLatestReleaseAssetsAction(BaseGithubAction):
    def run(self, repository, path):
        repo = self._client.get_repo(repository)
        latest = repo.get_latest_release()
        assets = latest.get_assets()

        results = []
        for asset in assets:
            file_path = os.path.join(path, asset.name)
            asset.download_asset(file_path)
            results.append({'name': asset.name, 'path': file_path})

        return results
