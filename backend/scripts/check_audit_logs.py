import asyncio
from app.db.session import async_session
from sqlalchemy import text

async def check_audit_logs():
    async with async_session() as db:
        # Check recent audit logs
        result = await db.execute(text('SELECT id, user_id, action, resource_type, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 5'))
        logs = result.fetchall()
        print('Recent audit logs:')
        for log in logs:
            print(f'  ID: {log[0]} (type: {type(log[0]).__name__}), User: {log[1]}, Action: {log[2]}, Resource: {log[3]}')

        # Delete old UUID audit logs
        print('\nDeleting old UUID audit logs...')
        result = await db.execute(text("DELETE FROM audit_logs WHERE typeof(id) = 'text'"))
        await db.commit()
        print(f'Deleted {result.rowcount} old audit logs')

asyncio.run(check_audit_logs())
