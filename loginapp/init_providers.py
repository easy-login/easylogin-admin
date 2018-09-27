import MySQLdb
import json

providers = [
    {
        "name": "line",
        "version": ["v2.1"],
        "required_permissions": "openid",
        "basic_fields": [
            {
                "key": "displayName",
                "name": "Display Name",
                "permission": "profile"
            },
            {
                "key": "pictureUrl",
                "name": "Picture URL",
                "permission": "profile"
            },
            {
                "key": "statusMessage",
                "name": "Status Message",
                "permission": "profile"
            }
        ],
        "advanced_fields": [
            {
                "key": "email",
                "name": "Email",
                "permission": "email"
            }
        ],
        "options": [
            {
                "key": "add_friend",
                "name": "Add friend",
                "default": True,
                "tooltip": "Show checkbox add LINE user as friend after logged in"
            }
        ]
    },
    {
        "name": "amazon",
        "version": ["v2"],
        "required_permissions": "profile:user_id",
        "basic_fields": [
            {
                "key": "name",
                "name": "Full Name",
                "permission": "profile"
            },
            {
                "key": "postal_code",
                "name": "Postal Code",
                "permission": "postal_code"
            }
        ],
        "advanced_fields": [
            {
                "key": "email",
                "name": "Email",
                "permission": "profile"
            }
        ]
    },
    {
        "name": "amazon",
        "version": ["v3"],
        "required_permissions": "profile:user_id",
        "basic_fields": [
            {
                "key": "namev3",
                "name": "Full Namev3",
                "permission": "profilev3"
            },
            {
                "key": "postal_codev3",
                "name": "Postal Codev3",
                "permission": "postal_codev3"
            }
        ],
        "advanced_fields": [
            {
                "key": "emailv3",
                "name": "Emailv3",
                "permission": "profilev3"
            }
        ]
    },
    {
        "name": "yahoojp",
        "version": ["v2"],
        "required_permissions": "openid",
        "basic_fields": [
            {
                "key": "name",
                "name": "Full Name",
                "permission": "profile"
            },
            {
                "key": "given_name",
                "name": "First Name",
                "permission": "profile"
            },
            {
                "key": "family_name",
                "name": "Last Name",
                "permission": "profile"
            },
            {
                "key": "gender",
                "name": "Gender",
                "permission": "profile"
            },
            {
                "key": "zoneinfo",
                "name": "Zone Info",
                "permission": "profile"
            },
            {
                "key": "locale",
                "name": "Locale",
                "permission": "profile"
            },
            {
                "key": "nickname",
                "name": "Nick Name",
                "permission": "profile"
            },
            {
                "key": "picture",
                "name": "Picture URL",
                "permission": "profile"
            }
        ],
        "advanced_fields": [
            {
                "key": "email",
                "name": "Email",
                "permission": "email"
            },
            {
                "key": "email_verified",
                "name": "Email Verified",
                "permission": "email"
            },
            {
                "key": "birth_date",
                "name": "Birth Date",
                "permission": "profile"
            },
            {
                "key": "address",
                "name": "Address",
                "permission": "address"
            }
        ]
    }
]

if __name__ == '__main__':
    data = []
    for provider in providers:
        for version in provider['version']:
            tup = (
                provider['name'],
                version,
                provider['required_permissions'],
                json.dumps(provider['basic_fields']),
                json.dumps(provider['advanced_fields']),
                json.dumps(provider.get('options', []))
            )
            print(tup)
            data.append(tup)

    db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='sociallogin')
    cursor = db.cursor()
    cursor.executemany("""
        INSERT INTO providers (name, version, required_permissions, basic_fields, advanced_fields, options) 
        VALUES (%s, %s, %s, %s, %s, %s)""", data)

    db.commit()
    db.close()
