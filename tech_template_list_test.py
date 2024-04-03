import pytest

from tech_templates_list import TECHS
from unit_templates_list import UNITS
from civ_templates_list import CIVS
from building_templates_list import BUILDINGS
from tech_template import TechTemplate
from unit_template import UnitTemplate
from civ_template import CivTemplate
from building_template import BuildingTemplate

class TestConsistency:
    def test_tech_names_consistency(self):
        for tech_template in TECHS:
            assert tech_template.name == tech_template.value.name, f"key and name mismatch: {tech_template.value.name} != {tech_template.name}"

    def test_unit_names_consistency(self):
        for name, json in UNITS.items():
            unit_template = UnitTemplate.from_json(json)
            assert unit_template.name == name, f"key and name mismatch: {name} != {unit_template.name}"

    def test_civ_names_consistency(self):
        for name, json in CIVS.items():
            civ_template = CivTemplate.from_json(json)
            assert civ_template.name == name, f"key and name mismatch: {name} != {civ_template.name}"

    def test_building_name_consistency(self):
        for name, json in BUILDINGS.items():
            building_template = BuildingTemplate.from_json(json)
            assert building_template.name == name, f"key and name mismatch: {name} != {building_template.name}"

    def test_units_tech_consistency(self):
        found_units = set()
        for tech_template in TECHS.all():
            for unit_name in tech_template.unlocks_units:
                assert unit_name in UNITS, f"Tech {tech_template.name} unlocks unit {unit_name} which does not exist"
                assert unit_name not in found_units, f"Tech {tech_template.name} unlocks unit {unit_name} which is already unlocked by another tech"
                found_units.add(unit_name)
                assert UNITS[unit_name]['prereq'] == tech_template.name, f"Unit {unit_name} is unlocked by tech {UNITS[unit_name]['prereq']} but should be unlocked by {tech_template.name}"

        for unit_name in UNITS:
            assert unit_name in ["Scout", "Warrior", "Slinger"] or unit_name in found_units, f"Unit {unit_name} is not unlocked by any tech"

    def test_bldgs_tech_consistency(self):
        found_bldgs = set()
        for tech_template in TECHS.all():
            for bldg_name in tech_template.unlocks_buildings:
                assert bldg_name in BUILDINGS, f"Tech {tech_template.name} unlocks building {bldg_name} which does not exist"
                assert bldg_name not in found_bldgs, f"Tech {tech_template.name} unlocks building {bldg_name} which is already unlocked by another tech"
                found_bldgs.add(bldg_name)
                assert BUILDINGS[bldg_name]['prereq'] == tech_template.name, f"Building {bldg_name} is unlocked by tech {BUILDINGS[bldg_name]['prereq']} but should be unlocked by {tech_template.name}"

        for bldg_name in BUILDINGS:
            assert bldg_name in found_bldgs, f"Building {bldg_name} is not unlocked by any tech. It think it should be unlocked by {BUILDINGS[bldg_name].get('prereq')}"

    def test_civ_special_units_consistency(self):
        for name, json in CIVS.items():
            civ_template = CivTemplate.from_json(json)

            for ability in civ_template.abilities:
                if ability.name == 'IncreasedStrengthForUnit':
                    numbers = ability.numbers
                    unit_name = numbers[0]
                    assert unit_name in UNITS, f"Unit {unit_name} does not exist"


       

