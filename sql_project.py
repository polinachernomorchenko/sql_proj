import streamlit as st
import sqlite3
import pandas as pd

con = sqlite3.connect(r'mak_base.db')
cur = con.cursor()


def id_player_by_name(player_name):
    q = """SELECT id_player FROM players WHERE name_player=?"""

    res = pd.read_sql_query(q, params=[player_name], con=con)
    if not res.empty:
        return res.values[0][0]
    else:
        return None


def id_team_by_name(team_name):
    q = """SELECT id_team FROM teams WHERE name_team=?"""

    res = pd.read_sql_query(q, params=[team_name], con=con)
    if not res.empty:
        return res.values[0][0]
    else:
        return None


def get_tournament_id_from_name(tournament_name):
    q = """SELECT id_tournament FROM tournaments WHERE name_tournament=?"""
    res = pd.read_sql_query(q, params=[tournament_name], con=con)
    if not res.empty:
        return res.values[0][0]
    else:
        return None


def get_core_teams_by_players_name(player_name):
    q = """
        SELECT core_members.id_team, name_team, season
        FROM core_members 
        INNER JOIN teams ON (core_members.id_team=teams.id_team)
        WHERE core_members.id_player=(SELECT id_player
                                       FROM players
                                       WHERE name_player = ?)
        ORDER BY -season 
        """
    res = pd.read_sql_query(q, params=[player_name], con=con)
    return res


def get_tournaments_fom_players_name(player_name):
    q = """
        SELECT tournaments_members.id_tournament, name_team, name_tournament, num_answers, questions_number, day
        FROM tournaments_results, tournaments_members
        inner join teams on (teams.id_team=tournaments_members.id_team)
        inner join tournaments on (tournaments.id_tournament=tournaments_members.id_tournament)
        WHERE tournaments_members.id_player = (SELECT id_player
                           FROM players
                           WHERE name_player = ?)
        AND tournaments_results.id_team = tournaments_members.id_team 
        AND tournaments_results.id_tournament = tournaments_members.id_tournament
        ORDER BY -day
        """
    res = pd.read_sql_query(q, params = [player_name], con=con)
    return res


def player_data(player_name):
    n = id_player_by_name(player_name)
    if n:
        st.title(player_name)
        st.write(f'**id игрока: {n}**')
        st.write('**В базовых составах:**')
        st.write(get_core_teams_by_players_name(player_name))
        st.write('**Участие в турнирах**')
        st.write(get_tournaments_fom_players_name(player_name))
    else:
        st.write('**Нет результатов по вашему запросу**')


def get_core_members_by_team_name(team_name):
    q = """
        SELECT players.id_player, name_player, name_players_flag, season 
        FROM core_members, players, players_flags 
        WHERE core_members.id_team = (SELECT id_team
                                      FROM teams
                                      WHERE teams.name_team = ?)
        and core_members.id_player=players.id_player
        and core_members.id_flag=players_flags.id_players_flag
        """

    res = pd.read_sql_query(q, params=[team_name], con=con)
    return res


def get_tournaments_from_team_name(team_name):
    q = """
        SELECT tournaments_results.id_tournament, name_tournament, num_answers, questions_number, day
        FROM tournaments_results, tournaments
        WHERE id_team = (SELECT id_team
                         FROM teams
                         WHERE teams.name_team = ?)
        AND tournaments_results.id_tournament = tournaments.id_tournament
        """
    res = pd.read_sql_query(q, params = [team_name], con=con)
    return res


def get_sum_tournaments_from_team_name(team_name):
    q = """
        SELECT  COUNT(tournaments_results.id_tournament)
        FROM tournaments_results, tournaments
        WHERE id_team = (SELECT id_team
                         FROM teams
                         WHERE teams.name_team = ?)
        AND tournaments_results.id_tournament = tournaments.id_tournament
        """
    res = pd.read_sql_query(q, params=[team_name], con=con).values[0][0]
    return res


def get_sum_ans_from_team_name(team_name):
    q = """
        SELECT  SUM(num_answers)
        FROM tournaments_results, tournaments
        WHERE id_team = (SELECT id_team
                         FROM teams
                         WHERE teams.name_team = ?)
        AND tournaments_results.id_tournament = tournaments.id_tournament
        """
    res = pd.read_sql_query(q, params=[team_name], con=con).values[0][0]
    return res


def team_names_history(team_name):
    q = """
        SELECT name_team
        FROM teams_names_history
        WHERE id_team = (SELECT id_team
                         FROM teams
                         WHERE teams.name_team = ?)
    """
    res = pd.read_sql_query(q, params=[team_name], con=con)
    return res


def team_data(team_name):
    n = id_team_by_name(team_name)
    if n:
        st.subheader(team_name)
        st.write(f'**id команды: {n}**')
        st.write('**Базовые составы:**')
        st.write(get_core_members_by_team_name(team_name))
        st.write('**Участие в турнирах**')
        st.write(get_tournaments_from_team_name(team_name))
        st.write(f'Всего взятых вопросов: {get_sum_ans_from_team_name(team_name)}')
        st.write(f'Всего турниров: {get_sum_tournaments_from_team_name(team_name)}')
        st.write(f'**История названий:**')
        st.write(team_names_history(team_name))
    else:
        st.write('**Нет результатов по вашему запросу**')


def get_teams_from_tournament_name(tournament_name):
    q = """
        SELECT name_team, num_answers 
        FROM tournaments_results INNER JOIN teams ON (teams.id_team = tournaments_results.id_team)
        WHERE tournaments_results.id_tournament=(SELECT id_tournament
                                                FROM tournaments 
                                                WHERE tournaments.name_tournament = ?)
        ORDER BY -num_answers
        """

    res = pd.read_sql_query(q, params=[tournament_name], con=con)
    res.insert(0, column='place', value=pd.Series([[i] for i in range(1, len(res)+1)]))
    return res


def get_sum_teams_from_tournament_name(tournament_name):
    q = """
        SELECT COUNT(name_team) 
        FROM tournaments_results INNER JOIN teams ON (teams.id_team = tournaments_results.id_team)
        WHERE tournaments_results.id_tournament=(SELECT id_tournament
                                                FROM tournaments 
                                                WHERE tournaments.name_tournament = ?)
        ORDER BY -num_answers
        """

    res = pd.read_sql_query(q, params=[tournament_name], con=con).values[0][0]
    return res


def tournament_data(tournament_name):
    n = get_tournament_id_from_name(tournament_name)
    if n:
        st.title(tournament_name, )
        st.write(f'id турнира: {n}')
        st.write(f'Всего команд: {get_sum_teams_from_tournament_name(tournament_name)}')
        st.write(get_teams_from_tournament_name(tournament_name))
    else:
        st.write('**Нет результатов по вашему запросу**')


def upd_name_player(name, p_id):
    q = """
        UPDATE players
        SET name_player = ?
        WHERE id_player = ?
    """
    cur.execute(q, (name, p_id))
    con.commit()

    return "Данные успешно обновлены"


def upd_name_team(name, p_id):
    q = """
        UPDATE teams
        SET name_team = ?
        WHERE id_team = ?
    """
    cur.execute(q, (name, p_id))
    con.commit()

    return "Данные успешно обновлены"


def upd_name_tournament(name, p_id):

    q = """
        UPDATE tournaments
        SET name_tournament = ?
        WHERE id_tournament = ?
    """
    cur.execute(q, (name, p_id))
    con.commit()

    return "Данные успешно обновлены"


def del_smth(p_id, selector):
    if selector == 'Команда':
        tablename = 'teams'
        column = 'id_team'
    elif selector == 'Игрок':
        tablename = 'players'
        column = 'id_player'
    else:
        tablename = 'tournaments'
        column = 'id_tournament'

    q = 'DELETE FROM ' + tablename + ' WHERE ' + column + ' = ?'
    cur.execute(q, (p_id,))
    con.commit()

    return "Данные успешно удалены"


# def update_core_members(df, con, cur):
#     id_pl = int(df['id_player'].tolist()[0])
#     id_tm = int(df['id_team'].tolist()[0])
#     # nm_pl = df['name_player'].tolist()[0]
#     id_pf = int(df['id_players_flag'].tolist()[0])
#     ssn = df['season'].tolist()[0]
#
#     q = """
#         UPDATE core_members
#         SET id_player = ?,
#             id_team = ?,
#             id_flag = ?,
#             season = ?
#     """
#     cur.execute(q, (id_pl, id_tm, id_pf, ssn))
#     con.commit()
#
#     return 'Данные успешно добавлены'


c_query, c_choice = st.columns([4, 1])
choice = c_choice.selectbox(label='Вывести данные', options=['Игрок', 'Команда', 'Турнир'])
query = c_query.text_input('Введите запрос:')

c_id_upd, c_name_upd, c_choice_upd = st.columns([1, 3, 1])
choice_upd = c_choice_upd.selectbox(label='Изменить имя', options=['Игрок', 'Команда', 'Турнир'])
query_id_upd = c_id_upd.text_input('Введитe id:')
query_name_upd = c_name_upd.text_input('Введите новое имя:')


c_id_del, c_choice_del = st.columns([4, 1])
choice_del = c_choice_del.selectbox(label='Удалить', options=['Игрок', 'Команда', 'Турнир'])
query_id_del = c_id_del.text_input('Введите id:')


if query_id_del:
    st.write(del_smth(query_id_del, choice_del))


if query:
    if choice == 'Игрок':
        player_data(query)
    elif choice == 'Команда':
        team_data(query)
    elif choice == 'Турнир':
        tournament_data(query)


if query_name_upd and query_id_upd:
    if choice_upd == 'Игрок':
        st.write(upd_name_player(query_name_upd, query_id_upd))
    elif choice_upd == 'Команда':
        st.write(upd_name_team(query_name_upd, query_id_upd))
    elif choice_upd == 'Турнир':
        st.write(upd_name_tournament(query_name_upd, query_id_upd))



# c_query2, c_choice2 = st.columns([4, 1])
# choice2 = c_choice2.selectbox(label='Добавить данные', options=['Игрок', 'Базовый состав', 'Участие в турнире', 'Турнир'])
#
# uploaded_file = c_query2.file_uploader('Данные в формате .csv')
# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     if choice2 == 'Базовый состав':
#         st.write(update_core_members(df, con, cur))
