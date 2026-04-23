# This file contains hard-coded variables that are used across the bot,
# this is to avoid hardcoding things in multiple places.

developers_uid = {
    "mahler": 1383041519371685958,
    "adzel": 142854071647338496
}
developers = list(developers_uid.values())
# hardcoded user IDs of the active developers
# these are used for the internal permission system, see config.py and helpers.py for more details
# this is strictly for testing purposes

main_server_id = 1451022861706989712
staff_server_id = 1451282482103062653

staff_entry_channel_id = 1451022863271329814
mainserver_entry_channel_id = 1476358868018659429

owner_role_ids = [1451036920619466862, 1451282482493395126]
admin_role_ids = [1451037130049716295, 1476330523726053376]
mod_role_ids = [1451038256958275594, 1451282482480807981]
helper_role_ids = [1451038323027214377, 1451282482480807980]
#FORMAT: tiername_role_ids = [staff_server_role_id, main_server_role_id]

noperm = "You do not have permission to use this command."
noperm_generic = "You do not have permission to perform this action."
#TODO: add role IDs, helper functions for determining ranks, etc.