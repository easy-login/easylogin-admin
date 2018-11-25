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
                "default": False,
                "tooltip": "Show checkbox add LINE user as friend after logged in",
                "restrict_levels": "1|2"
            },
            {
                "key": "add_wife",
                "name": "Add wife",
                "default": False,
                "tooltip": "show show cc",
            }
        ]
    },
    {
        "name": "amazon",
        "version": ["v2"],
        "required_permissions": "profile:user_id|payments:widget",
        "basic_fields": [
            {
                "key": "name",
                "name": "Full Name",
                "permission": "profile"
            },
            {
                "key": "email",
                "name": "Email",
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
                "key": "shipping_address",
                "name": "Payments Shipping Address",
                "permission": "payments:shipping_address"
            },
            {
                "key": "billing_address",
                "name": "Payments Billing Address",
                "permission": "payments:billing_address"
            }
        ],
        "options": [
            {
                "key": "add_cmm",
                "name": "Add CMM",
                "default": True,
                "tooltip": "Show checkbox add CMM",
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
    },
    {
        "name": "facebook",
        "version": ["v3.1"],
        "required_permissions": "public_profile",
        "basic_fields": [
            {
                "key": "first_name",
                "name": "First Name",
                "permission": "public_profile"
            },
            {
                "key": "last_name",
                "name": "Last Name",
                "permission": "public_profile"
            },
            {
                "key": "middle_name",
                "name": "Middle Name",
                "permission": "public_profile"
            },
            {
                "key": "name",
                "name": "Name",
                "permission": "public_profile"
            },
            {
                "key": "picture",
                "name": "Picture URL",
                "permission": "public_profile"
            },
            {
                "key": "email",
                "name": "Email",
                "permission": "email"
            }
        ],
        "advanced_fields": [
            {
                "key": "age_range",
                "name": "Age Range",
                "permission": "user_age_range"
            },
            {
                "key": "birthday",
                "name": "Birthday",
                "permission": "user_birthday"
            },
            {
                "key": "gender",
                "name": "Gender",
                "permission": "user_gender"
            },
            {
                "key": "hometown",
                "name": "Hometown",
                "permission": "user_hometown"
            },
            {
                "key": "likes",
                "name": "User Likes",
                "permission": "user_likes"
            },
            {
                "key": "link",
                "name": "Timeline Link",
                "permission": "user_link"
            },
            {
                "key": "location",
                "name": "Location",
                "permission": "user_location"
            }
        ]
    },
    {
        "name": "twitter",
        "version": ["v3.1"],
        "required_permissions": "public_profile",
        "basic_fields": [
            {
                "key": "first_name",
                "name": "First Name",
                "permission": "public_profile"
            },
            {
                "key": "last_name",
                "name": "Last Name",
                "permission": "public_profile"
            },
            {
                "key": "middle_name",
                "name": "Middle Name",
                "permission": "public_profile"
            },
            {
                "key": "name",
                "name": "Name",
                "permission": "public_profile"
            },
            {
                "key": "picture",
                "name": "Picture URL",
                "permission": "public_profile"
            },
            {
                "key": "email",
                "name": "Email",
                "permission": "email"
            }
        ],
        "advanced_fields": [
            {
                "key": "age_range",
                "name": "Age Range",
                "permission": "user_age_range"
            },
            {
                "key": "birthday",
                "name": "Birthday",
                "permission": "user_birthday"
            },
            {
                "key": "gender",
                "name": "Gender",
                "permission": "user_gender"
            },
            {
                "key": "hometown",
                "name": "Hometown",
                "permission": "user_hometown"
            },
            {
                "key": "likes",
                "name": "User Likes",
                "permission": "user_likes"
            },
            {
                "key": "link",
                "name": "Timeline Link",
                "permission": "user_link"
            },
            {
                "key": "location",
                "name": "Location",
                "permission": "user_location"
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
