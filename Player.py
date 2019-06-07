from datetime import date, timedelta

from trueskill import Rating


class Player:

    def __init__(self, name, skill, player_counter):
        self.playerID = name.replace(" ", "") + str(player_counter)  # playerID is name plus their order in history
        self.name = name
        self.wins, self.losses, self.draws = 0, 0, 0
        self.games_played = self.wins + self.losses + self.draws
        self.skill = Rating(skill)
        self.ranking_score = round(self.skill.mu - (3 * self.skill.sigma), 2)
        self.mu_history, self.sigma_history = [], []
        self.skill_by_day = {}
        self.skill_by_game = [self.ranking_score]
        self.current_winning_streak, self.current_losing_streak = 0, 0
        self.longest_winning_streak, self.longest_losing_streak = 0, 0
        self.points_scored, self.points_lost = 0, 0
        if self.games_played == 0:
            self.average_ppg = 0
        else:
            self.average_ppg = round(self.points_scored / self.games_played, 2)
        if self.games_played == 0:
            self.average_point_margin = 0
        else:
            self.average_point_margin = round((self.points_scored - self.points_lost) / self.games_played, 2)

    def __str__(self):
        header = "Player Name: " + self.name + "  " + "ID: " + str(self.playerID)
        return f"\n{header} " \
            f"\nWin Rate: {self.get_win_percentage()} " \
            f"\nSkill Mean: {round(self.skill.mu, 2)} Skill Variance: {round(self.skill.sigma, 2)}" \
            f"\nRanking Score: {self.ranking_score}\n"

    def get_win_percentage(self):
        """
        Gets this players win percentage (wins / (wins + losses))
        :return: string representation of win rate, rounded to the hundredths place (ex. 34.52%)
        """
        if self.wins + self.losses == 0:
            return "No games played"
        else:
            return str(round(100*self.wins / (self.wins + self.losses), 2)) + "%"

    def update_skill(self, new_skill: Rating, timestamp: str):
        """
        Refreshes player skill rating and adds old skill rating to this player's skill_by_day
        :param new_skill: new Rating object
        :return: None
        """
        self.mu_history.append(self.skill.mu)
        self.sigma_history.append(self.skill.sigma)
        self.skill = Rating(new_skill)
        self.ranking_score = round(self.skill.mu - (3 * self.skill.sigma), 2)
        self.skill_by_game.append(self.ranking_score)
        timestamp = timestamp.split(' ')
        date = timestamp[0]
        date = date.split('/')
        if len(date[0]) == 1:
            date[0] = '0' + date[0]  # enforces that month is always two digits
        if len(date[1]) == 1:
            date[1] = '0' + date[1]  # enforces that day is always two digits
        self.skill_by_day[f'{date[2]}-{date[0]}-{date[1]}'] = self.ranking_score

    def update_stats_after_game(self, players_score: int, opponents_score: int):
        """
        updates player's stats like wins, average pts, etc.
        :param players_score: this player's score as int
        :param opponents_score: opponent's score as int
        :return:
        """
        self.games_played += 1
        self.points_scored += players_score
        self.points_lost += opponents_score
        self.average_ppg = round(self.points_scored / self.games_played, 2)
        self.average_point_margin = round((self.points_scored - self.points_lost) / self.games_played, 2)
        if players_score > opponents_score:
            self.wins += 1
            self.current_losing_streak = 0
            self.current_winning_streak += 1
            if self.current_winning_streak > self.longest_winning_streak:
                self.longest_winning_streak = self.current_winning_streak
        elif players_score < opponents_score:
            self.losses += 1
            self.current_winning_streak = 0
            self.current_losing_streak += 1
            if self.current_losing_streak > self.longest_losing_streak:
                self.longest_losing_streak = self.current_losing_streak
        else:
            self.draws += 1

    def reset_stats(self, new_skill: Rating):
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.games_played = 0
        self.skill = new_skill
        self.ranking_score = round(self.skill.mu - (3 * self.skill.sigma), 2)
        self.mu_history = []
        self.sigma_history = []
        self.skill_by_day = {}
        self.skill_by_game = [self.ranking_score]
        self.current_winning_streak = 0
        self.current_losing_streak = 0
        self.longest_winning_streak = 0
        self.longest_losing_streak = 0
        self.points_scored = 0
        self.points_lost = 0
        self.average_ppg = 0
        self.average_point_margin = 0

    def get_skill_on_day(self, skill_date: str):
        """
        returns a player's skill on a certain date
        :param skill_date: must be a string in the form 'YYYY-MM-DD'
        :return: float that's player's skill
        """
        if self.games_played == 0:
            return 0.00

        if skill_date in self.skill_by_day:
            return self.skill_by_day[skill_date]

        last_skill_date = skill_date
        while last_skill_date not in self.skill_by_day:
            if last_skill_date == '2018-01-01':
                return 0.00
            split = last_skill_date.split('-')
            # convert to date object so we can minus one day
            last_skill_date = date(int(split[0]), int(split[1]), int(split[2])) - timedelta(1)
            last_skill_date = last_skill_date.strftime('%Y-%m-%d')
        return self.skill_by_day[last_skill_date]
