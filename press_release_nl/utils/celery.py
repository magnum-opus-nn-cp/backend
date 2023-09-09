from config.celery_app import app


def get_scheduled_tasks_name() -> [str]:
    i = app.control.inspect()
    t = i.active()
    all_tasks = []
    for worker, tasks in t.items():
        all_tasks += tasks
    return [x["name"] for x in all_tasks]
