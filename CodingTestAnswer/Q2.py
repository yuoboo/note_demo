

"""
The number of goals achieved by two football teams in matches in a league is given in the form of two lists.
For each match of team B, compute the total number of matches of team A
    where team A has scored less than or equal to the number of goals scored by team B in that match.
Example:
    teamA = [1, 2, 3]
    teamB = [2, 4]

Team A has played three matches and has scored teamA = [1, 2, 3] goals in each match respectively.
Team B has played two matches and has scored teamB = [2, 4] goals in each match respectively.
For 2 goals scored by team B in its first match, team A has 2 matches with scores 1 and 2.
For 4 goals scored by team B in its second match, team A has 3 matches with scores 1, 2 and 3. Hence, the answer is [2, 3].
"""


def total_nums(team_a: list, team_b: list) -> list:
    """
    思路： 遍历team_b, 取b中的值统计team_a中小于或等于该值的个数
    """
    res = []
    for i in team_b:
        nums = filter(lambda x: x <= i, team_a)
        res.append(len(list(nums)))

    return res


if __name__ == '__main__':
    # python3.7.4环境运行

    # 特殊情况： 数组长度为 1 或者 2
    input_team_a = [1, 2, 3]
    input_team_b = [2, 4]
    output = total_nums(input_team_a, input_team_b)
    print(f"output: {output}")

    input_team_a = [1, 2, 3, 5]
    input_team_b = [0, 4, 1]
    output = total_nums(input_team_a, input_team_b)
    print(f"output: {output}")
