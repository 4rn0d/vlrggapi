import re

import requests
from bs4 import BeautifulSoup

import utils.utils as res
from utils.utils import headers


class Vlr:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
        }

    def get_soup(self, URL):
        response = requests.get(URL, headers=self.headers)

        html, status_code = response.text, response.status_code
        return BeautifulSoup(html, "lxml"), status_code

    def vlr_recent(self):
        URL = "https://www.vlr.gg/news"

        soup, status = self.get_soup(URL)

        articles = soup.body.find_all(
            "a", class_="wf-module-item"
        )

        result = []
        for article in articles:
            # Titles of articles
            title = article.find(
                "div",
                attrs={"style": "font-weight: 700; font-size: 15px; line-height: 1.3;"},
            ).text.strip()

            # get descriptions of articles
            desc = article.find(
                "div",
                attrs={
                    "style": " font-size: 13px; padding: 5px 0; padding-bottom: 6px; line-height: 1.4;"
                },
            ).text.strip()

            date_and_author = article.find("div", class_="ge-text-light").text.strip()
            date, by_author = map(lambda s: s.strip(), date_and_author[1:].split("\u2022"))

            # get url_path of articles
            url = article["href"]

            result.append(
                {
                    "title": title,
                    "description": desc,
                    "date": date,
                    "author": by_author[3:],
                    "url_path": url,
                }
            )

        data = {
            "data": {
                "status": status,
                "segments": result
            }
        }

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data

    @staticmethod
    def vlr_rankings(region):
        URL = "https://www.vlr.gg/rankings/" + res.region[str(region)]
        html = requests.get(URL, headers=headers)
        soup = BeautifulSoup(html.content, "lxml")
        status = html.status_code

        base = soup.find(class_=re.compile("mod-scroll"))
        containers = base.find_all(class_="rank-item")

        result = []
        for container in containers:
            # column 1
            rank = container.find(class_=re.compile("rank-item-rank-num")).text.strip()

            # column 2 - team
            team_container = container.find("div", {"class": "ge-text"}).text.strip()
            team = re.sub(re.compile(r'\s+'), '', team_container)
            team = team.split("#")[0]

            # column 2 - logo
            logo_container = container.find(class_=re.compile("rank-item-team"))
            img = logo_container.find("img")
            logo = "https:" + img["src"]

            # column 2 - ctry
            country = container.find(class_=re.compile("rank-item-team-country")).text.strip()

            result.append(
                {
                    "rank": rank,
                    "team": team,
                    "country": country,
                    "logo": logo,
                }
            )

        data = {"status": status, "data": result}

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data

    @staticmethod
    def vlr_score():
        URL = "https://www.vlr.gg/matches/results"
        html = requests.get(URL, headers=headers)
        soup = BeautifulSoup(html.content, "lxml")
        status = html.status_code

        base = soup.find(id="wrapper")

        vlr_module = base.find_all(
            "a",
            {"class": "wf-module-item"},
        )

        result = []
        for module in vlr_module:
            # link to match info
            url_path = module["href"]

            # Match completed time
            eta_container = module.find("div", {"class": "match-item-eta"})
            eta = (
                      eta_container.find("div", {"class": "ml-eta mod-completed"})
                          .get_text()
                          .strip()
                  ) + " ago"

            # round of tounranment
            round_container = module.find("div", {"class": "match-item-event text-of"})
            round = (
                round_container.find(
                    "div", {"class": "match-item-event-series text-of"}
                )
                    .get_text()
                    .strip()
            )
            round = round.replace("\u2013", "-")

            # tournament name
            tourney = (
                module.find("div", {"class": "match-item-event text-of"})
                    .get_text()
                    .strip()
            )
            tourney = tourney.replace("\t", " ")
            tourney = tourney.strip().split("\n")[1]
            tourney = tourney.strip()

            # tournament icon
            tourney_icon = module.find("img")["src"]
            tourney_icon = f"https:{tourney_icon}"

            # flags
            flags_container = module.findAll("div", {"class": "text-of"})
            flag1 = flags_container[0].span.get("class")[1]
            flag1 = flag1.replace("-", " ")
            flag1 = "flag_" + flag1.strip().split(" ")[1]

            flag2 = flags_container[1].span.get("class")[1]
            flag2 = flag2.replace("-", " ")
            flag2 = "flag_" + flag2.strip().split(" ")[1]

            # match items
            match_container = (
                module.find("div", {"class": "match-item-vs"}).get_text().strip()
            )

            match_array = match_container.replace("\t", " ").replace("\n", " ")
            match_array = match_array.strip().split(
                "                                  "
            )
            # 1st item in match_array is first team
            team1 = match_array[0]
            # 2nd item in match_array is first team score
            score1 = match_array[1]
            # 3rd item in match_array is second team                            ")[1]
            team2 = match_array[2].strip()
            # 4th item in match_array is second team score
            score2 = match_array[-1]

            result.append(
                {
                    "team1": team1,
                    "team2": team2,
                    "score1": score1,
                    "score2": score2,
                    "flag1": flag1,
                    "flag2": flag2,
                    "time_completed": eta,
                    "round_info": round,
                    "tournament_name": tourney,
                    "match_page": url_path,
                    "tournament_icon": tourney_icon,
                }
            )
        segments = {"status": status, "segments": result}

        data = {"data": segments}

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data

    @staticmethod
    def vlr_stats(region: str, timespan: int):
        URL = f"https://www.vlr.gg/stats/?event_group_id=all&event_id=all&region={region}&country=all&min_rounds=200" \
              f"&min_rating=1550&agent=all&map_id=all&timespan={timespan}d"

        html = requests.get(URL, headers=headers)
        soup = BeautifulSoup(html.content, "lxml")
        status = html.status_code

        tbody = soup.find("tbody")
        containers = tbody.find_all("tr")

        result = []
        for container in containers:
            # name of player
            player_container = container.find("td", {"class": "mod-player mod-a"})
            player = player_container.a.div.text.replace("\n", " ").strip()
            player = player.split(" ")[0]

            # org name for player
            org_container = container.find("td", {"class": "mod-player mod-a"})
            org = org_container.a.div.text.replace("\n", " ").strip()
            org = org.split(" ")[-1]

            # stats for player
            stats_container = container.findAll("td", {"class": "mod-color-sq"})
            acs = stats_container[0].div.text.strip()
            kd = stats_container[1].div.text.strip()
            adr = stats_container[3].div.text.strip()
            kpr = stats_container[4].div.text.strip()
            apr = stats_container[5].div.text.strip()
            fkpr = stats_container[6].div.text.strip()
            fdpr = stats_container[7].div.text.strip()
            hs = stats_container[8].div.text.strip()
            cl = stats_container[9].div.text.strip()

            result.append(
                {
                    "player": player,
                    "org": org,
                    "average_combat_score": acs,
                    "kill_deaths": kd,
                    "average_damage_per_round": adr,
                    "kills_per_round": kpr,
                    "assists_per_round": apr,
                    "first_kills_per_round": fkpr,
                    "first_deaths_per_round": fdpr,
                    "headshot_percentage": hs,
                    "clutch_success_percentage": cl,
                }
            )
        segments = {"status": status, "segments": result}

        data = {"data": segments}

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data

    @staticmethod
    def vlr_upcoming():
        URL = "https://www.vlr.gg/matches"
        html = requests.get(URL, headers=headers)
        soup = BeautifulSoup(html.content, "lxml")
        status = html.status_code

        base = soup.find(id="wrapper")

        vlr_module = base.find_all(
            "a",
            {"class": "wf-module-item"},
        )

        result = []
        for module in vlr_module:
            # link to match info
            url_path = module["href"]

            # Match completed time
            eta_container = module.find("div", {"class": "match-item-eta"})
            eta = "TBD"
            eta_time = eta_container.find("div", {"class": "ml-eta"})
            if eta_time is not None:
                eta = (
                          eta_time
                              .get_text()
                              .strip()
                      ) + " from now"

            # round of tournament
            round_container = module.find("div", {"class": "match-item-event text-of"})
            round = (
                round_container.find(
                    "div", {"class": "match-item-event-series text-of"}
                )
                    .get_text()
                    .strip()
            )
            round = round.replace("\u2013", "-")

            # tournament name
            tourney = (
                module.find("div", {"class": "match-item-event text-of"})
                    .get_text()
                    .strip()
            )
            tourney = tourney.replace("\t", " ")
            tourney = tourney.strip().split("\n")[1]
            tourney = tourney.strip()

            # tournament icon
            tourney_icon = module.find("img")["src"]
            tourney_icon = f"https:{tourney_icon}"

            # flags
            flags_container = module.findAll("div", {"class": "text-of"})
            flag1 = flags_container[0].span.get("class")[1]
            flag1 = flag1.replace("-", " ")
            flag1 = "flag_" + flag1.strip().split(" ")[1]

            flag2 = flags_container[1].span.get("class")[1]
            flag2 = flag2.replace("-", " ")
            flag2 = "flag_" + flag2.strip().split(" ")[1]

            # match items
            match_container = (
                module.find("div", {"class": "match-item-vs"}).get_text().strip()
            )

            match_array = match_container.replace("\t", " ").replace("\n", " ")
            match_array = match_array.strip().split(
                "                                  "
            )
            team1 = "TBD"
            team2 = "TBD"
            if match_array is not None and len(match_array) > 1:
                team1 = match_array[0]
                team2 = match_array[2].strip()
            result.append(
                {
                    "team1": team1,
                    "team2": team2,
                    "flag1": flag1,
                    "flag2": flag2,
                    "time_until_match": eta,
                    "round_info": round,
                    "tournament_name": tourney,
                    "match_page": url_path,
                    "tournament_icon": tourney_icon,
                }
            )
        segments = {"status": status, "segments": result}

        data = {"data": segments}

        if status != 200:
            raise Exception("API response: {}".format(status))
        return data


if __name__ == '__main__':
    print(Vlr.vlr_rankings("na"))
