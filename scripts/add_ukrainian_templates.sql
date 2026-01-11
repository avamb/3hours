-- Insert Ukrainian main templates (informal - ти)
INSERT INTO question_templates (template_text, language_code, formal, category, is_active) VALUES
('Привіт, {name}! Що хорошого сталося сьогодні?', 'uk', false, 'main', true),
('{name}, розкажи, що порадувало тебе за останні години?', 'uk', false, 'main', true),
('Гей, {name}! Поділися чимось хорошим зі свого дня', 'uk', false, 'main', true),
('{name}, за що ти вдячний сьогодні?', 'uk', false, 'main', true),
('Який момент сьогодні змусив тебе посміхнутися, {name}?', 'uk', false, 'main', true);

-- Ukrainian main templates (formal - ви)
INSERT INTO question_templates (template_text, language_code, formal, category, is_active) VALUES
('Вітаю, {name}! Що хорошого сталося у Вас сьогодні?', 'uk', true, 'main', true),
('{name}, розкажіть, що порадувало Вас за останні години?', 'uk', true, 'main', true),
('{name}, поділіться чимось хорошим з Вашого дня', 'uk', true, 'main', true),
('{name}, за що Ви вдячні сьогодні?', 'uk', true, 'main', true),
('Який момент сьогодні змусив Вас посміхнутися, {name}?', 'uk', true, 'main', true);

-- Ukrainian follow_up templates (informal)
INSERT INTO question_templates (template_text, language_code, formal, category, is_active) VALUES
('А що ще хорошого було, {name}?', 'uk', false, 'follow_up', true),
('Розкажи детальніше, {name}!', 'uk', false, 'follow_up', true),
('Це чудово! Що ще порадувало?', 'uk', false, 'follow_up', true);

-- Ukrainian follow_up templates (formal)
INSERT INTO question_templates (template_text, language_code, formal, category, is_active) VALUES
('А що ще хорошого було, {name}?', 'uk', true, 'follow_up', true),
('Розкажіть детальніше, {name}!', 'uk', true, 'follow_up', true),
('Це чудово! Що ще Вас порадувало?', 'uk', true, 'follow_up', true);

-- Ukrainian return_inactive templates (informal)
INSERT INTO question_templates (template_text, language_code, formal, category, is_active) VALUES
('{name}, ми сумували! Що хорошого сталося за цей час?', 'uk', false, 'return_inactive', true),
('Привіт, {name}! Давно не спілкувалися. Поділися чимось хорошим!', 'uk', false, 'return_inactive', true);

-- Ukrainian return_inactive templates (formal)
INSERT INTO question_templates (template_text, language_code, formal, category, is_active) VALUES
('{name}, ми сумували! Що хорошого сталося за цей час?', 'uk', true, 'return_inactive', true),
('Вітаю, {name}! Давно не спілкувалися. Поділіться чимось хорошим!', 'uk', true, 'return_inactive', true);
