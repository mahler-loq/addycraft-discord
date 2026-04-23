# This file is for any configuration option that can define how the bot behaves on certain events or situations.

AUTOLEAVE_UNTRUSTED_SERVERS = False
# auto-leaves any server that is not MAIN or STAFF on any event

HELPERS_ARE_STAFF = True
# if True, helpers are considered staff and have access to the permissions intended for their rank, if False, consider them members when checking
# for permissions to execute actions

STRICT_SECURITY = False
# enables AUTOLEAVE_UNTRUSTED_SERVERS and overrides HELPERS_ARE_STAFF, disabling it

CONST_DEVELOPERS_MAXPERM_DEBUG = True
# if True, users hardcoded in src/cnst.py::developers_uid will be considered tier 0 (max permissions)
# this is strictly for testing purposes, and should be set to False when in production use
# Hardcoded users in src/cnst.py::developers_uid will still have a minimum tier of 2 (moderator) if this is set to False
