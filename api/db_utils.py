import aiosqlite
import sqlite3
from datetime import datetime
from contextlib import asynccontextmanager
from typing import AsyncGenerator

DB_NAME = "rag_app.db"

# Connection pool
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(DB_NAME) as conn:
        yield conn

@asynccontextmanager
async def get_db_context():
    async with aiosqlite.connect(DB_NAME) as conn:
        try:
            yield conn
        finally:
            await conn.close()

# Initialize tables
def init_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS application_logs
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_query TEXT,
            gpt_response TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS document_store
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        ''')
        conn.commit()
    finally:
        conn.close()

async def get_all_documents():
    async with get_db_context() as conn:
        async with conn.execute(
            '''SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC'''
        ) as cursor:
            documents = await cursor.fetchall()
            columns = ['id', 'filename', 'upload_timestamp']
            return [dict(zip(columns, doc)) for doc in documents]

async def insert_application_logs(session_id, user_query, gpt_response, model):
    async with get_db_context() as conn:
        await conn.execute(
            '''INSERT INTO application_logs (session_id, user_query, gpt_response, model) 
               VALUES (?, ?, ?, ?)''', 
            (session_id, user_query, gpt_response, model)
        )
        await conn.commit()

async def get_chat_history(session_id):
    async with get_db_context() as conn:
        async with conn.execute('''
            SELECT user_query, gpt_response FROM application_logs
            WHERE session_id = ? ORDER BY created_at''', 
            (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            messages = []
            for row in rows:
                messages.extend([
                    {"role": "human", "content": row[0]},
                    {"role": "ai", "content": row[1]}
                ])
            return messages

async def insert_document_record(filename):
    async with get_db_context() as conn:
        cursor = await conn.execute(
            '''INSERT INTO document_store (filename) VALUES (?)''', 
            (filename,)
        )
        file_id = cursor.lastrowid
        await conn.commit()
        return file_id

async def delete_document_record(file_id):
    async with get_db_context() as conn:
        await conn.execute(
            '''DELETE FROM document_store WHERE id = ?''', 
            (file_id,)
        )
        await conn.commit()
        return True

init_db()