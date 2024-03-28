__all__ = ["Database", "UsersDB", "SessionDB", "ChatsDB"]

from mysql.connector import connect as testconnect
from mysql.connector.aio import connect
from json import loads, dump

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
    
    async def execGetLastRow(self, query, *args) -> None:

        cnx, cur = await self.get_cursor()

        await cur.execute(query, *args)

        await cnx.commit()

        row_id = cur.lastrowid

        await cur.close()
        await cnx.close()
        return row_id

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

class ChatsDB(Database):

    def __init__(self) -> None:
        super().__init__()

    async def get_user_chats(self, user_id: int):
        query: str = "SELECT id, messages, author_id, created_at FROM chats WHERE author_id = %s"
        data = await self.fetch(query, (user_id,))
        return data
    
    async def new_chat(self, user_id: int):
        query: str = "INSERT INTO chats(author_id) VALUES (%s)"
        chat_id = await self.execGetLastRow(query, (user_id,))
        return chat_id

    async def get_chat(self, chat_id: int):
        query: str = "SELECT id, messages, author_id, name, created_at FROM chats WHERE id = %s"
        data = await self.fetchone(query, (chat_id,))
        return data

    async def chat_delete(self, chat_id: int):
        query = "DELETE FROM chats WHERE id = %s"
        await self.execute(query, (chat_id,))

    async def update(self, chat_id: int, column: str, new_value):
        query = f"UPDATE chats SET {column} = %s WHERE id = %s"
        await self.execute(query, (new_value, chat_id))



if __name__ == "__main__":
    Database().test()