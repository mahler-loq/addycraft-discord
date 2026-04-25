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

main_server_id = 1234
staff_server_id = 1234


music_queue_channel_ids = [1234, 1234]

staff_entry_channel_id = 1234
mainserver_entry_channel_id = 1234

owner_role_ids = [1234, 1234]
admin_role_ids = [1234, 1234]
mod_role_ids = [1234, 1234]
helper_role_ids = [1234, 1234]
dj_role_ids = [1234, 1234]
#FORMAT: tiername_role_ids = [staff_server_role_id,main_server_role_id]