from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
import time

# def get_page_source(url):
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--window-size=1920x1080")
#     driver = webdriver.Chrome(options=chrome_options,
#                               executable_path='nowg_parser/chromedriver')
#     driver.get(url)
#     time.sleep(2)
#     a = driver.find_elements_by_css_selector('div.right')
#     print(11111111111, a)


def get_html(url):
    user_agent = UserAgent().chrome
    r = requests.get(url, headers={'User-Agent': user_agent})
    if r.ok:
        return r.text
    print(r.status_code)


def strip_parentheses(string):
    if string[0] == '[':
        return string[1:-1]
    return string


def find_weather_info(soup):
    tags = soup.find_all('div', class_='row')
    return [tag.text for tag in tags if 'Weather' in tag.text][0]


def get_score(value):
    if value == '':
        return 0
    return value.split('-')


def data_cast(team, scorred, missed, count):
    prefix = '{}_last{}m'.format(team, count)
    return {prefix+'_score_goals': scorred['goals'],
            prefix+'_score_corners': scorred['corners'],
            prefix+'_missed_goals': missed['goals'],
            prefix+'_missed_corners': missed['corners']}


def get_score_missed_stat(trs, team, type_):
    scorred = {'goals': 0, 'corners': 0}
    missed = {'goals': 0, 'corners': 0}
    result_stat = {}
    events_count = 0
    for tr in trs[4:]:
        try:
            tds = tr.select('td')
            table_home_team = tds[2].text
            final_score = get_score(tds[3].text)
            corner_score = get_score(tds[5].text)
            if team == table_home_team:
                scorred['goals'] += int(final_score[0])
                scorred['corners'] += int(corner_score[0])
                missed['goals'] += int(final_score[1])
                missed['corners'] += int(corner_score[1])
                events_count += 1
            else:
                scorred['goals'] += int(final_score[1])
                scorred['corners'] += int(corner_score[1])
                missed['goals'] += int(final_score[0])
                missed['corners'] += int(corner_score[0])
                events_count += 1
        except Exception:
            continue

        if events_count == 5:
            data = data_cast(team, scorred, missed, 5)
            result_stat.update(data)

        if events_count == 10:
            data = data_cast(team, scorred, missed, 10)
            result_stat.update(data)

    data = data_cast(team, scorred, missed, events_count)
    result_stat.update(data)
    return result_stat


def get_common_stat(trs, team):
    result_data = {}
    for tr in trs[3:6]:
        tds = tr.select('td')
        title = tds[0].text
        result_data[team+'_'+title+'_match'] = int(tds[1].text)
        result_data[team+'_'+title+'_win'] = int(tds[2].text)
        result_data[team+'_'+title+'_draw'] = int(tds[3].text)
        result_data[team+'_'+title+'_lose'] = int(tds[4].text)
        result_data[team+'_'+title+'_odds%'] = float(tds[5].text[:-1])
        result_data[team+'_'+title+'_over'] = int(tds[7].text)
        result_data[team+'_'+title+'_over%'] = float(tds[8].text[:-1])
        result_data[team+'_'+title+'_under'] = int(tds[9].text)
        result_data[team+'_'+title+'_under%'] = float(tds[10].text[:-1])
    return result_data


def get_stat(html):
    soup = BeautifulSoup(html, 'lxml')
    champ_title = strip_parentheses(
        soup.find('span', class_='LName').find('a').text)
    weather = find_weather_info(soup).split('Weather:')[1]
    teams_titles = [
        [a.text for a in soup.select('span.sclassName a')][0],
        [a.text for a in soup.select('span.sclassName a')][1]]
    final_result = [int(div.text)for div in soup.select('div.score')]
    total_score = sum(final_result)
    first_half_result = soup.find('span', title="Score 1st Half").text
    second_half_result = soup.find('span', title="Score 2nd Half").text

    data = {'champ_title': champ_title,
            'weather': weather,
            'home': teams_titles[0],
            'away': teams_titles[1],
            'result': '{}-{}'.format(final_result[0], final_result[1]),
            'total_score': total_score,
            'first_half': first_half_result,
            'second_half': second_half_result}

    h2h_stat = get_score_missed_stat(
        soup.select('table#table_v3 tr'), teams_titles[0], 'head2head')
    home_prev_stat = get_score_missed_stat(
        soup.select('table#table_v1 tr'), teams_titles[0], 'home_prev')
    away_prev_stat = get_score_missed_stat(
        soup.select('table#table_v2 tr'), teams_titles[1], 'away_prev')
    date_box = soup.select('tbody table tr td table.date_box tr')
    home_box, away_box = date_box[:7], date_box[7:14]
    home_common_stat = get_common_stat(home_box, teams_titles[0])
    away_common_stat = get_common_stat(away_box, teams_titles[0])
    data.update(h2h_stat)
    data.update(home_prev_stat)
    data.update(away_prev_stat)
    data.update(home_common_stat)
    data.update(away_common_stat)

    return data


new_type = 'http://www.nowgoal.group/analysis/1763774.html'
old_type = 'http://data.nowgoal.group/analysis/987471.html'
from_new_to_old = 'http://data.nowgoal.group/analysis/1426148.html'

print(get_stat(get_html(old_type)))
# get_main_stat(get_html(old_type))

# get_main_stat(get_html(new_type))
# get_main_stat(get_html(old_type))


# def get_score_missed_stat(trs, team, type_):
#     scorred = {'goals': 0, 'corners': 0}
#     missed = {'goals': 0, 'corners': 0}
#     for tr in trs[4:]:  # возможно 3й элемент уже сыгран
#         try:
#             tds = tr.select('td')
#             hh_home_team = tds[2].text
#             final_score = get_score(tds[3].text)
#             corner_score = get_score(tds[5].text)
#             print('hh - {} input - {}'.format(hh_home_team, team))
#             if team == hh_home_team:
#                 scorred['goal'] += int(final_score[0])
#                 scorred['corners'] += int(corner_score[0])
#                 missed['goal'] += int(final_score[1])
#                 missed['corners'] += int(corner_score[1])
#             else:
#                 scorred['goal'] += int(final_score[1])
#                 scorred['corners'] += int(corner_score[1])
#                 missed['goal'] += int(final_score[0])
#                 missed['corners'] += int(corner_score[0])
#         except Exception:
#             continue
# home_team_goals = home_away_score['goals'][0] + away_home_score['goals'][1]
# home_team_corners = home_away_score['corner'][0] + \
#     away_home_score['corner'][1]
# away_team_goals = home_away_score['goals'][1] + away_home_score['goals'][0]
# away_team_corners = home_away_score['corner'][1] + \
#     away_home_score['corner'][0]
# print(home_away_score)
# print(away_home_score)
# return {type_+'_total_home_goals': home_team_goals,
#         type_+'_total_home_corners': home_team_corners,
#         type_+'_total_away_goals': away_team_goals,
#         type_+'_total_away_corners': away_team_corners,
#         type_+'_curent_order_home_goals': home_away_score['goals'][0],
#         type_+'_curent_order_away_goals': home_away_score['goals'][1],
#         type_+'_curent_order_home_corners': home_away_score['corner'][0],
#         type_+'_curent_order_away_corners': home_away_score['corner'][1]}
