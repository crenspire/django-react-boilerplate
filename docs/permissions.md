# Permissions

The admin console follows Django admin's model — staff status plus model permissions — with extra rules that stop staff users from escalating their own access. All rules live in [`apps/admin_panel/domain/policies.py`](../starterkit/apps/admin_panel/domain/policies.py) and are enforced in services, never in React.

## Signing in

A user can sign in to `/admin/` when they are **active** and **staff**. Every other account gets the same generic error, so the form cannot be used to discover which accounts exist or are inactive.

Failed sign-ins are throttled per username + client IP and per client IP (`ADMIN_LOGIN_MAX_ATTEMPTS` failures within `ADMIN_LOGIN_LOCKOUT_SECONDS`). See [Configuration](configuration.md).

## What each action needs

Superusers pass every check. Other staff need the matching Django model permission, granted directly or through a group:

| Action | Permission |
|---|---|
| View the users list | `auth.view_user` or `auth.change_user` |
| Create users | `auth.add_user` |
| Edit users | `auth.change_user` |
| Delete users | `auth.delete_user` |
| View the groups list | `auth.view_group` or `auth.change_group` |
| Create / edit / delete groups | `auth.add_group` / `auth.change_group` / `auth.delete_group` |

The dashboard is available to every staff user; its statistics and quick actions only show what the user may access. The sidebar and ⌘K palette are built from the same rules on the server.

## Privilege changes are superuser-only

Changing any of these requires a superuser, even for staff who hold `change_user` or `change_group`:

- staff status
- superuser status
- group membership
- a group's permissions

Non-superusers can only edit and delete accounts that have neither staff nor superuser status. In the UI these controls are disabled with an explanation; on the server the change is rejected with a field error.

## Self-lockout protection

Nobody can:

- delete their own account
- deactivate their own account
- remove their own staff status
- remove their own superuser status

## Common setups

**Support agent** — can look people up and fix profile details, nothing more:

1. Create a group "Support" with `auth.view_user` and `auth.change_user`.
2. Create the agent as a staff user and add them to the group (as a superuser).

**Auditor** — read-only access to users and groups: a group with `auth.view_user` and `auth.view_group`.

## Changing the rules

Edit the policy functions and their tests in `apps/admin_panel/tests/test_policies.py`. Because services call policies and the UI only renders the `can` flags services return, a policy change applies everywhere at once.
