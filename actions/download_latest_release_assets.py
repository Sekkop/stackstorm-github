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

            # Create the directory if it doesn't exist
            try:
                os.makedirs(path)
            except Exception:
                pass

            # Remove the file if it already exists
            try:
                os.remove(file_path)
            except Exception:
                pass



            asset.download_asset(file_path)
            results.append({'name': asset.name, 'path': file_path})

        return results
