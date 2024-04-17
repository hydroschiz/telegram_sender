import pickle


def get_groups():
    groups = []
    with open("data/groups.txt", encoding="utf-8") as groups_file:
        line = groups_file.readline().strip()
        while line:
            groups.append(line)
            line = groups_file.readline().strip()

    return groups


def get_keywords():
    keywords = set()
    with open("data/keywords.txt", encoding="utf-8") as keywords_file:
        line = keywords_file.readline().strip().lower()
        while line:
            keywords.add(line)
            line = keywords_file.readline().strip().lower()

    return keywords


def save_admin_panel(panel):
    with open("data/admin_panel.pickle", "wb") as f:
        pickle.dump(panel, f)


def load_admin_panel():
    with open("data/admin_panel.pickle", "rb") as f:
        panel = pickle.load(f)
    return panel
