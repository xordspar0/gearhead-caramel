from pbge.plots import Plot, Adventure
from pbge.dialogue import Offer, ContextTag, Cue
from .. import teams, services, ghdialogue
from ..ghdialogue import context
import gears
import gharchitecture
import pbge
import plotutility
import ghwaypoints
import ghterrain
from . import GHNarrativeRequest, PLOT_LIST


class DZD_Wujung(Plot):
    LABEL = "DZD_HOME_BASE"

    # noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
    def custom_init(self, nart):
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team", allies=(team1,))
        myscene = gears.GearHeadScene(50, 50, "Wujung City", player_team=team1, civilian_team=team2,
                                      scale=gears.scale.HumanScale,
                                      attributes=(gears.personality.GreenZone, gears.tags.City))
        myscene.exploration_music = 'Doctor_Turtle_-_04_-_Lets_Just_Get_Through_Christmas.ogg'

        npc = gears.selector.random_character(50, local_tags=myscene.attributes)
        npc.place(myscene, team=team2)

        myscenegen = pbge.randmaps.CityGridGenerator(myscene, gharchitecture.HumanScaleGreenzone(),
                                                     road_terrain=ghterrain.Flagstone)

        self.register_scene(nart, myscene, myscenegen, ident="LOCALE")

        # myscene.contents.append(ghterrain.ScrapIronBuilding(waypoints={"DOOR":ghwaypoints.ScrapIronDoor(),"OTHER":ghwaypoints.RetroComputer()}))

        myroom = self.register_element("_ROOM", pbge.randmaps.rooms.FuzzyRoom(5, 5), dident="LOCALE")
        myent = self.register_element("ENTRANCE", ghwaypoints.Waypoint(anchor=pbge.randmaps.anchors.middle),
                                      dident="_ROOM")

        myroom2 = self.register_element("_ROOM2", pbge.randmaps.rooms.Room(3, 3, anchor=pbge.randmaps.anchors.west),
                                        dident="LOCALE")
        westgate = self.register_element("ADVENTURE_GATE", ghwaypoints.Exit(name="The West Gate",
                                                                            desc="You stand at the western city gate of Wujung. Beyond this point lies the dead zone.",
                                                                            anchor=pbge.randmaps.anchors.west,
                                                                            plot_locked=True), dident="_ROOM2")

        # Add the services.
        tplot = self.add_sub_plot(nart, "DZDHB_AlliedArmor")
        tplot = self.add_sub_plot(nart, "DZDHB_EliteEquipment")
        tplot = self.add_sub_plot(nart, "DZDHB_BlueFortress")

        return True


class AdventureSeed(Adventure):
    def __init__(self, camp, name, adv_type, adv_return, pstate=None, auto_set_rank=True):
        # adv_return is a (Destination,Entrance) tuple.
        super(AdventureSeed, self).__init__(name=name, world=None)
        self.pstate = pstate or pbge.plots.PlotState(adv=self,rank=camp.pc.renown)
        self.pstate.adv = self
        self.pstate.elements["ADVENTURE_RETURN"] = adv_return
        self.adv_type = adv_type
        self.auto_set_rank = auto_set_rank

    def __call__(self, camp):
        """

        :type camp: gears.GearHeadCampaign
        """
        if self.auto_set_rank:
            self.pstate.rank = camp.pc.renown
        nart = GHNarrativeRequest(camp, self.pstate, self.adv_type, PLOT_LIST)
        if nart.story:
            nart.build()
            camp.check_trigger("UPDATE")
        else:
            for e in nart.errors:
                print e


class DZD_BlueFortressHQ(Plot):
    LABEL = "DZDHB_BlueFortress"

    active = True
    scope = True

    def custom_init(self, nart):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Blue Fortress")},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "Blue Fortress L1", player_team=team1, civilian_team=team2,
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene, room1=building,
                                                    room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.TerranDefenseForce)

        self.adventure_seed = None

        return True

    def ADVENTURE_GATE_menu(self, camp, thingmenu):
        if self.adventure_seed:
            thingmenu.add_item(self.adventure_seed.name, self.adventure_seed)

    def register_adventure(self,camp):
        self.adventure_seed = AdventureSeed(camp,"Boring Adventure","DZD_COMBAT_MISSION",(self.elements["LOCALE"],self.elements["ADVENTURE_GATE"]))
    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        if not self.adventure_seed:
            mylist.append(Offer("Why don't you go have an adventure?",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.register_adventure
                            ))

        return mylist


class DZD_AlliedArmor(Plot):
    LABEL = "DZDHB_AlliedArmor"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Allied Armor")},
            door_sign=(ghterrain.AlliedArmorSignEast, ghterrain.AlliedArmorSignSouth),
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "Allied Armor", player_team=team1, civilian_team=team2,
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")
        foyer.contents.append(ghwaypoints.AlliedArmorSignWP())

        mycon2 = plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene, room1=building,
                                                    room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.TerranDefenseForce)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("Testing the shop.",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop
                            ))

        return mylist


class DZD_EliteEquipment(Plot):
    LABEL = "DZDHB_EliteEquipment"

    active = True
    scope = "INTERIOR"

    def custom_init(self, nart):
        # Create a building within the town.
        building = self.register_element("_EXTERIOR", ghterrain.BrickBuilding(
            waypoints={"DOOR": ghwaypoints.ScrapIronDoor(name="Elite Equipment")},
            tags=[pbge.randmaps.CITY_GRID_ROAD_OVERLAP]), dident="LOCALE")

        # Add the interior scene.
        team1 = teams.Team(name="Player Team")
        team2 = teams.Team(name="Civilian Team")
        intscene = gears.GearHeadScene(35, 35, "Elite Equipment", player_team=team1, civilian_team=team2,
                                       scale=gears.scale.HumanScale)
        intscenegen = pbge.randmaps.SceneGenerator(intscene, gharchitecture.CommercialBuilding())
        self.register_scene(nart, intscene, intscenegen, ident="INTERIOR")
        foyer = self.register_element('_introom', pbge.randmaps.rooms.ClosedRoom(anchor=pbge.randmaps.anchors.south,
                                                                                 decorate=gharchitecture.CheeseShopDecor()),
                                      dident="INTERIOR")

        mycon2 = plotutility.TownBuildingConnection(self, self.elements["LOCALE"], intscene, room1=building,
                                                    room2=foyer, door1=building.waypoints["DOOR"], move_door1=False)

        npc = self.register_element("SHOPKEEPER",
                                    gears.selector.random_character(50, local_tags=self.elements["LOCALE"].attributes,
                                                                    job=gears.jobs.ALL_JOBS["Shopkeeper"]))
        npc.place(intscene, team=team2)

        self.shop = services.Shop(npc=npc, shop_faction=gears.factions.TerranDefenseForce,
                                  ware_types=services.GENERAL_STORE)

        return True

    def SHOPKEEPER_offers(self, camp):
        mylist = list()

        mylist.append(Offer("Testing the shop.",
                            context=ContextTag([context.OPEN_SHOP]), effect=self.shop
                            ))

        return mylist
