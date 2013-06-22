================
Members2Accounts
================

Loading Member file into LDAP in a save manner.

Todo - Bugs - Limitations
-------------------------

1. Race condition in user and groud IDs there is a LDAP method (get+increment?) for this.

1. Handle existing groups.

1. Add everyone to the "everyone" group.

1. Document setup for activation on incoming e-mail.

Ideas for future developments
-----------------------------

1. Send out emails to members that have been created / granted member status.

1. Either be called with file to process or watch directory for new documents.
