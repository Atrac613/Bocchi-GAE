USE_I18N = True

# Valid languages
LANGUAGES = (
    # 'en', 'zh_TW' match the directories in conf/locale/*
    ('en', _('English')),
    ('ja', _('Japanese')),
    # or ('zh-tw', _('Chinese')), # But the directory must still be conf/locale/zh_TW
    )# This is a default language

LANGUAGE_CODE = 'en'

UA_APPLICATION_KEY = ''
UA_APPLICATION_MASTER_SECRET = ''

UA_PROD_APPLICATION_KEY = ''
UA_PROD_APPLICATION_MASTER_SECRET = ''