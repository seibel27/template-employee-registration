import abstra.forms as af
from abstra.tasks import get_tasks, send_task
from abstra.tables import insert 


# replace "_" by " " on the key and captalizes it to display as label on the form
def transform_to_label(key):
    return key.replace("_", " ").capitalize()


# checks with the user if the data is correct
def render_info_update(partial):
    print("printing partial")
    print(partial)
    print("printing partial keys")
    print(partial.keys())
    if "is_data_error" in partial.keys():
        print("printing partial[is_data_error] in the first stage")
        print(partial["is_data_error"])
        if (partial["is_data_error"] == "Yes"):
            print("printing partial[is_data_error] in the second stage")
            print(partial["is_data_error"])
            print("i got to the first if")
            update_page = af.Page().display("Please check the following information regarding your data")
            if contract_data_dict:
                print("i got to the second if")
                for key in contract_data_dict.keys():
                    update_page = (
                        update_page.read(f"{transform_to_label(key)}:", key=key, initial_value=contract_data_dict[key])
                    )
                    print("im inside the for loop")
            else:
                print("i got to the else")
                for key in register_dict.keys():
                    update_page = (
                        update_page.read(f"{transform_to_label(key)}:", key=key, initial_value=register_dict[key])
                    )
                    print("im inside the second for loop")
            print("im gonna return the update page")
            return update_page


# asks about the error if the employer rejects the document
def render_contract_comments(partial):
    if len(partial) != 0:
        if (partial["is_contract_error"] == "Yes"):
            return(
                af.Page()
                .read_textarea(
                    "Comments",
                    required=False,
                    placeholder="Put here your comments about the problems",
                    key="comments",
                )
                .read_multiple_choice(
                    "Does the contract have error regarding your information?",
                    ["Yes", "No"],
                    key="is_data_error"
                )
                .reactive(render_info_update)
            )

# defining outside the loop
register_dict = {}
contract_dict = {}
contract_data_dict = {}
# get the data from the task payload
tasks = get_tasks()
for task in tasks:

    payload = task.get_payload()

    register_dict = payload["register_info"]
    contract_dict = payload["contract_path"]
    contract_data_dict = payload["contract_data"]

    contract_filename = contract_dict["contract_filename"]
    employee_name = register_dict["name"]
    contract_filepath = contract_dict["contract_filepath"]

    # page about the contract approval or rejection 
    contract_status_page =(
        af.Page()
        .display(f"Document Approval - {contract_filename}", size="large")
        .display(
            f'Please read the "{contract_filename}" document related to the hiring of {employee_name} and approve/reject it'
        )
        .display_file(contract_filepath, dowload_text="Click here to download the document")
        .run(actions=["Approve", "Reject"])
    )

    if contract_status_page.action == "Reject":
        contract_reject_page = (
            af.Page()
            .read_multiple_choice(
                "Does the contract have any error or a clause you disagree with?",
                ["Yes", "No"],
                key="is_contract_error"
            )
            .reactive(render_contract_comments)
            .run("Send")
        )

        payload["approval_status"] = "not_approved"
        data_error_log = {}
        if (contract_reject_page["is_data_error"] == "Yes"):
            if contract_data_dict:
                for key in contract_data_dict.keys():
                    if (key in contract_reject_page.keys()):
                        if contract_data_dict[key] != contract_reject_page[key]:
                            data_error_log[key] = [contract_data_dict[key], contract_reject_page[key]]
            else:
                for key in register_dict.keys():
                    if key in contract_reject_page.keys():
                        if register_dict[key] != contract_reject_page[key]:
                            data_error_log[key] = [register_dict[key], contract_reject_page[key]]

        payload["data_error_log"] = data_error_log
        payload["comments"] = contract_reject_page.get("comments", "")

    else:
        payload["approval_status"] = "approved"

        adding_member = insert(
            "employee_register",
            register_dict,
        )

    send_task("approval_status", payload)
    task.complete()