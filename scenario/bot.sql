insert into bot(name, token, active, date_created, date_updated)
values('@Simple2022MathBot', '5240278243:AAEMmtPTPaqnamswsUBLERaiOjDdYdXc9aA', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@nerd_puzzle_bot', '5519845269:AAFp391caUQ2GD75lTddQHLp0hw55xLu7DA', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@nerd_botmaker_bot', '5446289650:AAGg8fyO1NMzemA7w_l7jyMlZNSYbsD12Go', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@the_nerdest_bot', '5478696004:AAG5nqzDL_E_LM1uHh01FusWCiFFhcHV87g', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@DobrynyaBot', '970402676:AAHw22md9tXCjGGWlSRnTQ6KXfT82a9Kx10', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@netd_aimy_bot', '5468779098:AAHp05IQS8qaRr0Hx3TmRo4oqZOc6LcuFyE', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@nerd_sendpulse_bot', '5581648138:AAH9x9A7lmAv5mQE-NeI6b-1PzvXHanAoYY', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into bot(name, token, active, date_created, date_updated)
values('@mf_dump2019_bot', '867425126:AAFKNcFzk4e1S7uP4VkoYlEJoP7Z1del1r4', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


select * from main.bot;

delete from user;
update user set name  = ':message' where user_id = 123

select * from user;
delete from user where id=1;
insert into user(date_created, rel_bot, user_id) values (CURRENT_TIMESTAMP, 1, 1);

-- scenario
select * from scenario;
update scenario set db_target='user.email' where id=3;
select step, next_step, text, buttons, db_target, "sleep" from scenario where rel_bot=3 order by 1;
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 1, null,
'Приветствие… Прошу подтвердить согласие на обработку перс.данных',
'[[
  {"text": "да", "callback": "1", "next_step": 2},
  {"text": "нет", "callback": "0", "next_step": 999}
]]', null, null, null);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 2, 3, 'Введите ваше имя', null, 'user.name', null, null);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 3, 4, 'Введите ваш email', null, 'user.email ', null, null);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 4, 5, 'Выберите ваш род деятельности',
'[
  [{"text": "бухгалтер", "calback": "buch"}],
  [{"text": "руководитель", "calback": "rukovod"}],
  [{"text": "IT", "calback": "it"}],
  [{"text": "экономист", "calback": "ecomo"}],
  [{"text": "менеджер", "calback": "manager"}]
]', 'user.profession ', null, null);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 5, null,
'Рассказать о нас?',
'[[
  {"text": "да", "callback": "1", "next_step": 6},
  {"text": "нет", "callback": "0", "next_step": 100}
]]', null, null, null);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 6, 7, 'бла-бла-бла', null, null, null, 2);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 7, 8, 'ту-ту-ту', null, null, null, 2);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 8, 100, 'ла-ла-ла', null, null, null, 2);
insert into scenario(rel_bot, step, next_step, text, buttons, db_target, action, sleep)
values(3, 100, null, 'Предлагаю пройти квиз',
'[[
  {"text": "начать квиз", "callback": "quiz_start:quiz_ural", "next_step": 101},
  {"text": "пропустить", "callback": "skip_quiz", "next_step": 110}
]]', null, null, 2);
