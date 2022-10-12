from roleidentification import pull_data, get_roles

# Pull the data required to make role assignments
champion_roles = pull_data()

# You can pass in a list of champions to `get_roles`
champions = [122, 64, 69, 28, 201]  # ['Darius', 'Lee Sin', 'Cassiopeia', 'Draven', 'Braum']
roles = get_roles(champion_roles, champions)
print(roles)
# Output:
#{'TOP': 122, 'JUNGLE': 64, 'MIDDLE': 69, 'BOTTOM': 119, 'UTILITY': 201}