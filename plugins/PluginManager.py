import inspect
from plugins.Plugin import Plugin
from plugins.MailPlugin import MailPlugin


def call_all_plugins(data):
    for cls in Plugin.__subclasses__():
        plugin = cls.__call__()
        plugin.run(data)