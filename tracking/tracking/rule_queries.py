from datetime import datetime


async def notification_with_position(pool, rule_id, position_id):
    print('Notification with position rule id {}'.format(rule_id))
    async with pool.acquire() as connection:
        result = await connection.execute('INSERT INTO notifications_notification (rule_id, position_id, created_at) values ($1, $2, $3);',
        rule_id, position_id, datetime.utcnow())
        return result


async def notification_without_position(pool, rule_id):
    print('Notification rule id {}'.format(rule_id))
    async with pool.acquire() as connection:
        result = await connection.execute('INSERT INTO notifications_notification (rule_id, created_at) values ($1, $2);',
        rule_id, datetime.utcnow())
        return result


async def deactivate_rule(pool, rule_id):
    print('Deactivate rule id {}'.format(rule_id))
    async with pool.acquire() as connection:
        result = await connection.execute('UPDATE rules_rule SET is_active = FALSE WHERE id=$1;', rule_id)
        return result

