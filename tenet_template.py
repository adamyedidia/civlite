class TenetTemplate:
    def __init__(self, name, description, advancement_level, quest_description=None):
        self.name = name
        self.description = description
        self.advancement_level = advancement_level
        self.quest_description = quest_description

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "advancement_level": self.advancement_level
        }