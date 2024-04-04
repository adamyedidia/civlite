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
            for unit in tech_template.unlocks_units:
                assert unit not in found_units, f"Tech {tech_template.name} unlocks unit {unit.name} which is already unlocked by another tech"
                found_units.add(unit)
                assert unit.prereq == tech_template, f"Unit {unit.name} is unlocked by tech {unit.prereq} but should be unlocked by {tech_template.name}"

        for unit in UNITS.all():
            assert unit in [UNITS.WARRIOR, UNITS.SLINGER] or unit in found_units, f"Unit {unit.name} is not unlocked by any tech"

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
                    try:
                        unit = UNITS.by_name(unit_name)
                    except KeyError:
                        raise ValueError(f"Civ {civ_template.name} has an ability which specifies a unit {unit_name} which does not exist")



       

