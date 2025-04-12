import abstra.forms as af
from abstra.tasks import get_tasks, send_task
import pandas as pd

# replace "_" by " " on the key and captalizes it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()

# get the data from the task payload
tasks = get_tasks()
for task in tasks:

    payload = task.get_payload()

    mismatch_dict = payload["mismatch_info"]
    register_dict = payload["register_info"]
    paths_dict = payload["paths"]

    mismatch_df = {transform_to_label(key): register_dict[key] for key in mismatch_dict.keys() if not(mismatch_dict[key])}
    mismatch_df = pd.DataFrame(list(mismatch_df.items()), columns=["Label", "Value"])

    # build the page where the data provided will be mannually verified
    mismatch_page = (
        af.Page()
        .display(f'The AI found an error on the following information provided by {register_dict["name"]}:')
        .display_pandas(mismatch_df)
        .display("Please check it according to the following documents provided:")
        .display_image(paths_dict["id_front_page"])
        .display_image(paths_dict["id_back_page"])
        .display_image(paths_dict["address_proof"])
        .read_multiple_choice(
            "Is the information provided correct ?",
            ["Yes", "No"],
            key="is_info_correct"
        )
        .run()
    )

    # send the task to the next step
    if(mismatch_page["is_info_correct"] == "Yes"):
        send_task("manual_match", payload)
    else:
        send_task("manual_mismatch", payload)

    task.complete()