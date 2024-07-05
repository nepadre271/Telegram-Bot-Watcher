SELECT
    params->'extra'->'movie_name' as "Название фильма",
    params->'extra'->'year' as "Год выпуска",
    params->'extra'->'type' as "Тип",
    params->'extra'->'season' as "Сезон",
    params->'extra'->'seria' as "Серия",
    params->'extra'->'movie_id',
    timestamp
FROM user_actions
WHERE name = 'Movie: process upload' AND params->'extra' IS NOT NULL