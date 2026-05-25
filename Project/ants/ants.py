"""Ants Vs. SomeBees."""

from __future__ import annotations  # This makes the type annotations work
import random
from ucb import main, interact, trace
from collections import OrderedDict

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive = False

    def __init__(self, name: str, exit: Place | None = None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name = name
        self.exit = exit
        self.bees: list[Bee] = []
        self.ant: Ant | None = None
        self.entrance: Place | None = None
        # Phase 1: Add an entrance to the exit
        # BEGIN Problem 2
        "*** YOUR CODE HERE ***"
        if self.exit != None:
            self.exit.entrance = self
        # END Problem 2

    def add_insect(self, insect: Insect):
        """Asks the insect to add itself to this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect: Insect):
        """Asks the insect to remove itself from this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.remove_from(self)

    def __str__(self) -> str:
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    next_id = 0  # Every insect gets a unique id number
    damage = 0
    # ADD CLASS ATTRIBUTES HERE
    is_waterproof = False

    def __init__(self, health: int, place: Place | None = None):
        """Create an Insect with a health and a starting PLACE."""
        self.health = health
        self.full_health = health
        self.place = place

        # assign a unique ID to every insect
        self.id = Insect.next_id
        Insect.next_id += 1

    def reduce_health(self, damage_taken: float):
        """Reduce health by DAMAGE_TAKEN, and remove the insect from its place if it
        has no health remaining. Decorated in gui.py for GUI support.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= damage_taken
        if self.health <= 0:
            self.zero_health_callback()

            if self.place is not None:
                self.place.remove_insect(self)

    def action(self, gamestate: GameState):
        """The action performed each turn."""

    def zero_health_callback(self):
        """
        Called when health reaches 0 or below.
        Decorated in gui.py to support GUI
        """

    def add_to(self, place: Place):
        self.place = place

    def remove_from(self, place: Place):
        self.place = None

    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False  # Only implemented Ant classes should be instantiated
    food_cost = 0
    is_container = False
    blocks_path = True
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health: int = 1):
        super().__init__(health)
        self.is_doubled = False

    def can_contain(self, other: Ant) -> bool:
        return False

    def store_ant(self, ant: Ant):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, ant: Ant):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place: Place):
        if place.ant is None:
            place.ant = self
        else:
            # BEGIN Problem 8b
            """
            Q: When can a second Ant be added to a place that already contains an Ant?
            A: When exactly one of the Ant instances is a container and the
               container ant does not already contain another ant
            
            Q: If two Ants occupy the same Place, what is stored in that place's ant
               instance attribute?
            A: The Container Ant

            Q: Which Ant does a ContainerAnt guard?
            A: The Ant instance that is in the same place as itself
            """
            #Modify Ant.add_to to allow a container and its contained ant to occupy the same place according to the following rules:
            #1.ContainerAnt 先放置且内部是空的（can_contain返回true）
            #2.待被保护的Ant先放置，且后续放的ContainerAnt可以保护之前的Ant（can_contain返回true
            #   2.1:Important: If there are two Ants in a specific Place, the ant attribute of the Place instance should refer to the container ant, and the container ant should contain the non-container ant.
            #3.除了上述两种情况之外的情况抛出assert place.ant is None, 'Too many ants in {0}'.format(place)
            if (place.ant.is_container) and (place.ant.can_contain(self)):
                place.ant.store_ant(self)
            elif (not place.ant.is_container) and (self.can_contain(place.ant)):
                self.store_ant(place.ant)
                place.ant = self
            else:
                assert place.ant is None, 'Too many ants in {0}'.format(place)
            # END Problem 8b
        Insect.add_to(self, place)

    def remove_from(self, place: Place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def double(self):
        """Double this ants's damage, if it has not already been doubled."""
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        if not self.is_doubled:
            self.damage = self.damage * 2
            self.is_doubled = True
        # END Problem 12


class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    # my coding
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE

    def action(self, gamestate: GameState):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        "*** YOUR CODE HERE ***"
        gamestate.food += 1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    implemented = True
    damage = 1
    # my coding
    food_cost = 3
    lower_bound = 0.0
    upper_bound = float('inf')
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE

    def nearest_bee(self) -> Bee | None:
        """Return a random Bee from the nearest Place (excluding the Hive) that contains Bees and is reachable from
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        if not self.place:
            return None  # An Ant that is not in a Place has no nearest Bee
        # BEGIN Problem 3 and 4
        current_place = self.place
        place_distance = 0
        while (not current_place.is_hive):
            if (current_place.bees != []) and (self.lower_bound <= place_distance <= self.upper_bound):
                return random_bee(current_place.bees)
            current_place = current_place.entrance
            place_distance += 1
        return None

        # return random_bee(self.place.bees) # REPLACE THIS LINE
        # END Problem 3 and 4

    def throw_at(self, target: Bee | None):
        """Throw a leaf at the target Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate: GameState):
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())


def random_bee(bees: list[Bee]) -> Bee | None:
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), \
        "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

##############
# Extensions #
##############


class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    lower_bound = 0.0
    upper_bound = 3.0
    # BEGIN Problem 4
    implemented = True   # Change to True to view in the GUI
    # END Problem 4


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    lower_bound = 5.0
    upper_bound = float('inf')
    # BEGIN Problem 4
    implemented = True   # Change to True to view in the GUI
    # END Problem 4


class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented = True   # Change to True to view in the GUI
    # END Problem 5

    def __init__(self, health: int = 3):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)

    def reduce_health(self, damage_taken: float):
        """Reduce health by DAMAGE_TAKEN, and remove the FireAnt from its place if it
        has no health remaining.

        Make sure to reduce the health of each bee in the current place, and apply
        the additional damage if the fire ant dies.
        """
        # # BEGIN Problem 5
        # "*** YOUR CODE HERE ***"
        # #1.蜜蜂调用FireAnt(实例).reduce_health()方法对FireAnt(实例)造成伤害
        # #2.没死：对自身place上的所有蜜蜂造成反弹伤害
        # #3.死了：造成反弹伤害的同时造成自身damage = 3的自爆伤害

        # #先拷贝蜜蜂列表以防直接对源列表操作删除蜜蜂时无法遍历全部蜜蜂，边遍历边修改会容易出错
        # current_place_bees = list(self.place.bees)
        # # super().reduce_health(damage_taken)
        # Ant.reduce_health(self, damage_taken)
        # for bee in current_place_bees:
        #     bee.reduce_health(damage_taken)
        #     if self.place is None and bee.place is not None:
        #         bee.reduce_health(self.damage)
        # # END Problem 5

        # BEGIN Problem 5
        if self.place is None:
            return
        
        # 1. 拷贝当前格子的蜜蜂列表（非常好的一步！）
        current_place_bees = list(self.place.bees)
        
        # 2. 调用父类方法承受伤害
        super().reduce_health(damage_taken)
        
        # 3. 结算总伤害（基础反弹伤害 + 可能的自爆伤害）
        total_damage = damage_taken
        if self.health <= 0:  # 如果自己死了，加上额外自爆伤害 self.damage
            total_damage += self.damage
            
        # 4. 对所有蜜蜂一次性应用总伤害
        for bee in current_place_bees:
            bee.reduce_health(total_damage)
            
        # END Problem 5

# BEGIN Problem 6
# The WallAnt class
class WallAnt(Ant):
    """WallAnt does nothing each turn except having a large health value."""

    name = 'Wall'
    damage = 0
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True   # Change to True to view in the GUI
    def __init__(self, health: int = 4):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)
# END Problem 6

# BEGIN Problem 7
# The HungryAnt Class
class HungryAnt(Ant):
    """WallAnt does nothing each turn except having a large health value."""

    name = 'Hungry'
    damage = 0
    food_cost = 4
    chew_cooldown = 3
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True   # Change to True to view in the GUI
    def __init__(self, health: int = 1):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)
        self.cooldown = 0

    #吃掉自己位置上的蜜蜂，并冷却三回合（到第四回合才能吃）
    #1.自己的位置不为None
    #2.自己的位置上有蜜蜂时随便挑一个调用其reduce_health()方法
    #   2.1设置自己的cooldown为3
    #3.自己的位置上没蜜蜂时什么都不做
    #4.每回合cooldown减1直到0
    def action(self, gamestate: GameState):
        if self.place is None:
            return "HungryAnt 死掉了哦" #😆
        
        # 1. 优先结算冷却
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            # 2. 只有此时才去抓捕蜜蜂，节约性能
            eaten_bee = random_bee(self.place.bees)
            if eaten_bee is not None:
                # 3. 开吃，重置冷却
                eaten_bee.reduce_health(eaten_bee.health)
                self.cooldown = HungryAnt.chew_cooldown  # 这里也可以写 self.chew_cooldown 也可以
# END Problem 7


class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container = True

    def __init__(self, health: int):
        super().__init__(health)
        self.ant_contained = None

    def can_contain(self, other: Ant) -> bool:
        # BEGIN Problem 8a
        #Return True:
        #   1.This ContainerAnt does not already contain another ant.
        #   2.The other ant is not a container.
        "*** YOUR CODE HERE ***"
        if (self.ant_contained is None) and (not other.is_container):
            return True
        return False
        # END Problem 8a

    def store_ant(self, ant: Ant):
        # Implement the store_ant method so that it sets the ContainerAnt's ant_contained instance attribute to the ant argument passed in. 
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        self.ant_contained = ant
        # END Problem 8a

    def remove_ant(self, ant: Ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place: Place):
        # Special handling for container ants
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = self.ant_contained
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate: GameState):
        #This method will ensure that if our ContainerAnt currently contains an ant, ant_contained's action is performed.
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)
        # END Problem 8a


class ProtectorAnt(ContainerAnt):
    """ProtectorAnt provides protection to other Ants."""

    name = 'Protector'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 8c
    implemented = True   # Change to True to view in the GUI
    def __init__(self):
        super().__init__(2)
    # END Problem 8c

# BEGIN Problem 9
# The TankAnt class
class TankAnt(ContainerAnt):
    """ The TankAnt is a ContainerAnt that protects an ant in its place and also deals 1 damage to all Bees in its Place each turn. """

    name = 'Tank'
    damage = 1
    food_cost = 6
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True   # Change to True to view in the GUI
    def __init__(self, health: int = 2):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)
    def action(self, gamestate: GameState):
        if self.place is None:
            return "TankAnt 死掉了哦"
        #注意提前拷贝列表，以防出现莫名其妙的bug
        current_place_bees = list(self.place.bees)
        super().action(gamestate)
        for bee in current_place_bees:
            print("DEBUG:", bee.health)
            print("DEBUG: how many bees?", len(current_place_bees))
            bee.reduce_health(self.damage)
# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect: Insect):
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        "*** YOUR CODE HERE ***"
        super().add_insect(insect)
        if not insect.is_waterproof:
            insect.reduce_health(insect.health)
        # END Problem 10

# BEGIN Problem 11
# The ScubaThrower class
class ScubaThrower(ThrowerAnt):
    """ 
    Implement the ScubaThrower, which is a subclass of ThrowerAnt that is more costly and waterproof, but otherwise identical to its base class. 
    A ScubaThrower should not lose its health when placed in Water.
    """ 
    name = 'Scuba'
    food_cost = 6
    is_waterproof = True
    # OVERRIDE CLASS ATTRIBUTES HERE
    # Change to True to view in the GUI


# END Problem 11


class QueenAnt(ThrowerAnt):
    """
    QueenAnt boosts the damage of all ants behind her.
    In addition to the standard ThrowerAnt action, a QueenAnt doubles the damage of all the ants behind her in her tunnel each time she performs an action. 
    Note: The reflected damage of a FireAnt should not be doubled, only the extra damage it deals when its health is reduced to 0.
    """

    name = 'Queen'
    food_cost = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 12
    implemented = True   # Change to True to view in the GUI
    # END Problem 12

    def action(self, gamestate: GameState):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        # 1.通过place.exit向后遍历自己tunnel上的每一个place直到最后一个place.exit == None
        # 2.对于每一个place先判断该位置上是否有ant
        #   2.1若有，先将其self.damage加倍
        #   2.2再判断是否是container（即判断is_container == True）和其是否包含另一只ant，若为真self.ant_contained.damage加倍
        # 3.判断是否到tunnel最后
        super().action(gamestate)
        if self.place.exit is None:
            return
        current_place = self.place
        while(current_place.exit is not None):
            current_place = current_place.exit
            if current_place.ant is None:
                continue
            current_place.ant.double()
            if not current_place.ant.is_container:
                continue
            if current_place.ant.ant_contained is not None:
                current_place.ant.ant_contained.double()
            
        # END Problem 12

    def reduce_health(self, damage_taken: float):
        """Reduce health by DAMAGE_TAKEN, and if the QueenAnt has no health
        remaining, signal the end of the game.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        super().reduce_health(damage_taken)
        if self.health <= 0:
            ants_lose()
        # END Problem 12


################
# Extra Challenge #
################

class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""
    """
    SlowThrower throws sticky syrup at a bee, slowing it for 5 turns. 
    When a bee is slowed, it does its regular Bee action when gamestate.time is even, and takes no action (does not move or sting) otherwise. 
    If a bee is hit by syrup while it is already slowed, it is slowed for 5 turns starting from the most recent time it is hit by syrup. 
    That is, if a bee is hit by syrup, takes 2 turns, and is hit by syrup again, it will now be slowed for 5 turns after the second time it is hit by syrup. 
    So it will have been slowed for 7 turns total (not 10!).
    """
    """
    Important Restriction: You may not modify any code outside the SlowThrower class for this problem. 
    That means you may not modify the Bee.action method directly. Our tests will check for this.
    """
    """
    Hint: Take a look at SlowThrower's parent class, ThrowerAnt. 
    ThrowerAnt's action method calls throw_at, which is what you should be overriding in SlowThrower. 
    What is passed into the target parameter in SlowThrower's throw_at function and why? 
    What is target.action referring to?
    """
    """
    Implementation Hint: Assign target.action to a new function that conditionally calls Bee.action. 
    You can create and use an instance attribute to track how many more turns the bee will be slowed. 
    Once the slowing effect is over, Bee.action should be called every turn again.
    """
    name = 'Slow'
    food_cost = 6
    # BEGIN Problem EC 1
    implemented = True   # Change to True to view in the GUI
    damage = 0
    # END Problem EC 1

    def throw_at(self, target: Bee | None):
        if target is None:
            return
        target.reduce_health(self.damage)
        # 1. 在这里想办法记录 target 还需要被减速多少个回合（可以用 setattr 或者给 target 增加一个属性）
        # 比如：target.slow_turns = ??? 
        target.slow_turns = 5
        
        # 2. 伪造一个新的行动逻辑！（注意看它的参数！）
        def new_action(gamestate: GameState):
            # 破案了！这个函数实在未来引擎要求蜜蜂行动时被调用的,
            # 引擎会自动把 gamestate 传进来！
            # 就在这里，你可以愉快地访问 gamestate.time 啦：
            
            # 如果还有减速回合：
            #     如果是偶数回合：执行常规动作
            #     如果是奇数回合：什么都不做（发呆）
            #     记得减去一个减速回合哦！
            # 如果减速回合用完了：
            #     执行常规动作
            
            # 【重要提示】：执行常规动作时，按 Hint 说的,
            # 直接调用原本的类方法：Bee.action(target, gamestate)
            if target.slow_turns > 0:
                if gamestate.time % 2 == 0:
                    Bee.action(target, gamestate)
                target.slow_turns -= 1
            else:
                Bee.action(target, gamestate)
            
        # 3. 移花接木！把蜜蜂原本的 action 替换成你写的这个带有“减速毒药”的新函数
        target.action = new_action


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""
    """
    1.If the bee is already right next to the Hive and cannot go back further, it should not move. To check if a bee is next to the Hive, you might find the is_hive instance attribute of Place useful.
    2.Bees remain scared until they have tried to back away twice. So, the back away effect lasts two turns.
    3.Bees cannot try to back away if they are slowed and gamestate.time is odd. This would be a turn they're frozen by SlowThrower!
    4.Once a bee has been scared once, it can't be scared ever again.
    """
    """
    In order to complete the implementation of this ScaryThrower, you will need to set its class attributes appropriately and implement the scare method in Bee, which applies the scared status on a particular bee. 
    You may also have to edit some other methods of Bee such as action.
    """
    name = 'Scary'
    food_cost = 6
    # BEGIN Problem EC 2
    implemented = True   # Change to True to view in the GUI
    damage = 0
    # END Problem EC 2

    def throw_at(self, target: Bee | None):
        # BEGIN Problem EC 2
        if target is None:
            return
        target.reduce_health(self.damage)
        target.scare(2)



        # #判断是否受过惊吓，若有直接执行修改过的Bee.action(target, gamestate)，没有设self.scared_turns = 2
        # if not hasattr(target, "scared_turns"):
        #     target.scared_turns = 2

        # def new_action(gamestate: GameState):
        #     "*** YOUR CODE HERE ***"  
        #     #受惊吓还有惊吓回合且不靠着hive：
        #         #2.没有被减速，每回合倒退一格,即执行修改过的Bee.action(target, gamestate)
        #         #3.被减速且gamestate.time is even 每回合倒退一格,，执行修改过的Bee.action(target, gamestate)
        #         #4.被减速且gamestate.time is odd 停住，即发呆
        #         #6.惊吓回合减一
        #     #受惊吓还有惊吓回合且靠着hive：
        #         #停住，即发呆
        #         #6.惊吓回合减一
        #     #惊吓回合用完了:
        #         #5.执行修改过的Bee.action(target, gamestate)

        #     if target.scared_turns > 0:
        #         #target.scared_turns -= 1
        #         if hasattr(target, "slow_turns"):
        #             if ((target.slow_turns > 0) and (gamestate.time % 2 != 0)) or (target.place.entrance.is_hive):
        #                 return
        #     Bee.action(target, gamestate)
        # # 3. 移花接木！把蜜蜂原本的 action 替换成你写的这个带有“惊吓魔盒”的新函数
        # target.action = new_action

        # END Problem EC 2


class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name = 'Ninja'
    damage = 1
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    blocks_path = False
    # BEGIN Problem EC 3
    implemented = True   # Change to True to view in the GUI
    # END Problem EC 3

    def action(self, gamestate: GameState):
        # BEGIN Problem EC 3
        "*** YOUR CODE HERE ***"
        # 1. 拷贝当前格子的蜜蜂列表（非常好的一步！）
        current_place_bees = list(self.place.bees)
        # 2. 对所有在当前格子的蜜蜂造成伤害
        for bee in current_place_bees:
            bee.reduce_health(self.damage)
        # END Problem EC 3


class LaserAnt(ThrowerAnt):
    """ThrowerAnt that damages all Insects standing in its path."""
    """
    1.对自己位置（除了自己）和自己前面的所有的除了在Hive中的Insects造成伤害
    2.基础伤害值为2
    3.每经过一个place镭射的伤害-0.25
    4.每对一个Insect造成伤害镭射的威力立马-0.0625
    5.如果伤害值减小到小于等于0，那么镭射造成的伤害为0
    The exact order in which things are damaged within a turn does not matter.
    Important: If an insect's health is unaffected, its health should remain as a whole number (integer), as it was when the insect was initially created.
    """
    name = 'Laser'
    food_cost = 10
    # OVERRIDE CLASS ATTRIBUTES HERE
    ddamage = 2
    # BEGIN Problem EC 4
    implemented = True   # Change to True to view in the GUI
    # END Problem EC 4

    def __init__(self, health: int = 1):
        super().__init__(health)
        self.insects_shot = 0
        self.base_damage = self.ddamage

    def insects_in_front(self) -> dict[Insect, int]:
        ant_distance = {}
        distance = 0
        current_place = self.place

        while not current_place.is_hive:
            # 1. 处理该位置的蚂蚁
            target_ant = current_place.ant
            if target_ant is not None and target_ant is not self:
                ant_distance[target_ant] = distance
                # 如果是容器，还要检查里面有没有“别人”
                if target_ant.is_container and target_ant.ant_contained is not None:
                    # 只有当里面的蚂蚁不是 LaserAnt 自己时才加进去
                    if target_ant.ant_contained is not self:
                        ant_distance[target_ant.ant_contained] = distance
            
            # 2. 处理该位置的所有蜜蜂
            for bee in current_place.bees:
                ant_distance[bee] = distance

            # 3. 前进到下一个格子
            current_place = current_place.entrance
            distance += 1
        return ant_distance
        # END Problem EC 4

    def calculate_damage(self, distance: int) -> float:
        # 直接计算当前应该造成的伤害
        # 基础 2.0 - 距离损耗 - 之前射击过的损耗
        current_damage = 2.0 - (0.25 * distance) - (0.0625 * self.insects_shot)
        return max(0, current_damage) # 确保不为负数

    def action(self, gamestate: GameState):
        insects_and_distances = self.insects_in_front()
        print("Debug insects_and_distances is: ", insects_and_distances)
        LaserAnt.play_sound_effect() # laser beam sound effect
        for insect, distance in insects_and_distances.items():
            print("Debug insect is None? ", insect is None)
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1

    @classmethod
    def play_sound_effect(cls):
        """Play laser sound effect. Decorated in gui.py"""
        pass


########
# Bees #
########

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True


    def sting(self, ant: Ant):
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place: Place):
        """Move from the Bee's current Place to a new PLACE."""
        if self.place is not None:
            self.place.remove_insect(self)

        if place is not None:
            place.add_insect(self)

    def blocked(self) -> bool:
        """Return True if this Bee cannot advance to the next Place."""
        # Special handling for NinjaAnt
        # BEGIN Problem EC 3
        if self.place is None:
            return False
        if self.place.ant is None:
            return False
        return self.place.ant.blocks_path
        # END Problem EC 3

    def action(self, gamestate: GameState):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination = None
        # if hasattr(self,"scared_turns"):
        #     if (self.place and not self.scared_turns):
        #         destination = self.place.exit
        #     elif (self.place and self.scared_turns):
        #         destination = self.place.entrance
        #         self.scared_turns -= 1
        # else:
        
        if (self.place):
            #如果被恐惧了且不在奇数回合改变行进方向
            #在hive前即使被scare了也不能退后,只能发呆
            if ( hasattr(self, "scared_turns") and (self.scared_turns > 0) ):
                if self.place.entrance.is_hive:
                    self.scared_turns -= 1

                # elif ((gamestate.time % 2 == 0)):
                else:
                    destination = self.place.entrance
                    self.scared_turns -= 1
            else:
                destination = self.place.exit

        if self.blocked() and self.place and self.place.ant:
            self.sting(self.place.ant)
        elif self.health > 0 and destination is not None:
            self.move_to(destination)

    

    def add_to(self, place: Place):
        place.bees.append(self)
        super().add_to(place)

    def remove_from(self, place: Place):
        place.bees.remove(self)
        super().remove_from(place)

    def scare(self, length: int):
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
        """
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        #1.在hive前即使被scare了也不能退后,只能发呆
        #2.一只蜂一生只能被scare一次
        #3.恐惧效果维持两回合但要兼容减速效果，奇数回合不后退只发呆
        if hasattr(self, "scared_turns"):
            return
        self.scared_turns = length

        # END Problem EC 2


class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2


class Boss(Wasp):
    """The leader of the bees. Damage to the boss by any attack is capped.
    """
    name = 'Boss'
    damage_cap = 8

    def reduce_health(self, damage_taken: float):
        super().reduce_health(min(damage_taken, self.damage_cap))

    @classmethod
    def play_sound_effect(cls):
        "Play sound effect when boss arrives! Decorated in gui.py"
        pass


class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive = True

    def __init__(self, assault_plan: AssaultPlan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees: list[Bee] = []
        for bee in assault_plan.all_bees():
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance: None = None
        self.ant: None = None
        self.exit: Place | None = None

    def strategy(self, gamestate: GameState):
        exits = [p for p in gamestate.places.values() if p.entrance is self]

        for bee in self.assault_plan.get(gamestate.time, []):
            if Boss in bee.__class__.__mro__:
                Boss.play_sound_effect()
                GameState.display_notification('Boss Bee is Here!')
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)

###################
# Game Components #
###################

class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, beehive: Hive, ant_types: list, create_places, dimensions, food: int = 2):
        """Create an GameState for simulating a game.

        Arguments:
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time: int = 0
        self.food = food
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees: list = []
        self.configure(beehive, create_places)

    def configure(self, beehive: Hive, create_places):
        """Configure the places in the colony."""
        self.base: AntHomeBase = AntHomeBase('Ant Home Base')
        self.places: OrderedDict = OrderedDict()
        self.bee_entrances: list = []

        def register_place(place: Place, is_bee_entrance: bool):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place,
                      self.dimensions[0], self.dimensions[1])

    def ants_take_actions(self): # Ask ants to take actions
        for ant in self.ants:
            if ant.health > 0:
                ant.action(self)

    def bees_take_actions(self, num_bees: int) -> int: # Ask bees to take actions
        for bee in self.active_bees[:]:
            if bee.health > 0:
                bee.action(self)
            if bee.health <= 0:
                num_bees -= 1
                self.active_bees.remove(bee)
        if num_bees == 0: # Check if player won
            GameState.play_win_sound()
            raise AntsWinException()
        return num_bees

    def simulate(self):
        """Simulate an attack on the ant colony. This is called by the GUI to play the game."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self) # Bees invade from hive
                yield None # After yielding, players have time to place ants
                self.ants_take_actions()
                self.time += 1
                yield None # After yielding, wait for throw leaf animation to play, then ask bees to take action
                num_bees = self.bees_take_actions(num_bees)
        except AntsWinException:
            print('All bees are vanquished. You win!')
            yield True
        except AntsLoseException:
            print('The bees reached homebase or the queen ant queen has perished. Please try again :(')
            yield False

    def deploy_ant(self, place_name: str, ant_type_name: str) -> Ant | None:
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        ant_type = self.ant_types[ant_type_name]
        if ant_type.food_cost > self.food:
            message = 'Not enough food!'
            print(message)
            GameState.display_notification(message)
        else:
            ant: Ant = ant_type()
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name: str):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @staticmethod
    def display_notification(message):
        """Display a notification! Decorated in gui.py for GUI support"""
        pass

    @classmethod
    def play_win_sound(cls):
        """Play the sound effect when ants win! Decorated in gui.py"""
        pass

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen normally resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a AntsLoseException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()


def ants_lose():
    """Signal that Ants lose."""
    raise AntsLoseException()


def ant_types() -> list:
    """Return a list of all implemented Ant classes."""
    all_ant_types: list = []
    new_types: list = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


def bee_types() -> list:
    """Return a list of all implemented Bee classes."""
    all_bee_types: list = []
    new_types: list = [Bee]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_bee_types.extend(new_types)
    return all_bee_types


class GameOverException(Exception):
    """Base game over Exception."""
    pass


class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass


class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass


###########
# Layouts #
###########


def wet_layout(queen: AntHomeBase, register_place, tunnels: int = 3, length: int = 9, moat_frequency: int = 3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen: AntHomeBase, register_place, tunnels: int = 3, length: int = 9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """
    def add_wave(self, bee_type, bee_health: int, time: int, count: int) -> AssaultPlan:
        """Add a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    def all_bees(self) -> list:
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]