"""
   Copyright 2018 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from logging import config

from apscheduler.schedulers.blocking import BlockingScheduler
from globomap_monitoring import zbx_passive

from globomap_loader.loader.loader import CoreLoader
from globomap_loader.settings import LOGGING
from globomap_loader.settings import ZBX_PASSIVE_MONITOR_LOADER

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=60)
def job_monitoracao_zabbix():
    zbx_passive.send(ZBX_PASSIVE_MONITOR_LOADER)


if __name__ == '__main__':
    config.dictConfig(LOGGING)

    CoreLoader().load()

    sched.start()
