__author__ = 'chotee'

import pytest
from datetime import date

from memberizer.accounts import Accounts, Account

import ldap
from fakeldap import MockLDAP
from mocks import Mock_Member

from memberizer.exc import *

@pytest.fixture
def fake_accounts(monkeypatch):

    initial_directory = {
        'cn=NextFreeUnixId,dc=techinc,dc=nl': {
            'objectClass': ['inetOrgPerson', 'sambaUnixIdPool'],
            'gidNumber': ['777'],
            'uidNumber': ['666'],
            'cn': ['NextFreeUnixId'],
            'sn': ['NextFreeUnixId']
        },
        'cn=everybody,ou=groups,dc=techinc,dc=nl': {
            'cn': ['everybody']
        },
        'cn=members,ou=groups,dc=techinc,dc=nl': {
            'cn': ['members']
        }
    }
    mock_ldap_conn = MockLDAP(directory=initial_directory)

    people = {
        'existing':
            ('cn=existing,ou=people,dc=techinc,dc=nl',
             {
                'objectClass': ['inetOrgPerson', 'posixAccount', 'top'],
                'cn': ['existing'], 'sn': ['existing'], 'uid': ['existing'],
                'homeDirectory': ['/home/existing'],
                'mail': ['existing@techinc.nl'],
                'telexNumber': ['2013-12-01'],
                'uidNumber': ['501'], 'gidNumber': ['500'],
             }),
        'anotherMember':
            ('cn=anotherMember,ou=people,dc=techinc,dc=nl',
             {
                'objectClass': ['inetOrgPerson', 'posixAccount', 'top'],
                'cn': ['anotherMember'], 'sn': ['anotherMember'], 'uid': ['anotherMember'],
                'homeDirectory': ['/home/anotherMember'],
                'mail': ['anotherMember@techinc.nl'],
                'telexNumber': ['2013-12-15'],
                'uidNumber': ['502'], 'gidNumber': ['501'],
             })
    }

    a = Accounts(mock_ldap_conn)
    a._conn.set_return_value('search_s',
        #(base, scope, filterstr, attrlist, attrsonly),
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_BASE , '(objectClass=*)', None, 0),
            [
                ('ou=people,dc=techinc,dc=nl',
                {'objectClass': ['organizationalUnit', 'top'],
                 'ou': ['people']})
            ]
    )
    a._conn.set_return_value('search_s',
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(&(mail=existing@techinc.nl)(objectClass=inetOrgPerson))',
         None, 0),
        [
            people['existing']
        ]
    )
    a._conn.set_return_value('search_s',
       ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(|(cn=existing)(cn=anotherMember))', None, 0),
       [
           people['existing'],
           people['anotherMember']
       ]
    )
    a._conn.set_return_value('search_s',
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(&(objectClass=inetOrgPerson)(cn=testcreate))',
         None, 0),
        []
    )
    a._conn.set_return_value('search_s',
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(&(objectClass=inetOrgPerson)(cn=group_already_exists))',
         None, 0),
        []
    )
    a._conn.set_return_value('search_s',
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(&(mail=doesnotexist@techinc.nl)(objectClass=inetOrgPerson))',
         None, 0),
        []
    )
    a._conn.set_return_value('search_s',
        ('cn=NextFreeUnixId,dc=techinc,dc=nl', ldap.SCOPE_BASE, '(objectClass=*)', None, 0),
        [
            ('cn=NextFreeUnixId,dc=techinc,dc=nl',
             {'cn': ['NextFreeUnixId'],
              'gidNumber': ['777'],
              'objectClass': ['inetOrgPerson', 'sambaUnixIdPool'],
              'sn': ['NextFreeUnixId'],
              'uidNumber': ['666']}
            )
        ]
    )
    a._conn.set_return_value('search_s',
       ('ou=groups,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(cn=members)', None, 0),
       [
           ('cn=members,ou=groups,dc=techinc,dc=nl',
            {'cn': ['members'],
             'gidNumber': ['700'],
             'memberUid': ['existing', 'anotherMember'],
             'objectClass': ['posixGroup', 'top']
            }
           )
       ]
    )
    a._conn.set_return_value('search_s',
        ('ou=groups,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(memberUid=afakeaccount)', None, 0),
        []
    )
    a._conn.set_return_value('add_s',
        ('cn=group_already_exists,ou=groups,dc=techinc,dc=nl',
         (('cn', 'group_already_exists'),
          ('memberUid', 'group_already_exists'),
          ('gidNumber', '777'),
          ('objectClass',
           ('posixGroup', 'top')))),
        ldap.ALREADY_EXISTS()
    )
    return a

@pytest.fixture
def a_fake_account(fake_accounts):
    accounts = fake_accounts
    account = accounts.new_account()
    member_original = Mock_Member(nickname="afakeaccount", email="afakeaccount@techinc.nl", paid_until=date(2013, 8, 12))
    account.load_account_from_member(member_original)
    return account

class TestAccount(object):
    def test_load_from_member(self, fake_accounts):
        member = Mock_Member(nickname="existing", email="existing@techinc.nl", paid_until=date(2013,12,1))
        a = Account(fake_accounts._conn)
        a.load_account_from_member(member)
        assert a.nickname == "existing"
        assert a.email == 'existing@techinc.nl'
        assert a.paid_until == date(2013, 12, 1)

    def test_create(self, fake_accounts):
        accounts = fake_accounts
        member = Mock_Member(nickname="testcreate", email="test@techinc.nl", paid_until=date(2013, 8, 12))
        account = accounts.new_account()
        account.load_account_from_member(member)
        assert account.email == "test@techinc.nl"
        assert account.nickname == "testcreate"
        assert account.paid_until == date(2013, 8, 12)
        assert account.in_ldap == False
        assert account.is_dirty
        account.save()
        assert account.in_ldap == True
        assert not account.is_dirty

    def test_create_invalid_member(self, fake_accounts):
        accounts = fake_accounts
        account = accounts.new_account()
        member_original = Mock_Member(nickname="", email="test@techinc.nl", paid_until=date(2013, 8, 12))
        pytest.raises(MemberNotValidException, account.load_account_from_member, member_original)

    def test_create_account_group_already_exists(self, fake_accounts):
        accounts = fake_accounts
        member = Mock_Member(nickname="group_already_exists", email="group_already_exists@techinc.nl", paid_until=date(2013, 8, 12))
        account = accounts.new_account()
        account.load_account_from_member(member)
        account.save()

    def test_getter_and_setters(self, fake_accounts):
        accs = fake_accounts
        a = accs.new_account()
        assert None == a.nickname
        assert a.is_dirty == False
        a.nickname = "testnick"
        assert "testnick" == a.nickname
        assert a.is_dirty == True
        a = accs.new_account()
        assert None == a.email
        assert a.is_dirty == False
        a.email = "testnick@techinc.nl"
        assert "testnick@techinc.nl" == a.email
        assert a.is_dirty == True
        a = accs.new_account()
        assert None == a.paid_until
        assert a.is_dirty == False
        a.paid_until = date(2013, 8, 20)
        assert a.is_dirty == True

    def test_update(self, fake_accounts):
        accounts = fake_accounts
        account = accounts.new_account()
        member_original = Mock_Member(nickname="testcreate", email="test@techinc.nl", paid_until=date(2013, 8, 12))
        assert account.is_dirty == False
        account.load_account_from_member(member_original)
        assert account.is_dirty == True
        account.save()
        assert account.is_dirty == False
        member_updated = Mock_Member(nickname="testcreate", email="test@techinc.nl", paid_until=date(2013, 10, 30))
        account.load_account_from_member(member_updated)
        assert account.is_dirty == True
        account.save()
        assert account.is_dirty == False

    def test_make_member(self, a_fake_account):
        account = a_fake_account
        assert account.is_member == False
        account.grant_membership()
#        assert account.is_member == True
        account.revoke_membership()
        assert account.is_member == False

    def test_ldap_data_missing_paid_until(self, fake_accounts):
        accounts = fake_accounts
        a = accounts.new_account()
        account_info = (
            'cn=no_paid_until,ou=people,dc=techinc,dc=nl',
            {'cn': 'no_paid_until',
             'mail': 'no_paid@techinc.nl'
            }
        )
        a.load_from_ldap_account_info(account_info)
        assert None == a.paid_until

class TestAccounts(object):
    def test_verify_connection(self, fake_accounts):
        a = fake_accounts
        a.verify_connection()

    def test_get_all_member_accounts(self, fake_accounts):
        a = fake_accounts
        res = a.get_all_member_accounts()
        assert 2 == len(res)
        assert 'existing' == res[0].nickname
