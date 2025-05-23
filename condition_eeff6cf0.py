from abstra.tasks import get_trigger_task, send_task

task = get_trigger_task()
payload = task.get_payload()

condition_values = "True,False".split(",")
condition = payload.get("is_manual_checked", None)

for condition_value in condition_values:
    if condition is not None and condition == condition_value:
        dto = task.get_dto()
        send_task(condition_value, payload)

task.complete()
