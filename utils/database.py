__all__ = ["Database", "UsersDB", "SessionDB"]

from mysql.connector import connect as testconnect
from mysql.connector.aio import connect

class Database():

    def __init__(self) -> None:
        self.database = "ai-chat-app"
        self.user = "root"
        self.password = "" 

    async def get_cursor(self):

        cnx = await connect(
            user = self.user,
            password = self.password,
            database = self.database
        )
        return cnx, await cnx.cursor()
    
    async def fetch(self, query, *args) -> int | bool | str | float:

        cnx, cur = await self.get_cursor()

        await cur.execute(query, *args)
        result = await cur.fetchall()

        await cur.close()
        await cnx.close()

        return result
    
    async def fetchone(self, query, *args) -> int | bool | str | float:

        cnx, cur = await self.get_cursor()

        await cur.execute(query, *args)
        result = await cur.fetchone()

        await cur.close()
        await cnx.close()

        return result 
    
    async def execute(self, query, *args) -> None:

        cnx, cur = await self.get_cursor()

        await cur.execute(query, *args)

        await cnx.commit()

        await cur.close()
        await cnx.close()

    def test(self) -> None:
        try:
            conn = testconnect(user = self.user, password = self.password, database=self.database)
            cur = conn.cursor()
            cur.execute("SELECT * from users")

            print(cur.fetchall())
        except Exception as e:
            print(e)

class UsersDB(Database): 

    def __init__(self) -> None:
        super().__init__()

    async def get(self, user_id: int) -> tuple | None:
        query: str = "SELECT id, name, password FROM users WHERE id = %s"
        data = await self.fetchone(query, (user_id,))
        return data
    
    async def get_by_name(self, user_name: str) -> tuple | None:
        query: str = "SELECT id, name, password FROM users WHERE name = %s"
        data = await self.fetchone(query, (user_name,))
        
        return data

class SessionDB(Database): 

    def __init__(self) -> None:
        super().__init__()

    async def get(self, token: str) -> tuple | None:
        query: str = "SELECT session_token, user_id FROM session WHERE session_token = %s"
        data = await self.fetchone(query, (token,))
        return data
    
    async def get_by_userid(self, user_id: int) -> tuple | None:
        query: str = "SELECT session_token, user_id FROM session WHERE user_id = %s"
        data = await self.fetchone(query, (user_id,))
        return data
    
    async def create(self, token: str, user_id: int) -> tuple | None: 
        query: str = "INSERT INTO session(session_token, user_id) VALUES (%s, %s)"
        await self.execute(query, (token, user_id))





if __name__ == "__main__":
    Database().test()