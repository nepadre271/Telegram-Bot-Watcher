SELECT
    users.id,
    users.username,
    users.join as "Дата создания",
    users.join_to_group as "Дата подписки на группу",
    users.subscribe_expire as "Подписка действительна до",
    users.views_left as "Просмотров осталось",
    users.invite_from as "Приглашен",
    actions.last_action as "Последнее действие",
    uref."Количество рефералов"
FROM public.users
LEFT JOIN (
    SELECT user_id, last(timestamp, timestamp) as last_action
    FROM public.user_actions
    GROUP BY user_id
) as actions
ON actions.user_id = users.id
LEFT JOIN (
    SELECT invite_from, COUNT(invite_from) as "Количество рефералов"
    FROM public.users
    WHERE invite_from IS NOT NULL
    GROUP BY invite_from
) as uref
ON users.id = uref.invite_from
ORDER BY users.join DESC;