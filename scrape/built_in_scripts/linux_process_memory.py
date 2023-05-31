import asyncssh
from errors import ScriptError

class LinuxProcessMemory(object):
    _fields = ['vsz', 'rss']
    _parameters = ['pid']
    def __init__(self, conn: asyncssh.SSHClientConnection, pid:int ,**kwargs):
        self.conn = conn
        self.data = {}
        self.pid = pid

    @property
    def vsz(self):
        return self.data['vsz']

    @property
    def rss(self):
        return self.data['rss']

    async def get_data(self):
        if self.conn == None:
            raise ValueError("Connection is None.")
        output = await self.conn.run(f"ps -p {self.pid} -o vsz=,rss=")
        if output.exit_status == 0:
            result = output.stdout
            memory = result.strip().split()
            if len(memory) != 2:
                raise ScriptError('LinuxProcessMemory', f"Output is Invalid. {result}")
            self.data['vsz'] = int(memory[0])
            self.data['rss'] = int(memory[1])
        else:
            raise ScriptError('LinuxProcessMemory', output.stderr)
