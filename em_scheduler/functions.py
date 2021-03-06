"""Scheduler Event Logging."""
# Extract Management 2.0
# Copyright (C) 2020  Riverside Healthcare, Kankakee, IL

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import hashlib
import time

from requests import get

from em_scheduler.extensions import db, scheduler
from em_scheduler.model import Task


def scheduler_delete_all_tasks():
    """Delete all jobs associated with a task from the scheduler.

    :returns: true
    """
    for job in scheduler.get_jobs():
        if job.args:
            job.remove()

    return True


def scheduler_delete_task(task_id):
    """Delete all jobs associated with a task from the scheduler.

    :param task_id: id of task to delete associated jobs
    :returns: true
    """
    for job in scheduler.get_jobs():
        if job.args and str(job.args[0]) == str(task_id):
            job.remove()

    return True


def scheduler_task_runner(task_id):
    """Send request to runner api to run task.

    :param task_id: id of task to run
    """
    try:
        with scheduler.app.app_context():
            get(scheduler.app.config["RUNNER_HOST"] + "/" + task_id)
    # pylint: disable=broad-except
    except BaseException as e:
        print("failed to run job.")  # noqa: T001
        print(str(e))  # noqa: T001
        raise e


def scheduler_add_task(task_id):
    """Create job for task in the scheduler.

    :param task_id: id of task to create a schedule for

    *Parameters for APScheduler*

    :func: function to run
    :trigger: date, interval or cron
    :id: used to match job up to db
    :name: desc of job
    :misfire_grace_time: seconds a job can run late
    :coalesce: merge mul into one run
    :max_instances: max concurrent runs allowed
    :next_run_time: when to start schedule (None: job paused)
    :jobstore: alias of jobstore to use
    :executor: alias of excutor to use
    :replace_existing: true to replace jobs with same id

    *Parameters for Cron Jobs*

    :year: 4 digit year
    :month: 1-12
    :day: 1-31
    :week: 1-53
    :day_of_week: 0-6 or mon,tue,wed,thu,fri,sat,sun
    :hour: 0-23
    :minute: 0-59
    :second: 0-59
    :start_date: (datetime) soonest start
    :end_date: (datetime) latest run

    *Paramters for Interval Jobs*

    :weeks: (int) number of weeks between runs
    :days: (int) number of days between runs
    :hours: (int) number of hours between runs
    :minutes: (int) number of minutes between runs
    :seconds: (int) number of seconds between runs
    :start_date: (datetime) soonest start date
    :end_date: (datetime) latest run date

    *Parameters for One Off Jobs*

    :run_date: (datetime) when to run

    *Notes*

    If multiple triggers are specified on the task a schedule will be added for each trigger
    type. So it is possible to have multiple triggers per task. Because of this, the id
    assigned to the job is project_id-task_id-<time hash>. The tasks id is sent as an arg
    to the job.

    """
    task = Task.query.filter_by(id=task_id).first()

    # fyi, task must be re-queried after each type is
    # scheduled, as the scheduler events will modify
    # the task causing a session break!!
    if not task:
        return False

    task.enabled = 1
    db.session.commit()

    my_hash = hashlib.sha256()

    # schedule cron
    if task.project.cron == 1:
        project = task.project
        scheduler.add_job(
            func=scheduler_task_runner,
            trigger="cron",
            second=project.cron_sec,
            minute=project.cron_min,
            hour=project.cron_hour,
            year=project.cron_year,
            month=project.cron_month,
            week=project.cron_week,
            day=project.cron_day,
            day_of_week=project.cron_week_day,
            start_date=project.cron_start_date,
            end_date=project.cron_end_date,
            args=[str(task_id)],
            id=str(project.id) + "-" + str(task.id) + "-cron",
            name="(cron) " + project.name + ": " + task.name,
            replace_existing=True,
        )

    # schedule interval
    task = Task.query.filter_by(id=task_id).first()
    if task.project.intv == 1:
        project = task.project
        weeks = project.intv_value or 999 if project.intv_type == "w" else 0
        days = project.intv_value or 999 if project.intv_type == "d" else 0
        hours = project.intv_value or 999 if project.intv_type == "h" else 0
        minutes = project.intv_value or 999 if project.intv_type == "m" else 0
        seconds = project.intv_value or 999 if project.intv_type == "s" else 0

        scheduler.add_job(
            func=scheduler_task_runner,
            trigger="interval",
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks,
            start_date=project.intv_start_date,
            end_date=project.intv_end_date,
            args=[str(task_id)],
            id=str(project.id) + "-" + str(task.id) + "-intv",
            name="(inverval) " + project.name + ": " + task.name,
            replace_existing=True,
        )

    # ooff tasks use a hash to identify jobs as a job can have multiple one-off runs scheduled.
    task = Task.query.filter_by(id=task_id).first()
    if task.project.ooff == 1:
        project = task.project
        my_hash.update(str(time.time()).encode("utf-8"))
        scheduler.add_job(
            func=scheduler_task_runner,
            trigger="date",
            run_date=project.ooff_date,
            args=[str(task_id)],
            id=str(project.id) + "-" + str(task.id) + "-" + my_hash.hexdigest()[:10],
            name="(one off) " + project.name + ": " + task.name,
            replace_existing=True,
        )

    return True
