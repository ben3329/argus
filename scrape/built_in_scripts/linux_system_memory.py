import asyncssh
from errors import ScriptError

class LinuxSystemMemory(object):
    _fields = ['used', 'utilization']
    _parameters = []
    def __init__(self, conn: asyncssh.SSHClientConnection, **kwargs):
        self.conn = conn
        self.data = {}

    @property
    def used(self):
        return self.data['used']

    @property
    def utilization(self):
        return round((self.data['used'] / self.data['total']) * 100, 2)

    async def get_data(self):
        if self.conn == None:
            raise ValueError("Connection is None.")
        output = await self.conn.run(f"free -k")
        if output.exit_status == 0:
            result = output.stdout
            lines = result.strip().split('\n')
            keys = lines[0].strip().split()
            values = lines[1].strip().split()[1:]
            for key, value in zip(keys, values):
                self.data[key] = int(value)
        else:
            raise ScriptError('LinuxSystemMemory', output.stderr)
