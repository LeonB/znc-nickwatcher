import znc
import re

class nickwatcher(znc.Module):
    description = "Watches your nicks and places messages in a separate buffer"
    # module_types = [znc.CModInfo.NetworkModule, znc.CModInfo.UserModule]
    pattern = '(%s)([^a-zA-Z0-9]+|$)'

    def __init__(self):
        super(nickwatcher, self).__init__()
        self.nicks = []
        self.regex = None

    # def GetWebMenuTitle(self):
    #     return "Nick watcher"

    def OnLoad(self, args, message):
        self.nicks  = self.get_nicks() # get initial nicks
        self.regex = self.compile_pattern() # get regex based on initial nicks

        # self.PutModule("dir(self): %s" % dir(self))
        # self.PutModule("dir(znc): %s" % dir(znc))
        # self.PutModule("dir(znc.CBuffer): %s" % dir(znc.CBuffer))
        # self.PutModule("dir(self.GetNetwork()): %s" % dir(self.GetNetwork()))
        # self.PutModule("self.GetNetwork().IsUserAttached(): %s" % )

        return znc.CONTINUE

    def OnNick(self, old_nick, new_nick):
        self.nicks = self.get_nicks()
        self.regex = self.compile_pattern()

        return znc.CONTINUE

    def OnChanMsg(self, nick, channel, message):
        # self.PutModule("message: %s" % message.s)

        # Search for my nicks
        match = self.regex.search(message.s)
        # don't know why, but sometimes `if match:` is true even though
        # `match` doesn't contain anything...
        if match and match.group(0):
            self.match(channel, nick, message)

        return znc.CONTINUE

    def get_nicks(self):
        network = self.GetNetwork()
        return [
            network.GetNick(),
            network.GetAltNick(),
            network.GetCurNick()
        ]

    def compile_pattern(self):
        # Escape regex character in nicks
        escaped_nicks = map(lambda x: re.escape(x), self.nicks)

        # Make the pattern
        pattern = self.pattern % '|'.join(escaped_nicks)
        # self.PutModule('pattern: %s' % pattern)
        return re.compile(pattern)

    def match(self, channel, nick, message):
        self.PutModule("regex.pattern: %s" % self.regex.pattern)
        self.PutModule("self.nicks: %s" % self.nicks)

        msg = "<%(nick)s:%(channel)s> %(message)s" % {'nick': nick, 'channel': channel, 'message': message.s}
        if self.GetNetwork().IsUserAttached():
            self.PutModule(msg)
        else:
            channel.GetBuffer().AddLine(":*nickwatcher!nickwatcher@znc.in PRIVMSG {target} :{text}", msg)
