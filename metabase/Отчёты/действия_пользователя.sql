SELECT
    *
FROM user_actions
WHERE user_id = {{user_id}}::bigint
ORDER BY timestamp DESC