# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and

from lib.base import BaseGithubAction


class ListReleasesAction(BaseGithubAction):
    def run(self, repository):
        results = []
        repo = self._client.get_repo(repository)
        releases = repo.get_releases()

        for release in releases:
            results.append(
                {'author': release.author.login,
                 'avatar_url': release.author.avatar_url,
                 'html_url': release.html_url,
                 'tag_name': release.tag_name,
                 'target_commitish': release.target_commitish,
                 'name': release.title,
                 'body': release.body,
                 'draft': release.draft,
                 'prerelease': release.prerelease,
                 'created_at': release.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                 'published_at': release.published_at.strftime('%Y-%m-%d %H:%M:%S'),
                 'total_assets': len(release.assets)})

        return results
