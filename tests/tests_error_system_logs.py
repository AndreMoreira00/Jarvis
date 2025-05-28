import unittest
import asyncio
from app.error.error_system_logs import errorSystemLog

class TestErrorSystemLog(unittest.TestCase):
  
  async def testLog(self):
    await self.assertEqual(errorSystemLog("Olá"), None)

if __name__ == '__main__':
  asyncio.run(unittest.main())