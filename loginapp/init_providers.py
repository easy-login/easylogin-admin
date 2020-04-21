import MySQLdb
import json
from urllib import parse as up

providers = [
    {
        "name": "line",
        "version": ["v2.1"],
        "required_permissions": "openid",
        "basic_fields": [
            "displayName,Display Name,profile",
            "pictureUrl,Picture URL,profile",
            "statusMessage,Status Message,profile"
        ],
        "advanced_fields": [
            "email,Email,email"
        ],
        "options": [
            {
                "key": "add_friend",
                "name": "Add friend",
                "default": False,
                "tooltip": "Show checkbox add LINE user as friend after logged in",
                "restrict_levels": 1
            }
        ]
    },
    {
        "name": "amazon",
        "version": ["v2"],
        "required_permissions": "profile:user_id",
        "basic_fields": [
            "name,Full Name,profile",
            "email,Email,profile"
        ],
        "advanced_fields": [
            "postal_code,Postal Code,postal_code"
        ],
        "options": [
            {
                "key": "amazon_pay",
                "name": "Associate with Amazon Pay",
                "default": False,
                "tooltip": "Indicates that your app use Login and Pay with Amazon",
                "restrict_levels": 2
            }
        ]
    },
    {
        "name": "yahoojp",
        "version": ["v2"],
        "required_permissions": "openid",
        "basic_fields": [
            "name,Full Name,profile",
            "given_name,First Name,profile",
            "family_name,Last Name,profile",
            "gender,Gender,profile",
            "zoneinfo,Zone Info,profile",
            "locale,Locale,profile",
            "nickname,Nick Name,profile",
            "birth_date,Birth Date,profile",
            "picture,Picture URL,profile"
        ],
        "advanced_fields": [
            "email,Email,email",
            "email_verified,Email Verified,email",
            "address,Address,address"
        ]
    },
    {
        "name": "facebook",
        "version": ["v3.1", "v3.2"],
        "required_permissions": "public_profile",
        "basic_fields": [
            "first_name,First Name,public_profile",
            "last_name, Last Name,public_profile",
            "middle_name,Middle Name,public_profile",
            "name,Full Name,public_profile",
            "picture,Picture URL,public_profile",
            "email,Email,email"
        ],
        "advanced_fields": [
            "age_range,Age Range,user_age_range",
            "birthday,Birthday,user_birthday",
            "gender,Gender,user_gender",
            "hometown,Hometown,user_hometown",
            "likes,User Likes,user_likes",
            "location,Location,user_location"
        ],
        "options": []
    },
    {
        "name": "twitter",
        "version": ["v1.1"],
        "required_permissions": "",
        "basic_fields": [
            "name,Name,",
            "screen_name,Screen Name,",
            "location,Location,",
            "url,Personal URL,",
            "description,Description,",
            "created_at,Created At,",
            "lang,Languages,",
            "profile_background_image_url_https,Background Image URL,",
            "profile_banner_url,Banner Image URL,",
            "profile_image_url_https, Image URL,",
            "verified,Verified,",
            "statuses_count,Statuses Count,",
            "followers_count,Followers Count,",
            "friends_count,Friends Count,",
            "listed_count,Listed Count,",
            "favourites_count,Favourites Count,"
        ],
        "advanced_fields": [
            "email,Email,"
        ],
        "options": []
    },
    {
        "name": "google",
        "version": ["v1"],
        "required_permissions": "openid|email",
        "basic_fields": [
            "emailAddresses,Email,email",
            "names,Name,profile",
            "locales,Locale,profile",
            "nicknames,Nickname,profile",
            "coverPhotos,Cover Photo URL,profile",
            "photos,Photo URL,profile",
            "genders,Gender,profile"
        ],
        "advanced_fields": [
            "phoneNumbers,Phone Number,https://www.googleapis.com/auth/user.phonenumbers.read",
            "addresses,Address,https://www.googleapis.com/auth/user.addresses.read",
            "birthdays,Birthday,https://www.googleapis.com/auth/user.birthday.read",
            "ageRanges,Age Range,https://www.googleapis.com/auth/plus.login"
        ]
    }
]


def convert_fields(fields):
    converted = []
    for field in fields:
        parts = field.split(',')
        converted.append({
            'key': parts[0],
            'name': parts[1],
            'permission': up.quote_plus(parts[2])
        })
    return converted


def init_providers(conn, cursor):
    data = []
    for provider in providers:
        for version in provider['version']:
            tup = (
                provider['name'],
                version,
                provider['required_permissions'],
                json.dumps(convert_fields(provider['basic_fields'])),
                json.dumps(convert_fields(provider['advanced_fields'])),
                json.dumps(provider.get('options', []))
            )
            data.append(tup)
    cursor.execute("TRUNCATE providers")
    cursor.executemany("""
        INSERT INTO providers (name, version, required_permissions, basic_fields, advanced_fields, options) 
        VALUES (%s, %s, %s, %s, %s, %s)""", data)

    conn.commit()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    db = MySQLdb.connect(
        db=os.getenv('DATABASE_NAME', 'easylogin'),
        user=os.getenv('DATABASE_USER', 'root'),
        passwd=os.getenv('DATABASE_PASSWORD', 'root'),
        host=os.getenv('DATABASE_HOST', 'localhost'),   # Or an IP Address that your DB is hosted on
        port=os.getenv('DATABASE_PORT', '3306')
    )
    cursor = db.cursor()
    init_providers(db, cursor)
    db.close()
