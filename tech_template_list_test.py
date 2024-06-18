import pytest

from tech_templates_list import TECHS
from unit_templates_list import UNITS
from civ_templates_list import CIVS
from building_templates_list import BUILDINGS
from unit_template import UnitTag
from city_names import CITY_NAMES_BY_CIV

class TestConsistency:
    def test_units_tech_consistency(self):
        found_units = set()
        for tech_template in TECHS.all():
            for unit in tech_template.unlocks_units:
                assert unit not in found_units, f"Tech {tech_template.name} unlocks unit {unit.name} which is already unlocked by another tech"
                found_units.add(unit)
                assert unit.prereq == tech_template, f"Unit {unit.name} is unlocked by tech {unit.prereq} but should be unlocked by {tech_template.name}"

        for unit in UNITS.all():
            assert unit in [UNITS.WARRIOR, UNITS.SLINGER] or unit in found_units or unit.has_tag(UnitTag.WONDROUS), f"Unit {unit.name} is not unlocked by any tech"

    def test_bldgs_tech_consistency(self):
        found_bldgs = set()
        for tech_template in TECHS.all():
            for bldg in tech_template.unlocks_buildings:
                assert bldg not in found_bldgs, f"Tech {tech_template.name} unlocks building {bldg} which is already unlocked by another tech"
                found_bldgs.add(bldg)
                assert bldg.prereq == tech_template, f"Building {bldg} is unlocked by tech {bldg.prereq} but should be unlocked by {tech_template.name}"

        for bldg in BUILDINGS.all():
            assert bldg in found_bldgs, f"Building {bldg} is not unlocked by any tech. It think it should be unlocked by {bldg.prereq}"

    def test_civ_special_units_consistency(self):
        for civ_template in CIVS.all():
            for ability in civ_template.abilities:
                if ability.name == 'IncreasedStrengthForUnit':
                    numbers = ability.numbers
                    unit_name = numbers[0]
                    try:
                        unit = UNITS.by_name(unit_name)
                    except KeyError:
                        raise ValueError(f"Civ {civ_template.name} has an ability which specifies a unit {unit_name} which does not exist")


    def test_city_names_exist_for_every_civ(self):
        for civ_template in CIVS.all():
            assert civ_template.name in CITY_NAMES_BY_CIV, f"Civ {civ_template.name} does not have cities"


