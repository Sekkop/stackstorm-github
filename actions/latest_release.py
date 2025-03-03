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

import time
import datetime

from lib.base import BaseGithubAction


class LatestReleaseAction(BaseGithubAction):
    def run(self, repository):
        repo = self._client.get_repo(repository)
        latest = repo.get_latest_release()

        results = {'author': latest.author.login,
                   'avatar_url': latest.author.avatar_url,
                   'html_url': latest.html_url,
                   'tag_name': latest.tag_name,
                   'target_commitish': latest.target_commitish,
                   'name': latest.title,
                   'body': latest.body,
                   'draft': latest.draft,
                   'prerelease': latest.prerelease,
                   'created_at': latest.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                   'published_at': latest.published_at.strftime('%Y-%m-%d %H:%M:%S'),
                   'total_assets': len(latest.assets)}

        return results
