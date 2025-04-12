from abstra.tasks import get_trigger_task, send_task

task = get_trigger_task()
payload = task.get_payload()

status_values = "approved,not_approved".split(",")
approval_status = payload["approval_status"]

for status in status_values:
    if approval_status == status:
        send_task(approval_status, payload)

task.complete()
