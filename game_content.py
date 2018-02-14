import game_classes
import game_constants
import random
import util

#SPRITESHEETS
SPRITESHEET_TILES = game_classes.Spritesheet('resources/tiles.png')
SPRITESHEET_CONSUMABLES = game_classes.Spritesheet('resources/consumables.png')
SPRITESHEET_ENTITIES = game_classes.Spritesheet('resources/entities.png')

# WINDOWS
class Window_PlayerInventory(game_classes.WindowSelectable):
    def __init__(self):
        super().__init__(None, 'Inventory', True, True, w_inventory_items, [w_arrowkeys_input, w_inventory_input], w_inventory_quantities)
class Window_SearchInventory(game_classes.WindowSelectable):
    def __init__(self):
        super().__init__(None, 'Found items', True, True, w_search_items, [w_arrowkeys_input, w_search_input])
class Window_Status(game_classes.WindowSelectable):
    def __init__(self):
        super().__init__(None, 'Status', True, True, w_status_items, [w_arrowkeys_input], w_status_quantities)
class Window_SelectTarget(game_classes.WindowSelectable):
    def __init__(self, parent, item):
        self.parent = parent
        self.item = item
        self.x, self.y = self.item.initialTarget.execute()
        self.surface = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface.set_alpha(50)
        self.active = True
        self.visible = True
        self.image = GAME.entitiesSheet.image_at((64, 0, 32, 32), colorkey = game_constants.COLOR_COLORKEY)
        for window in GAME.windows:
            if window is not self:
                window.visible = False
    def draw(self):
        if self.visible:
            self.surface.fill(game_constants.COLOR_COLORKEY)
            for x in range(GAME.player.x - self.item.maxRange, GAME.player.x + self.item.maxRange+1):
                for y in range(GAME.player.y - self.item.maxRange, GAME.player.y + self.item.maxRange+1):
                    if self.item.targetCondition(x, y) and util.simpledistance((GAME.player.x, GAME.player.y), (x, y)) <= self.item.maxRange:
                        self.surface.fill(game_constants.COLOR_GREEN, pygame.Rect((x - GAME.camera.x)*32, (y - GAME.camera.y)*32, 32, 32))
            self.surface.blit(self.image, ((self.x - GAME.camera.x)*32, (self.y - GAME.camera.y)*32))
            SCREEN.blit(self.surface, (0, 0))
    def input(self, key):
        if key == 'up':
            if util.simpledistance((GAME.player.x, GAME.player.y), (self.x, self.y - 1)) <= self.item.maxRange:
                self.y -= 1
        if key == 'down':
            if util.simpledistance((GAME.player.x, GAME.player.y), (self.x, self.y + 1)) <= self.item.maxRange:
                self.y += 1
        if key == 'left':
            if util.simpledistance((GAME.player.x, GAME.player.y), (self.x - 1, self.y)) <= self.item.maxRange:
                self.x -= 1
        if key == 'right':
            if util.simpledistance((GAME.player.x, GAME.player.y), (self.x + 1, self.y)) <= self.item.maxRange:
                self.x += 1
        if key == 'use':
            if self.item.targetCondition(self.x, self.y):
                self.item.use(self.x, self.y)
                self.parent.destroy()
                self.destroy()
                self.parent.parent.getItems()
                self.parent.parent.active = True
                self.parent.parent.visible = True
                if self.parent.parent.index > 0:
                    self.parent.parent.index -= 1
                GAME.action = 'item'
                GAME.controlsText = game_constants.TEXT_ONINVENTORY

class w_arrowkeys_input(game_classes.Component):
    def execute(self, key):
        if key == 'up':
            self.parent.index = (self.parent.index - 1) % len(self.parent.items)
        if key == 'down':
            self.parent.index = (self.parent.index + 1) % len(self.parent.items)
        if key == 'cancel':
            self.parent.destroy()
class w_inventory_items(game_classes.Component):
    def execute(self):
        return [(item.name, item.color) for item in GAME.player.inventory]
class w_inventory_quantities(game_classes.Component):
    def execute(self):
        return [item.size for item in GAME.player.inventory]
class w_inventory_input(game_classes.Component):
    def execute(self, key):
        if key == 'use':
            if GAME.player.inventory[self.parent.index].itemType == 'consumable':
                self.parent.popupwindow = game_classes.WindowSelectable(self.parent, None, True, True, w_popupinventoryc_items, [w_arrowkeys_input, w_popupinventoryc_input])
                GAME.controlsText = game_constants.TEXT_ONPOPUP
            elif GAME.player.inventory[self.parent.index].itemType == 'equipment':
                self.parent.popupwindow = game_classes.WindowSelectable(self.parent, None, True, True, w_popupinventorye_items, [w_arrowkeys_input, w_popupinventorye_input])
            GAME.windows.append(self.parent.popupwindow)
            self.parent.active = False
        if key == 'cancel':
            GAME.player.active = True
            GAME.controlsText = game_constants.TEXT_ONMAP
class w_popupinventorye_items(game_classes.Component):
    def execute(self):
        return [('Equip', game_constants.COLOR_WHITE), ('Throw', game_constants.COLOR_WHITE), ('Cancel', game_constants.COLOR_WHITE)]
class w_popupinventorye_input(game_classes.Component):
    def execute(self, key):
        if key == 'use':
            if self.parent.index == 0: #EQUIP
                if GAME.player.equipment[self.parent.parent.items[self.parent.parent.index].slot] != None:
                    GAME.player.inventory.append(GAME.player.equipment[self.parent.parent.items[self.parent.parent.index].slot])
                GAME.player.equipment[self.parent.parent.items[self.parent.parent.index].slot] = self.parent.parent.items[self.parent.parent.index]
                GAME.player.equipment.pop(self.parent.parent.items[self.parent.parent.index])
                self.parent.parent.getItems()
                self.parent.parent.active = True
                self.parent.destroy()
            if self.parent.index == 1: #THROW
                item = GAME.player.inventory.pop(self.parent.parent.index)
                item.x = GAME.player.x
                item.y = GAME.player.y
                GAME.items.append(item)
                self.parent.parent.getItems()
                self.parent.parent.active = True
                self.parent.destroy()
            if self.parent.index == 2: #CANCEL
                self.parent.parent.active = True
                self.parent.destroy()
class w_popupinventoryc_items(game_classes.Component):
    def execute(self):
        colorUse = game_constants.COLOR_GRAY
        if GAME.player.inventory[self.parent.parent.index].condition():
                colorUse = game_constants.COLOR_WHITE
        return [('Use', colorUse), ('Throw', game_constants.COLOR_WHITE), ('Cancel', game_constants.COLOR_WHITE)]
class w_popupinventoryc_input(game_classes.Component):
    def execute(self, key):
        if key == 'use':
            if self.parent.index == 0: #USE
                if GAME.player.inventory[self.parent.parent.index].condition():
                    if GAME.player.inventory[self.parent.parent.index].target == 'self':
                        GAME.player.inventory[self.parent.parent.index].use()
                        self.parent.parent.getItems()
                        self.parent.parent.active = True
                        if self.parent.parent.index > 0:
                            self.parent.parent.index -= 1
                        GAME.action = 'item'
                        GAME.controlsText = game_constants.TEXT_ONINVENTORY
                        self.parent.destroy()
                    elif GAME.player.inventory[self.parent.parent.index].target == 'map':
                        self.parent.mapWindow = Window_SelectTarget(self.parent, GAME.player.inventory[self.parent.parent.index])
                        GAME.windows.append(self.parent.mapWindow)
                        self.parent.active = False
            if self.parent.index == 1: #THROW
                item = GAME.player.inventory.pop(self.parent.parent.index)
                item.x = GAME.player.x
                item.y = GAME.player.y
                GAME.items.append(item)
                self.parent.parent.getItems()
                self.parent.parent.active = True
                GAME.controlsText = game_constants.TEXT_ONINVENTORY
                self.parent.destroy()
            if self.parent.index == 2: #CANCEL
                self.parent.parent.active = True
                GAME.controlsText = game_constants.TEXT_ONINVENTORY
                self.parent.destroy()
        if key == 'cancel':
            self.parent.parent.active = True
            GAME.controlsText = game_constants.TEXT_ONINVENTORY
class w_search_items(game_classes.Component):
    def execute(self):
        return [(item.name, item.color) for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]
class w_search_input(game_classes.Component):
    def execute(self, key):
        if key == 'use':
            item = [item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)][self.parent.index]
            if item.size <= GAME.player.capacity - GAME.player.currentWeight():
                GAME.player.inventory.append(item)
                GAME.items.remove(item)
                self.parent.getItems()
            else:
                GAME.addLogMessage('You are carrying too much.', game_constants.COLOR_INFO)
        if key == 'cancel':
            GAME.player.active = True
            GAME.controlsText = game_constants.TEXT_ONMAP
            self.parent.destroy()
class w_status_items(game_classes.Component):
    def execute(self):
        for status in GAME.player.status:
            status.execute()
        return [(status.name, status.color) for status in GAME.player.status]
class w_status_quantities(game_classes.Component):
    def execute(self):
        return [status.turns for status in GAME.player.status]

# PLAYER BEHAVIORS
class b_play_move(game_classes.Component):
    def execute(self, dx = 0, dy = 0):
        if GAME.placeFree(self.parent.x + dx, self.parent.y + dy):
            if GAME.map[self.parent.x + dx][self.parent.y + dy].passable:
                self.parent.x += dx
                self.parent.y += dy
        else:
            for creature in GAME.creatures:
                if (creature is not self and creature.x == self.parent.x + dx and creature.y == self.parent.y + dy):
                    self.parent.attack(creature)
                    break
class b_play_death(game_classes.Component):
    def execute(self):
        pygame.quit()
        sys.exit()
class b_play_starvedamage(game_classes.Component):
    def execute(self):
        self.parent.damage(int(self.parent.stats[0]*0.1), 'true', 'none')
class b_play_hunger(game_classes.Component):
    def execute(self):
        if self.parent.hunger > 0:
            self.parent.hunger -= 1
        else:
            self.parent.onStarve()

class d_play_health(game_classes.Component):
    def execute(self):
        if self.parent.hp < self.parent.stats[0]*0.5:
            self.parent.stats[1] *= 0.5
class d_play_hunger(game_classes.Component):
    def execute(self):
        if self.parent.hunger < 50:
            self.parent.stats[0] = int(self.parent.stats[0] * 0.8)
        elif self.parent.hunger < 30:
            self.parent.stats[0] = int(self.parent.stats[0] * 0.4)


# CREATURES BEHAVIOR
class b_crea_simpleturn(game_classes.Component):
    def execute(self):
        self.parent.antistuck()
        if util.distance(self.parent, GAME.player) == 1:
            self.parent.attack(GAME.player)
        else:
            self.parent.move()
class b_crea_randommove(game_classes.Component):
    def execute(self, dx = 0, dy = 0):
        rnd = random.randint(1,5)
        if rnd == 0:
            dx, dy = (-1, 0)
        elif rnd == 1:
            dx, dy = (1, 0)
        elif rnd == 2:
            dx, dy = (0, -1)
        elif rnd == 3:
            dx, dy = (0, 1)
        else:
            dx, dy = (0, 0)
        if GAME.placeFree(self.parent.x + dx, self.parent.y + dy):
            if GAME.map[self.parent.x + dx][self.parent.y + dy].passable:
                self.parent.x += dx
                self.parent.y += dy
class b_crea_takedamage(game_classes.Component):
    def execute(self, amount, damageType, damageSubtype):
        self.parent.hp -= amount
        if self.parent.hp <= 0:
            self.parent.die()
        GAME.visualeffects.append(v_damagepopup(self.parent.x*32, self.parent.y*32 - 12, amount, game_constants.COLOR_WHITE))
class b_crea_simpledeath(game_classes.Component):
    def execute(self):
        for drop in self.parent.drops:
            rnd = random.random()
            if rnd < drop[1]:
                drop[0].x = self.parent.x
                drop[0].y = self.parent.y
                GAME.items.append(drop[0])
        GAME.creatures.remove(self.parent)
class b_crea_simpleattack(game_classes.Component):
    def execute(self, receiver):
        receiver.damage(self.parent.damageStat, 'physical', 'none')
        GAME.addLogMessage(self.parent.name + ' attacks ' + receiver.name + ' for ' + str(self.parent.damageStat) + ' damage!', game_constants.COLOR_RED)

#STATUS
class s_hunger(game_classes.Component):
    def execute(self):
        self.turns = None
        if self.parent.hunger > 50:
            self.name = 'Well fed'
            self.color = game_constants.COLOR_GREEN
        elif self.parent.hunger > 30:
            self.name = 'Hungry'
            self.color = game_constants.COLOR_YELLOW
        else:
            self.name = 'Starving'
            self.color = game_constants.COLOR_RED
class s_health(game_classes.Component):
    def execute(self):
        self.turns = None
        if self.parent.hp > self.parent.stats[0]*0.5:
            self.name = 'Healty'
            self.color = game_constants.COLOR_GREEN
        elif self.parent.hp > self.parent.stats[0]*0.3:
            self.name = 'Wounded'
            self.color = game_constants.COLOR_YELLOW
        else:
            self.name = 'Dying'
            self.color = game_constants.COLOR_RED

# EFFECTS
class e_getused(game_classes.Component):
    def execute(self, x=0, y=0):
        self.parent.used = True

        # DIRECT EFFECTS
class e_flatheal(game_classes.Component):
    def __init__(self, parent, amount):
        super().__init__(parent)
        self.amount = amount
    def execute(self):
        if self.parent.hp + self.amount > self.parent.stats[0]:
            value = self.parent.stats[0] - self.parent.hp
            GAME.addLogMessage(self.parent.name + ' heals to max!', game_constants.COLOR_HEAL)
        else:
            value = self.amount
            GAME.addLogMessage(self.parent.name + ' heals for ' + str(value) + '.', game_constants.COLOR_HEAL)
        self.parent.hp += value
class e_percheal(game_classes.Component):
    def __init__(self, parent, percent = 0.25):
        super().__init__(parent)
        self.percent = percent
    def execute(self):
        if math.floor(self.parent.stats[0]*self.percent + self.parent.hp) > self.parent.stats[0]:
            value = self.parent.stats[0] - self.parent.hp
            GAME.addLogMessage(self.parent.name + ' heals to max!', game_constants.COLOR_HEAL)
        else:
            value = math.floor(self.parent.stats[0]*self.percent)
            GAME.addLogMessage(self.parent.name + ' heals for ' + str(value) + '.', game_constants.COLOR_HEAL)
        self.parent.hp += value
class e_venom(game_classes.Component):
    def __init__(self, parent, amount, turns = -1):
        super().__init__(parent)
        self.amount = amount
        self.turns = turns
    def execute(self):
        if self.turns != 0:
            self.turns -= 1
            GAME.addLogMessage(self.parent.name + ' takes ' + str(self.amount) + ' damage from venom.', consants.COLOR_VENOM)
            self.parent.damage(self.amount)
class e_createbomb(game_classes.Component):
    def __init__(self, parent, turns, radius, damage):
        super().__init__(parent)
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute(self):
        SPRITESHEET_ENTITIES.append(n_bomb(self.parent.x, self.parent.y, SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY), self.turns, self.radius, self.damage))
        GAME.addLogMessage('The bomb will explode in ' + str(self.turns) + ' turns!', game_constants.COLOR_ALLY)
class e_eat(game_classes.Component):
    def __init__(self, parent, amount):
        super().__init__(parent)
        self.amount = amount
    def execute(self):
        if self.parent.hunger + self.amount > 100:
            value = 100 - self.parent.hunger
            GAME.addLogMessage(self.parent.name + ' is full!', game_constants.COLOR_HEAL)
        else:
            value = self.amount
            GAME.addLogMessage(self.parent.name + ' eats.', game_constants.COLOR_HEAL)
        self.parent.hunger += value

        # DISTANCE EFFECTS
class e_createbomb_l():
    def __init__(self, turns, radius, damage):
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute(self, x, y):
        GAME.entities.append(n_bomb(x, y, SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY), self.turns, self.radius, self.damage))
        GAME.addLogMessage('The bomb will explode in ' + str(self.turns) + ' turns!', game_constants.COLOR_ALLY)
class e_damage_l():
    def __init__(self, amount, damageType, damageSubtype):
        self.amount = amount
        self.damageType = damageType
        self.damageSubtype = damageSubtype
    def execute(self, x, y):
        for game_classes.Monster in GAME.creatures:
            if game_classes.Monster.x == x and game_classes.Monster.y == y:
                game_classes.Monster.damage(self.amount, self.damageType, self.damageSubtype)

# CONDITIONS / INTIAL COORDINATES
class c_playnotfullhealth(game_classes.Component):
    def execute(self):
        return GAME.player.hp < GAME.player.stats[0]
class c_playnotfullhunger(game_classes.Component):
    def execute(self):
        return GAME.player.hunger < 100
class c_initonplayer(game_classes.Component):
    def execute(self):
        return (GAME.player.x, GAME.player.y)
class c_creatureinlocation(game_classes.Component):
    def execute(self, x, y):
        for creature in GAME.creatures:
            if creature.x == x and creature.y == y:
                return True
        return False

# ENTITIES
class n_bomb(game_classes.Entity):
    def __init__(self, x, y, sprite, turns, radius, damage):
        super().__init__(x, y, sprite)
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute_action(self):
        if self.turns > 0:
            self.turns -= 1
        else:
            for game_classes.Tilex in range(self.x - self.radius, self.x + self.radius+1):
                for game_classes.Tiley in range(self.y - self.radius, self.y + self.radius+1):
                    if game_classes.Tilex < game_constants.MAP_WIDTH[GAME.level] and game_classes.Tiley < game_constants.MAP_HEIGHT[GAME.level]:
                        if util.simpledistance((game_classes.Tilex, game_classes.Tiley), (self.x, self.y)) <= self.radius:
                            GAME.visualeffects.append(v_square_fadeout(game_classes.Tilex, game_classes.Tiley, game_constants.COLOR_RED))
                            GAME.map[game_classes.Tilex][game_classes.Tiley].onDestroy()
            for creature in GAME.creatures:
                if util.distance(self, creature) <= self.radius:
                    creature.damage(self.damage, 'physical', 'explosion')
            map_light_update(GAME.light_map)
            GAME.addLogMessage('You hear a loud explosion.', game_constants.COLOR_INFO)
            GAME.entities.remove(self)

# VISUALS
class v_square_fadeout(game_classes.VisualEffect):
    def __init__(self, x, y, color):
        super().__init__(x*32, y*32, 32, 32)
        pygame.draw.rect(self.surface, color, (0, 0, 32, 32))
    def execute(self):
        super().execute()
        self.surface.set_alpha(255*(game_constants.EFFECTS_MAXTIME - self.time)/game_constants.EFFECTS_MAXTIME)
        if self.time > game_constants.EFFECTS_MAXTIME:
            GAME.visualeffects.remove(self)
class v_damagepopup(game_classes.VisualEffect):
    def __init__(self, x, y, damage, color, critical = False):
        if critical:
            text = game_constants.FONT_PERFECTDOS_LARGE.render(str(damage), False, game_constants.COLOR_CRITICAL)
        else:
            text = game_constants.FONT_PERFECTDOS.render(str(damage), False, color)
        width = text.get_width()
        height = text.get_height()
        super().__init__(x, y, width, height)
        self.x +=  16 - width * 0.5
        self.surface.fill(game_constants.COLOR_COLORKEY)
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface.blit(text, (0, 0))
        self.xspeed = random.random()*2 - 1
        self.yspeed = -0.6
    def execute(self):
        super().execute()
        self.surface.set_alpha(255*(game_constants.EFFECTS_MAXTIME - self.time)/game_constants.EFFECTS_MAXTIME)
        if self.time > game_constants.EFFECTS_MAXTIME:
            GAME.visualeffects.remove(self)
        self.yspeed += 0.05
        self.x += self.xspeed
        self.y += self.yspeed

# TILES
class t_cave_wall(game_classes.Tile):
    def __init__(self, x, y):
        rnd = random.choice([0, 1, 2]) # CHOOSE FROM 3 IMAGES
        super().__init__(x, y, False, False, 0, SPRITESHEET_TILES.image_at((0, 32*rnd, 32, 32)), SPRITESHEET_TILES.image_at((0, 32*rnd + 96, 32, 32)))
    def onDestroy(self):
        GAME.map[self.x][self.y] = t_cave_floor(self.x, self.y)
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, True, True)
class t_cave_floor(game_classes.Tile):
    def __init__(self, x, y):
        rnd = random.choice([0, 1, 2]) # CHOOSE FROM 3 IMAGES
        super().__init__(x, y, True, True, 0, SPRITESHEET_TILES.image_at((32, 32*rnd, 32, 32)), SPRITESHEET_TILES.image_at((32, 32*rnd + 96, 32, 32)))
class t_unbreakable_wall(game_classes.Tile):
    def __init__(self, x, y):
        rnd = random.choice([0, 1, 2]) # CHOOSE FROM 3 IMAGES
        super().__init__(x, y, False, False, 0, SPRITESHEET_TILES.image_at((64, 32*rnd, 32, 32)), SPRITESHEET_TILES.image_at((64, 32*rnd + 96, 32, 32)))

# MONSTERS
class m_slime(game_classes.Monster):
    def __init__(self, x, y):
        super().__init__(x, y, game_constants.SPRITE_ENEMY_SLIME, 'Slime', 10, [(i_minorhealpotion(0, 0), 0.5)], [b_crea_simpleturn(self)], [b_crea_randommove(self)], [b_crea_simpleattack(self)], [b_crea_takedamage(self)], [b_crea_simpledeath(self)])

# CONSUMABLES
class i_minorhealpotion(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x, #X
                         y, #Y
                         SPRITESHEET_CONSUMABLES.image_at((0, 0, 32, 32), game_constants.COLOR_COLORKEY), #SPRITE
                         'Minor heal potion', #NAME
                         game_constants.COLOR_WHITE, #COLOR
                         1, #WEIGHT
                         [e_flatheal(GAME.player, 10), e_getused(self)], #EFFECTS
                         useCondition = [c_playnotfullhealth(GAME.player)]) #CONDITION
class i_bomb(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x, #X
                         y, #Y
                         SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY), #SPRITE
                         'Bomb', #NAME
                         game_constants.COLOR_WHITE, #COLOR
                         3, #WEIGHT
                         [e_createbomb(GAME.player, 4, 4, 10), e_getused(self)]) #EFFECTS
class i_meat(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x, #X
                         y, #Y
                         SPRITESHEET_CONSUMABLES.image_at((64, 0, 32, 32), game_constants.COLOR_COLORKEY), #SPRITE
                         'Meat', #NAME
                         game_constants.COLOR_WHITE, #COLOR
                         4, #WEIGHT
                         [e_eat(GAME.player, 80), e_getused(self)], #EFFECTS
                         useCondition = [c_playnotfullhunger(GAME.player)]) #CONDITION
class i_throwablebomb(game_classes.ConsumableMap):
    def __init__(self, x, y):
        super().__init__(x, #X
                         y, #Y
                         SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY), #SPRITE
                         'Throwable bomb', #NAME
                         game_constants.COLOR_WHITE, #COLOR
                         3, #WEIGHT
                         [e_createbomb_l(4, 4, 10), e_getused(self)], #EFFECTS
                         c_initonplayer, #INITIAL COORDINATES
                         4) #MAX RANGE
class i_thunderrod(game_classes.ConsumableMap):
    def __init__(self, x, y):
        super().__init__(x, #X
                         y, #Y
                         SPRITESHEET_CONSUMABLES.image_at((96, 0, 32, 32), game_constants.COLOR_COLORKEY), #SPRITE
                         'Lightning rod', #NAME
                         game_constants.COLOR_WHITE, #COLOR
                         1, #WEIGHT
                         [e_damage_l(5, 'magical', 'lightning'), e_getused(self)], #EFFECTS
                         c_initonplayer, #INITIAL COORDINATES
                         8, #MAX RANGE
                         targetCondition = [c_creatureinlocation(self)],
                         charges = 3) #TARGET CONDITION

# PLAYABLE CHARACTERS
class p_normal(game_classes.Player):
    def __init__(self, x, y):
        super().__init__(x,
                        y,
                        game_constants.SPRITE_PLAYER,
                        [d_play_hunger(self, 11), d_play_health(self, 10)],
                        [s_health(self), s_hunger(self)],
                        [b_play_move(self)],
                        [b_play_starvedamage(self)],
                        [b_crea_simpleattack(self)],
                        [b_play_death(self)],
                        [b_crea_takedamage(self)],
                        [b_play_hunger(self)])
