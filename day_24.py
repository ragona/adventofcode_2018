from dataclasses import dataclass, field
from collections import deque
from util import number_grabber
import re
import unittest


@dataclass
class Group:

    size: int
    base_hp: int
    initiative: int
    damage: int
    army_name: str
    units: list = field(default_factory=list, repr=False)
    weaknesses: set = field(default_factory=set)
    immunities: set = field(default_factory=set)
    damage_type: str = None
    boost: int = 0

    def __hash__(self):
        return hash(id(self))

    @classmethod
    def group_from_string(cls, string, army, boost=0):
        """
        Performs unholy acts to parse the input string.
        """
        weaknesses = set()
        immunities = set()
        result = re.findall(r'weak to [a-z, ]+', string)
        if result:
            weaknesses = set(result[0][len('weak to '):].split(", "))
        result = re.findall(r'immune to [a-z, ]+', string)
        if result:
            immunities = set(result[0][len('immune to '):].split(", "))

        size, base_hp, damage, initiative = number_grabber(string)
        units = [base_hp for _ in range(size)]
        attack_type = re.findall(r'\w+ damage', string)[0].split()[0]

        return cls(size, base_hp, initiative, damage, army, units, weaknesses, immunities, attack_type, boost)

    @property
    def effective_power(self):
        return (self.damage + self.boost) * len(self.units)

    @property
    def alive(self):
        return sum(self.units) > 0

    def potential_damage(self, attacker):
        if not self.alive or not attacker.alive:
            raise Exception()

        if attacker.damage_type in self.immunities:
            return 0
        elif attacker.damage_type in self.weaknesses:
            return attacker.effective_power * 2
        return attacker.effective_power

    def take_damage(self, attacker):
        total = self.potential_damage(attacker)
        while total > 0:
            if len(self.units) > 0:
                unit = self.units[-1]
                if total >= unit:
                    self.units.pop()
                    total -= unit
                else:
                    # group survived; discard partial damage
                    break
            else:
                # group died
                break

    def attack(self, target):
        target.take_damage(attacker=self)

    def select_target(self, free_targets):
        potential_targets = sorted(
            free_targets,
            key=lambda g: (
                g.potential_damage(attacker=self),
                g.effective_power,
                g.initiative),
            reverse=True)

        if len(potential_targets) > 0:
            target = potential_targets[0]
            if target.potential_damage(attacker=self) > 0:
                return target

        return None


@dataclass
class Army:

    name: str
    groups: list = field(default_factory=list)

    @classmethod
    def armies_from_file(cls, filepath, boost=0):
        with open(filepath) as f:
            lines = deque([line.strip() for line in f.readlines()])

        immune_system = Army("immune_system")
        infection = Army("infection")
        army = immune_system

        for i in range(1, len(lines)):
            line = lines[i]
            try:
                if army is infection:
                    boost = 0
                army.groups.append(Group.group_from_string(line, army.name, boost))
            except:
                army = infection
                continue

        return immune_system, infection

    @property
    def dead(self):
        return sum([group.alive for group in self.groups]) <= 0

    @property
    def alive_groups(self):
        return {group for group in self.groups if group.alive}

    @property
    def total_units(self):
        return sum(len(group.units) for group in self.alive_groups)


class ImmuneFight:

    class FightOver(Exception):
        pass

    def __init__(self, immune_system, infection, immune_boost=0):
        self.immune_system = immune_system
        self.infection = infection

    def all_alive_groups(self):
        return [group for group in self.immune_system.groups + self.infection.groups if group.alive]

    def war(self):
        i = 0
        while True:
            try:
                all_units = self.total_units
                self.battle(i)
                if self.total_units == all_units:  # deadlock; no one is dying
                    break

            except ImmuneFight.FightOver:
                break
            i += 1

        if self.immune_system.dead:
            return self.infection
        elif self.infection.dead:
            return self.immune_system
        else:
            return None  # deadlock

    def battle(self, i):
        if self.immune_system.dead or self.infection.dead:
            raise ImmuneFight.FightOver()

        select_order = sorted(
            self.all_alive_groups(),
            key=lambda g: (g.effective_power, g.initiative),
            reverse=True)

        targets = dict()
        for group in select_order:

                army = self.enemy_army(group.army_name)
                free_targets = army.alive_groups - set(targets.values())

                if not free_targets:
                    continue

                target = group.select_target(free_targets)
                if target:
                    targets[group] = target

        attack_order = sorted(
            self.all_alive_groups(),
            key=lambda g: g.initiative,
            reverse=True)

        for group in attack_order:
            if group in targets:
                target = targets[group]
                if group.alive:
                    group.attack(target)
            else:
                continue

    def enemy_army(self, army_name):
        if army_name == 'infection':
            return self.immune_system
        else:
            return self.infection

    @property
    def total_units(self):
        return self.immune_system.total_units + self.infection.total_units


class TestImmuneFight(unittest.TestCase):

    def test_group_from_string(self):
        string_a = "6638 units each with 2292 hit points (weak to radiation) " \
                 "with an attack that does 3 cold damage at initiative 18"

        string_b = "3906 units each with 12319 hit points (immune to bludgeoning, " \
                   "cold, fire) with an attack that does 24 cold damage at initiative 14"

        a = Group.group_from_string(string_a, "immune")
        b = Group.group_from_string(string_b, "infection")

    def test_armies_from_file(self):
        immune, infection = Army.armies_from_file('input/day_24.txt')

    def test_sample_fight(self):
        immune, infection = Army.armies_from_file('input/day_24_test.txt')
        fight = ImmuneFight(immune, infection)
        victor = fight.war()

        assert victor.total_units == 5216

    def test_part_1(self):
        immune, infection = Army.armies_from_file('input/day_24.txt')
        fight = ImmuneFight(immune, infection)
        victor = fight.war()

        print("Part 1:", victor.total_units)

        assert victor.total_units == 22244

    def test_part_2(self):
        immune, infection = Army.armies_from_file('input/day_24.txt', boost=52)
        fight = ImmuneFight(immune, infection)

        victor = fight.war()

        if victor:
            print(victor.name, victor.total_units)
        else:
            print("tie")




"""
--- Day 24: Immune System Simulator 20XX ---
After a weird buzzing noise, you appear back at the man's cottage. He seems relieved to see his friend, but quickly
notices that the little reindeer caught some kind of cold while out exploring.

The portly man explains that this reindeer's immune system isn't similar to regular reindeer immune systems:

The immune system and the infection each have an army made up of several groups; each group consists of one or more
identical units. The armies repeatedly fight until only one army has units remaining.

Units within a group all have the same hit points (amount of damage a unit can take before it is destroyed), attack
damage (the amount of damage each unit deals), an attack type, an initiative (higher initiative units attack first and
win ties), and sometimes weaknesses or immunities. Here is an example group:

18 units each with 729 hit points (weak to fire; immune to cold, slashing)
 with an attack that does 8 radiation damage at initiative 10
Each group also has an effective power: the number of units in that group multiplied by their attack damage. The above
group has an effective power of 18 * 8 = 144. Groups never have zero or negative units; instead, the group is removed
from combat.

Each fight consists of two phases: target selection and attacking.

During the target selection phase, each group attempts to choose one target. In decreasing order of effective power,
groups choose their targets; in a tie, the group with the higher initiative chooses first. The attacking group chooses
to target the group in the enemy army to which it would deal the most damage (after accounting for weaknesses and
immunities, but not accounting for whether the defending group has enough units to actually receive all of that damage).

If an attacking group is considering two defending groups to which it would deal equal damage, it chooses to target the
defending group with the largest effective power; if there is still a tie, it chooses the defending group with the
highest initiative. If it cannot deal any defending groups damage, it does not choose a target. Defending groups can
only be chosen as a target by one attacking group.

At the end of the target selection phase, each group has selected zero or one groups to attack, and each group is being
attacked by zero or one groups.

During the attacking phase, each group deals damage to the target it selected, if any. Groups attack in decreasing order
of initiative, regardless of whether they are part of the infection or the immune system. (If a group contains no units,
it cannot attack.)

The damage an attacking group deals to a defending group depends on the attacking group's attack type and the defending
group's immunities and weaknesses. By default, an attacking group would deal damage equal to its effective power to the
defending group. However, if the defending group is immune to the attacking group's attack type, the defending group
instead takes no damage; if the defending group is weak to the attacking group's attack type, the defending group
instead takes double damage.

The defending group only loses whole units from damage; damage is always dealt in such a way that it kills the most
units possible, and any remaining damage to a unit that does not immediately kill it is ignored. For example, if a
defending group contains 10 units with 10 hit points each and receives 75 damage, it loses exactly 7 units and is left
with 3 units at full health.

After the fight is over, if both armies still contain units, a new fight begins; combat only ends once one army has lost
all of its units.

For example, consider the following armies:

Immune System:
17 units each with 5390 hit points (weak to radiation, bludgeoning) with
 an attack that does 4507 fire damage at initiative 2
989 units each with 1274 hit points (immune to fire; weak to bludgeoning,
 slashing) with an attack that does 25 slashing damage at initiative 3

Infection:
801 units each with 4706 hit points (weak to radiation) with an attack
 that does 116 bludgeoning damage at initiative 1
4485 units each with 2961 hit points (immune to radiation; weak to fire,
 cold) with an attack that does 12 slashing damage at initiative 4
If these armies were to enter combat, the following fights, including details during the target selection and attacking
phases, would take place:

Immune System:
Group 1 contains 17 units
Group 2 contains 989 units
Infection:
Group 1 contains 801 units
Group 2 contains 4485 units

Infection group 1 would deal defending group 1 185832 damage
Infection group 1 would deal defending group 2 185832 damage
Infection group 2 would deal defending group 2 107640 damage
Immune System group 1 would deal defending group 1 76619 damage
Immune System group 1 would deal defending group 2 153238 damage
Immune System group 2 would deal defending group 1 24725 damage

Infection group 2 attacks defending group 2, killing 84 units
Immune System group 2 attacks defending group 1, killing 4 units
Immune System group 1 attacks defending group 2, killing 51 units
Infection group 1 attacks defending group 1, killing 17 units
Immune System:
Group 2 contains 905 units
Infection:
Group 1 contains 797 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 184904 damage
Immune System group 2 would deal defending group 1 22625 damage
Immune System group 2 would deal defending group 2 22625 damage

Immune System group 2 attacks defending group 1, killing 4 units
Infection group 1 attacks defending group 2, killing 144 units
Immune System:
Group 2 contains 761 units
Infection:
Group 1 contains 793 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 183976 damage
Immune System group 2 would deal defending group 1 19025 damage
Immune System group 2 would deal defending group 2 19025 damage

Immune System group 2 attacks defending group 1, killing 4 units
Infection group 1 attacks defending group 2, killing 143 units
Immune System:
Group 2 contains 618 units
Infection:
Group 1 contains 789 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 183048 damage
Immune System group 2 would deal defending group 1 15450 damage
Immune System group 2 would deal defending group 2 15450 damage

Immune System group 2 attacks defending group 1, killing 3 units
Infection group 1 attacks defending group 2, killing 143 units
Immune System:
Group 2 contains 475 units
Infection:
Group 1 contains 786 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 182352 damage
Immune System group 2 would deal defending group 1 11875 damage
Immune System group 2 would deal defending group 2 11875 damage

Immune System group 2 attacks defending group 1, killing 2 units
Infection group 1 attacks defending group 2, killing 142 units
Immune System:
Group 2 contains 333 units
Infection:
Group 1 contains 784 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 181888 damage
Immune System group 2 would deal defending group 1 8325 damage
Immune System group 2 would deal defending group 2 8325 damage

Immune System group 2 attacks defending group 1, killing 1 unit
Infection group 1 attacks defending group 2, killing 142 units
Immune System:
Group 2 contains 191 units
Infection:
Group 1 contains 783 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 181656 damage
Immune System group 2 would deal defending group 1 4775 damage
Immune System group 2 would deal defending group 2 4775 damage

Immune System group 2 attacks defending group 1, killing 1 unit
Infection group 1 attacks defending group 2, killing 142 units
Immune System:
Group 2 contains 49 units
Infection:
Group 1 contains 782 units
Group 2 contains 4434 units

Infection group 1 would deal defending group 2 181424 damage
Immune System group 2 would deal defending group 1 1225 damage
Immune System group 2 would deal defending group 2 1225 damage

Immune System group 2 attacks defending group 1, killing 0 units
Infection group 1 attacks defending group 2, killing 49 units
Immune System:
No groups remain.
Infection:
Group 1 contains 782 units
Group 2 contains 4434 units
In the example above, the winning army ends up with 782 + 4434 = 5216 units.

You scan the reindeer's condition (your puzzle input); the white-bearded man looks nervous. As it stands now, how many
units would the winning army have?
"""

