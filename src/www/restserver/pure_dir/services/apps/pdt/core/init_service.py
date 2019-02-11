"""
    init_service.py
    ~~~~~~~~~~~~~

    Performs the cleanup for temporary files created

"""

import os
import gettext


def init_localization():
    locale_path = "/var/www/restserver/pure_dir/services/apps/pdt/locales/"
    os.system("msgfmt " + locale_path + "en_US/LC_MESSAGES/messages.po -o " +
              locale_path + "en_US/LC_MESSAGES/messages.mo")
    language = gettext.translation(
        'messages', localedir=locale_path, languages=['en_US'])
    language.install()


def init_service():
    init_localization()
