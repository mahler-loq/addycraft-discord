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

main_server_id = 1451282482103062653
staff_server_id = 1451022861706989712


music_queue_channel_ids = [1497731786107785256,1497740461786398890]

staff_entry_channel_id = 1451022863271329814
mainserver_entry_channel_id = 1476358868018659429

bolo_channel_id = 1496237433971544238

owner_role_ids = [1451282482493395126,1451036920619466862]
sr_admin_role_ids = [1451282482480807984,1451038062258688105]
admin_role_ids = [1234,1234]
sr_mod_role_ids = [1234,1234]
mod_role_ids = [1451282482480807981,1451038256958275594]
helper_role_ids = [1451282482480807980,1451038323027214377]
dj_role_ids = [1497742878628384940,1488303234581008574]
developer_role_ids = [1477336375769694392,1451282482480807983]
builder_role_ids = [1466218224319201377,1451282482480807982]
artist_role_ids = [1234,1234]
paid_rank_role_ids = {
    1234: 1234
}
monthly_rank_role_id = 1234
#FORMAT: tiername_role_ids = [staff_server_role_id,main_server_role_id]