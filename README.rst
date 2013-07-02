================
Members2Accounts
================

Loading JSON Member file into LDAP as accounts.

The JSON file contains all the members. Any members that do not yet have a LDAP account are created.

Anybody who is not there is a non-member and is removed from

Installation and deployment details
-----------------------------------

1. Obtain the project from the respository.

#. Create a GnuPG key pair specifically for this service. ``gpg --gen-key``. Do *not* give it a passphrase. Export the
   new public key and give it to the generators of the member file. This is the key they will need to have the public key
   of to encrypt.

#. In the process-keyring import the public-keys of all people going to do the signing, make sure you verify the
   signer-keys and trust them in the process-keyring.

#. Setup the software by running ``setup.py`` #. This will download the dependencies.
   If you wish to use virtualenv (recommended) run it virtualenv activated.

#. Run ``members2accounts -W config.json`` # This will generate a json file with all the configuration options.
   Change the options as needed. Any option you do not change, you can remove from the configuration file.
   You *must* atleast change the following entries.

   - ``gpg.my_id`` contains the full fingerprint of the key that the process uses. Member messages
     are encrypted with this key.

   - ``gpg.signer_ids``: List of fingerprints of keys that are allowed to send member files.

   - ``ldap.uri``: The URI of  the LDAP server.

   - ``ldap.user``: The distinguished (DN) name of the LDAP account the process will use to create and modify accounts.

   - ``ldap.password``: The password of the ldap account


Example LDAP Schema
-------------------

This schema was inspired on the SpaceFED LDAP schema (https://spacefed.net/wiki/index.php/Howto/Spacenet/Setup_LDAP)


Todo - Bugs - Limitations
-------------------------

1. Race condition in user and group IDs there is a LDAP method (get+increment?) for this.

1. The GnuPG key cannot have a password at the moment. The reasoning is that if the attacker has access to the
   gpg keys, they will also have access to the configuration file and then obtain the LDAP account details and
   GnuPG passphrases anyway.

Ideas for future developments
-----------------------------

1. Add SAMBA structure when creating new accounts. Also add the right attributes.

#. Send out emails to members that have been created / granted member status.

#. Send an email with the results of the update back to the signer of the member document.

#. Use the password store provided by OS to store the LDAP and GnuPG keys.