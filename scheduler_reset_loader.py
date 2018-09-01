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
# !/usr/bin/env python
from logging import config

from apscheduler.schedulers.blocking import BlockingScheduler
from globomap_monitoring import zbx_passive

from globomap_loader.loader.loader import CoreLoader
from globomap_loader.settings import LOGGING
from globomap_loader.settings import SCHEDULER_FREQUENCY_EXEC
from globomap_loader.settings import ZBX_PASSIVE_MONITOR_SCHEDULER

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='0-6', hour=SCHEDULER_FREQUENCY_EXEC)
def run_loader():
    config.dictConfig(LOGGING)
    CoreLoader().full_load()


@sched.scheduled_job('interval', seconds=60)
def job_monitoracao_zabbix():
    zbx_passive.send(ZBX_PASSIVE_MONITOR_SCHEDULER)


if __name__ == '__main__':
    sched.start()
