import pygame
import game_constants
import game_util
import libtcodpy

pygame.init()
global GAME, SCREEN

class Window_Description:
    def __init__(self):
        self.content_surface = pygame.Surface((game_constants.DESCWINDOW_WIDTH, game_constants.DESCWINDOW_HEIGHT))
        self.content_surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface = pygame.Surface((game_constants.DESCWINDOW_WIDTH, game_constants.DESCWINDOW_HEIGHT))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.reset()
        self.index = 0
        self.need_redraw = True
        self.x = 0
        self.y = 0
    def updateInfo(self, icon_list, name, color, typename, content):
        self.surface.fill(game_constants.COLOR_COLORKEY)
        self.content_surface.fill(game_constants.COLOR_COLORKEY)
        self.icon = [pygame.transform.scale2x(icon_list[i]) for i in range(len(icon_list))]
        self.name = game_constants.FONT_PERFECTDOS.render(name, False, color)
        self.typename = game_constants.FONT_PERFECTDOS_SMALL.render(typename, False, game_constants.COLOR_WHITE)
        for lineIndex in range(len(content)):
            xoffset = 0
            for element in content[lineIndex]:
                text = game_constants.FONT_PERFECTDOS.render(element[0], False, element[1])
                self.surface.blit(text, (xoffset + 16, 96 + lineIndex*16))
                xoffset += text.get_width()
        self.index = 0
        self.need_redraw = True
    def update(self):
        self.index = (self.index + 1) % len(self.icon)
    def reset(self):
        self.updateInfo([game_constants.SPRITE_NULL], '', game_constants.COLOR_WHITE, '', [])
    def draw(self):
        if self.need_redraw:
            self.surface.blit(game_constants.SPRITE_DESCRIPTIONWINDOW, (0, 0))
            self.surface.blit(self.content_surface, (0, 0))
            self.surface.blit(self.name, (100, 24))
            self.surface.blit(self.typename, (100, 44))
            self.surface.blit(game_constants.SPRITE_BACK_68X68, (16, 16))
            self.surface.blit(self.icon[0], (16, 16)) # 0 is a placeholder, meaning no animation is shown
            self.need_redraw = False
            GAME.update_rects.append(GAME.surface_windows.blit(self.surface, (self.x, self.y)))

class MainMenu:
    def __init__(self):
        self.timer = 0

        self.option = 0
        self.characterNumber = 0

        self.surface_logo = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))
        self.surface_options = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))

        self.surface_options.set_colorkey(game_constants.COLOR_COLORKEY)

        self.optionsText = [game_constants.FONT_PERFECTDOS_LARGE.render('Start game', False, game_constants.COLOR_WHITE),
                        game_constants.FONT_PERFECTDOS_LARGE.render('Options', False, game_constants.COLOR_WHITE),
                        game_constants.FONT_PERFECTDOS_LARGE.render('Exit', False, game_constants.COLOR_WHITE)]

        self.rd_img = True
        self.rd_opt = True
        self.update_rects = []
class Game:
    def __init__(self):
        # Initialization of game structures
        self.log = []
        self.creatures = []
        self.camera = Camera()
        self.windows = []
        self.items = []
        self.entities = []
        self.visualeffects = []
        self.visualactiveeffects = []
        self.descriptionWindow = Window_Description()
        self.player = None

        # General
        self.turn_counter = 0
        self.controlsText = game_constants.TEXT_ONMAP
        self.long_log = False
        self.show_minimap = 0

        # Level and map variables
        self.level = 0
        self.map = None
        self.light_map = None

        # Surfaces definition
        self.surface_map = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_log = pygame.Surface((409, 133))
        #self.surface_effects = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_status = pygame.Surface((699, 85 + 128)) # 85 for the main sprite, 128 for the extra message box that pops up from the bottom.
        self.surface_windows = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_entities = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))

        # Colorkeys and surface initialization
        #self.surface_effects.fill(game_constants.COLOR_COLORKEY)
        #self.surface_effects.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_status.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_windows.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_windows.set_alpha(None)
        self.surface_entities.fill(game_constants.COLOR_COLORKEY)
        self.surface_entities.set_colorkey(game_constants.COLOR_COLORKEY)

        # Player Movement control
        self.player_moved = False
        self.movetimer = 10

        # Redraw surfaces control
        self.rd_log = True
        self.rd_sta = True
        self.rd_win = True
        self.rd_min = True
        self.update_rects = [] # Currently not used

        # Description Window
        self.draw_descriptionwindow = False

        # Popup window
        self.popup_target_y = 0
        self.popup_time = -1
        self.popup_lines = []

        # Surfaces positions
        self.status_position_x, self.status_position_y = (game_constants.STATUS_IDLE_X, game_constants.STATUS_IDLE_Y)
        self.popup_position_x, self.popup_position_y = (game_constants.POPUP_IDLE_X, game_constants.POPUP_IDLE_Y)
        self.log_position_x, self.log_position_y = (game_constants.LOG_IDLE_X, game_constants.LOG_IDLE_Y)

    def setPopup(self, message_lines, max_time):
        if not message_lines:
            self.popup_target_y = 0
            self.popup_time = -1
        else:
            self.popup_target_y = len(message_lines)*12 + 20
            self.popup_time = max_time
            self.popup_lines = message_lines
    def updatePopupTime(self):
        if self.popup_time > 0:
            self.popup_time -= 1
        elif self.popup_time == 0:
            self.setPopup(None, 0)
            self.popup_time = -1
        if self.popup_time == -1 and self.popup_position_y == 0:
            self.popup_lines = []
    def addLogMessage(self, message, color):
        self.log.insert(0, (message, color))
        self.rd_log = True
    def entitiesExecuteTurn(self):
        for entity in self.entities + self.creatures + self.items:
            entity.event('turn', [entity])
            if libtcodpy.map_is_in_fov(self.light_map, entity.x, entity.y):
                entity.last_seen_pos = (entity.x, entity.y)
                entity.last_seen_image = entity.frame
                entity.last_visible = entity.visible
    def placeFree(self, x, y):
        for obj in self.creatures:
            if obj.x == x and obj.y == y:
                return False
        return True
    def updateOrder(self):
        self.entities.sort(key = lambda e: e.priority)
        self.creatures.sort(key = lambda c: c.priority)
    def generateMap(self, gen_function):
        self.map, self.items, self.entities, self.creatures, self.player.x, self.player.y = gen_function(game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level])
        self.lightmapInit()
        self.creatures.append(self.player)
        game_util.map_light_update(self.light_map)
    def lightmapInit(self):
        self.light_map = libtcodpy.map_new(game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level])
        for x in range(game_constants.MAP_WIDTH[self.level]):
            for y in range(game_constants.MAP_HEIGHT[self.level]):
                libtcodpy.map_set_properties(self.light_map, x, y, self.map[x][y].transparent, self.map[x][y].passable)

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()
    def image_at(self, rectangle, colorkey = None): # Load a specific image from a specific rectangle
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    def images_at(self, rects, colorkey = None): # Load a whole bunch of images and return them as a list
        return [self.image_at(rect, colorkey) for rect in rects]
    def images_at_loop(self, rects, colorkey = None):
        return self.images_at(rects, colorkey) + list(reversed(self.images_at(rects, colorkey)))
    def load_strip(self, rect, image_count, colorkey = None): # Load a whole strip of images
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
class Tile:
    def __init__(self, x, y, passable, transparent, sprite, destroy_func = None, walk_func = None):
        self.x = x
        self.y = y
        self.passable = passable
        self.transparent = transparent
        self.destroy_func = destroy_func
        self.walk_func = walk_func
        self.sprite = sprite.convert()
        self.sprite_shadow = self.sprite.convert()
        self.discovered = False
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, self.passable, self.transparent)
        dark = pygame.Surface((self.sprite.get_width(), self.sprite.get_height()), flags=pygame.SRCALPHA)
        dark.fill((50, 50, 50, 0))
        self.sprite_shadow.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    def onDestroy(self):
        if self.destroy_func:
            self.destroy_func(self)
    def onWalk(self):
        pass
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    def update(self, x, y):
        self.x += (x-self.x-game_constants.CAMERA_WIDTH*16)*0.05
        self.y += (y-self.y-game_constants.CAMERA_HEIGHT*16)*0.05
        self.x = int(game_util.clamp(self.x, 0, game_constants.MAP_WIDTH[GAME.level]*32 - game_constants.CAMERA_WIDTH*32))
        self.y = int(game_util.clamp(self.y, 0, game_constants.MAP_HEIGHT[GAME.level]*32 - game_constants.CAMERA_HEIGHT*32))
class VisualEffect:
    def __init__(self, x, y, visible, images):
        self.x = x
        self.y = y
        self.visible = visible
        self.images = images
        self.image = images[0]
    def update(self):
        pass
    def draw(self):
        if game_util.isinscreen(self.x*32, self.y*32) and self.visible:
            SCREEN.blit(self.image, (self.x*32 - GAME.camera.x, self.y*32 - GAME.camera.y + 8))
    def destroy(self):
        if self in GAME.visualactiveeffects:
            GAME.visualactiveeffects.remove(self)
        if self in GAME.visualeffects:
            GAME.visualeffects.remove(self)
class AnimationOnce(VisualEffect):
    def __init__(self, x, y, images, frame_wait):
        super().__init__(x, y, True, images)
        self.counter_next = 0
        self.frame = 0
        self.frame_wait = frame_wait
    def update(self):
        self.counter_next += 1
        if self.counter_next == self.frame_wait:
            self.frame += 1
            if self.frame == len(self.images):
                self.destroy()
                return
            self.counter_next = 0
            self.image = self.images[self.frame]
class LoopVisualEffect(VisualEffect):
    def __init__(self, x, y, visible, images, frame_wait):
        super().__init__(x, y, visible, images)
        self.frame_wait = frame_wait
        self.counter_next = 0
        self.frame = 0
    def update(self):
        self.counter_next += 1
        if self.counter_next == self.frame_wait:
            self.counter_next = 0
            self.frame = (self.frame + 1) % len(self.images)
            self.image = self.images[self.frame]
class CreatureMoveVisualEffect(LoopVisualEffect):
    def __init__(self, creature, from_pos, to_pos, duration):
        super().__init__(creature.x, creature.y, True, creature.sprite_list[creature.frame:] + creature.sprite_list[:creature.frame], game_constants.ANIMATION_WAIT * 8)
        self.creature = creature
        self.dx, self.dy = to_pos[0], to_pos[1]
        self.duration = duration
        self.current = 0
        self.creature.visible = False
    def update(self):
        if self.duration == 0:
            self.destroy()
            return
        self.current += 1
        self.x += self.dx / self.duration
        self.y += self.dy / self.duration
        super().update()
        if self.current == self.duration:
            self.destroy()
    def destroy(self):
        super().destroy()
        self.creature.visible = True

class Window:
    def __init__(self, x, y, sprite):
        self.x, self.y = (x, y)
        self.sprite = sprite.convert()
        self.surface = pygame.Surface((self.sprite.get_width(), self.sprite.get_height()))
        self.parent = None
        self.redraw = True
        self.visible = True
        self.active = True
        self.popup = None
        GAME.rd_win = True
        GAME.player.active = False
    def draw(self):
        if not self.visible:
            return
        if self.redraw:
            self.update()
        GAME.surface_windows.blit(self.surface, (self.x, self.y))
    def update(self):
        self.surface.blit(self.sprite, (0, 0))
    def destroy(self):
        if self in GAME.windows:
            GAME.windows.remove(self)
        if self.parent == None:
            GAME.player.active = True
        GAME.rd_win = True
    def input(self, key):
        if not self.active:
            return
        if self.popup == None:
            self.getItems()
            self.basicControls(key)
            self.redraw = True
        else:
            self.popup.input(key)
            self.popup.redraw = True
        GAME.rd_win = True
    def popupInput(self, key):
        if self.popup == None:
            return
    def destroyPopup(self):
        self.popup.destroy()
        self.popup = None
        self.active = True
        GAME.rd_win = True
    def basicControls(self, key):
        pass
    def getItems(self):
        pass
class WindowList(Window):
    def __init__(self, x, y, sprite, descriptable):
        super().__init__(x, y, sprite)
        self.index = 0
        self.getItems()
    def basicControls(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.items)
        elif key == 'cancel':
            self.destroy()
    def getItems(self):
        self.items = []
    def update(self):
        super().update()
    # def updateDescription(self):
    #     if self.needDesc:
    #         GAME.descriptionWindow.x = self.x - game_constants.DESCWINDOW_WIDTH
    #         GAME.descriptionWindow.y = min(self.index*16+self.yoffset + 32, game_constants.CAMERA_HEIGHT*32 - game_constants.DESCWINDOW_HEIGHT)
class WindowPopupList(WindowList):
    def __init__(self, parent_window, window_name, x, y, sprite, options_list):
        super().__init__(x, y, sprite, False)
        self.parent_window = parent_window
        self.window_name = window_name
        self.items = options_list
    def input(self, key):
        self.basicControls(key)
        self.redraw = True
        GAME.rd_win = True
    def update(self):
        super().update()
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 8, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16 + 8, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1], game_constants.COLOR_SHADOW)
    def basicControls(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.items)
        elif key == 'cancel':
            self.parent_window.popupInput('cancel')
        elif key == 'use':
            self.parent_window.popupInput('use')
    def getItems(self):
        pass
    def destroy(self):
        GAME.windows.remove(self)
class SelectTarget:
    def __init__(self, parent_window, window_name, item, marker_sprite):
        self.previousCamera = (GAME.camera.x, GAME.camera.y)
        self.max_range = item.maxRange
        self.valid_tiles = [(x, y) for x in range(-self.max_range, self.max_range + 1) for y in range(-self.max_range, self.max_range + 1) if item.targetCondition(x, y)]
        self.updatePosition()
        self.surface = pygame.Surface(((self.max_range + 1)*64, (self.max_range + 1)*64))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.parent = parent_window
        self.marker_sprite = marker_sprite
        self.marker_x, self.marker_y = item.getInitialTarget()
        self.visible = True
        self.active = True
        self.redraw = True
        self.redraw_all = True
    def updatePosition(self):
        if (GAME.camera.x, GAME.camera.y) != self.previousCamera:
            self.previousCamera = (GAME.camera.x, GAME.camera.y)
        self.x = (GAME.player.x - self.max_range)*32 - GAME.camera.x
        self.y = (GAME.player.y - self.max_range)*32 - GAME.camera.y
    def draw(self):
        if self.redraw_all:
            self.redraw_all = False
            self.surface.set_alpha()
            self.surface.fill(game_constants.COLOR_COLORKEY)
            self.updatePosition()
            self.update()
            self.surface.set_alpha(150)
        GAME.rd_win = True
        SCREEN.blit(self.surface, (self.x, self.y))
        SCREEN.blit(self.marker_sprite, (self.marker_x*32, self.marker_y*32))
    def update(self):
        self.updatePosition()
        for x in range(-self.max_range, self.max_range + 1):
            for y in range(-self.max_range, self.max_range + 1):
                if (x, y) in self.valid_tiles and game_util.simpledistance((x, y), (0, 0)) <= self.max_range:
                    self.surface.fill(game_constants.COLOR_GREEN, ((self.max_range + x)*32, (self.max_range + y)*32, 32, 32))
    def destroy(self):
        if self in GAME.windows:
            GAME.windows.remove(self)
        if self.parent == None:
            GAME.player.active = True
        GAME.rd_win = True
    def input(self, key):
        self.basicControls(key)
        self.redraw_all = True
        GAME.rd_win = True
    def basicControls(self, key):
        pass

class Entity:
    def __init__(self, x, y, tags, sprite_list, behaviors = []):
        self.x = x
        self.y = y
        self.behaviors = behaviors
        self.tags = tags
        self.visible = True
        self.priority = 0
        self.sprite_list = sprite_list
        self.sprite = self.sprite_list[0]
        self.frame = 0
        self.counter_next = 0
        self.sprites_shadow = [sprite.convert() for sprite in self.sprite_list]
        dark = pygame.Surface((self.sprite.get_width(), self.sprite.get_height()), flags=pygame.SRCALPHA)
        dark.fill((50, 50, 50, 0))
        for sprite in self.sprites_shadow:
            sprite.set_colorkey(game_constants.COLOR_COLORKEY)
            sprite.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            sprite.set_colorkey((49, 0 ,49))
        self.last_seen_pos = None
        self.last_seen_visible = True
        self.last_seen_image = self.frame
    def draw(self):
        if self.visible:
            GAME.surface_entities.blit(self.sprite, (self.x*32 - GAME.camera.x, self.y*32 - GAME.camera.y))
    def draw_last_seen(self):
        if self.last_seen_visible and self.last_seen_pos:
            GAME.surface_entities.blit(self.sprites_shadow[self.last_seen_image], (self.last_seen_pos[0] * 32 - GAME.camera.x, self.last_seen_pos[1] * 32 - GAME.camera.y))
    def update_frame(self):
        self.counter_next += 1
        if self.counter_next == game_constants.ANIMATION_WAIT * 8:
            self.counter_next = 0
            self.frame = (self.frame + 1) % len(self.sprite_list)
            self.sprite = self.sprite_list[self.frame]
    def destroy(self):
        GAME.entities.remove(self)
    def event(self, event_name, args = ()):
        for e in sorted(self.behaviors, key = lambda x: x[1]):
            e[0].execute(event_name, self, args)
class Creature(Entity):
    def __init__(self, x, y, tags, sprite_list, behaviors, stats, statmods = []):
        super().__init__(x, y, tags, sprite_list, behaviors)
        self.priority = 1
        self.behaviors = behaviors
        self.stats = stats
        self.statmods = statmods
        self.currentHitPoints = self.getMaxHitPoints()
        self.currentMagicPoints = self.getMaxMagicPoints()
    def isEnemy(self):
        return 'enemy' in self.tags
    def draw(self):
        super().draw()
        if self.visible:
            pygame.draw.rect(GAME.surface_entities, game_constants.COLOR_GREEN, ((self.x*32 - GAME.camera.x)+1, (self.y*32 - GAME.camera.y)+30, self.currentHitPoints/self.getMaxHitPoints()*(self.sprite.get_width()-1), 1))

    def getStatMod(self, stat_name):
        statmods = sorted(self.statmods, key = lambda x: x.priority)
        amount = 0
        for mod in statmods:
            amount = mod.execute(self, stat_name, amount)
        return amount
    def getMaxHitPoints(self):
        return max(int((self.stats['HitPointsFlat'])*self.stats['HitPointsMult']/100) + self.getStatMod('HitPointsFlat'), 1)
    def getMaxMagicPoints(self):
        return max(int((self.stats['MagicPointsFlat'])*self.stats['MagicPointsMult']/100) + self.getStatMod('MagicPointsFlat'), 1)
    def getPhyAttack(self):
        return max(int(self.stats['PhyAttackFlat']*self.stats['PhyAttackMult']/100) + self.getStatMod('PhyAttackFlat'), 0)
    def getMagAttack(self):
        return max(int((self.stats['MagAttackFlat'])*self.stats['MagAttackMult']/100) + self.getStatMod('MagAttackFlat'), 0)
    def getPhyArmor(self):
        return max(int((self.stats['PhyArmorFlat'])*self.stats['PhyArmorMult']/100) + self.getStatMod('PhyArmorFlat'), 1)
    def getMagArmor(self):
        return max(int((self.stats['MagArmorFlat'])*self.stats['MagArmorMult']/100) + self.getStatMod('MagArmorFlat'), 1)
class Player(Creature):
    def __init__(self, x, y, sprite_list, portrait_list, stats, equipment, inventory, modifiers, status, skilltree, behaviors, statmods = []):
        super().__init__(x, y, ['player'], sprite_list, behaviors, stats, statmods)
        self.inventory = inventory
        self.name = 'Player'
        self.portrait_list = portrait_list
        self.xp = 0
        self.level = 1
        self.equipment = equipment
        self.currentHunger = game_constants.MAX_HUNGER
        self.active = True
        self.priority = 2

        self.potion = None

        self.modifiers = modifiers
        self.status = status
        self.skilltree = skilltree
        self.behaviors = behaviors
    def input(self, key):
        if self.active:
            if key == 'up':
                self.event('move', (0, -1))
                game_util.map_light_update(GAME.light_map)
            elif key == 'down':
                self.event('move', (0, 1))
                game_util.map_light_update(GAME.light_map)
            elif key == 'left':
                self.event('move', (-1, 0))
                game_util.map_light_update(GAME.light_map)
            elif key == 'right':
                self.event('move', (1, 0))
                game_util.map_light_update(GAME.light_map)
    def canAttack(self, relativePosition):
        if self.equipment[0] is None: # No weapon equipped
            return [creature for creature in GAME.creatures if creature is not self and (creature.x, creature.y) == (self.x + relativePosition[0], self.y + relativePosition[1]) and 'monster' in creature.tags]
        return self.equipment[0].attackTargets(relativePosition) # Weapon range
    def tilesAttack(self, relativePosition):
        if self.equipment[0] is None: # No weapon equipped
            return [(self.x + relativePosition[0], self.y + relativePosition[1])]
        return self.equipment[0].attackTiles(relativePosition) # Weapon range


    def getMaxCarry(self):
        return 10 + self.stats['MaxCarry']
    def getHungerDepletion(self):
        return max(1, 4 + self.stats['HungerFlat'])
    def getCurrentCarry(self):
        return sum([item.size for item in self.inventory] + [item.size for item in self.equipment if item is not None])
class Monster(Creature):
    def __init__(self, x, y, tags, sprite_list, name, drops, behaviors, stats, statmods = []):
        super().__init__(x, y, tags, sprite_list, behaviors, stats, statmods)
        self.name = name
        self.drops = drops
        self.tags = ['monster'] + tags
class Item(Entity):
    def __init__(self, x, y, tags, sprite_list, name, rarity, size, description):
        super().__init__(x, y, tags, sprite_list)
        self.name = name
        self.size = size
        self.rarity = rarity
        if self.rarity == 'Common':
            self.color = game_constants.COLOR_WHITE
        elif self.rarity == 'Rare':
            self.color = game_constants.COLOR_BLUE
        elif self.rarity == 'Mythic':
            self.color = game_constants.COLOR_CYAN
        elif self.rarity == 'Antique':
            self.color = game_constants.COLOR_ORANGE
        if self.rarity == 'Divine':
            self.color = game_constants.COLOR_DARKRED
        else:
            self.color = game_constants.COLOR_GRAY
        self.description = description
class Equipment(Item):
    def __init__(self, x, y, name, rarity, size, description, slot, stats, statmods, mods, requirements, tags, sprite_list):
        super().__init__(x, y, tags, sprite_list, name, rarity, size, description)
        self.slot = slot
        self.itemType = 'equipment'
        self.stats = stats
        self.statmods = statmods
        self.mods = mods
        self.requirements = [requirement(self) for requirement in requirements]
    def equip(self):
        for stat, value in self.stats:
            GAME.player.stats[stat] += value
        for mod in self.mods:
            GAME.player.behaviors.append(mod)
        for statmod in self.statmods:
            GAME.player.statmods.append(statmod)
    def unequip(self):
        for stat, value in self.stats:
            GAME.player.stats[stat] -= value
        for mod in self.mods:
            GAME.player.statmods.remove(mod)
    def canEquip(self):
        return all(requirement() for requirement in self.requirements)
class Weapon(Equipment):
    def __init__(self, x, y, name, rarity, size, description, stats, statmods, mods, requirements, tags, sprite_list, spriteattack_list):
        super().__init__(x, y, name, rarity, size, description, 0, stats, statmods, mods, requirements, tags, sprite_list)
        self.spriteattack_list = spriteattack_list
    def attackTargets(self, relativePosition):
        pass
    def attackTiles(self, relativePosition):
        pass
class Consumable(Item):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, effects, useCondition = [], charges = 1):
        super().__init__(x, y, tags, sprite_list, name, color, size, description)
        self.tags += ['target_self']
        self.onUse = effects
        self.useCondition = useCondition
        self.charges = charges
        self.displayCharges = self.charges == 1
        self.itemType = 'consumable'
        self.used = False
    def use(self, *args):
        for action in self.onUse:
            action.execute()
        if self.used:
            GAME.player.inventory.remove(self)
    def condition(self):
        for condition in self.useCondition:
            if not condition.execute():
                return False
        return True
    def gotUsed(self):
        return self.used
class ConsumableMap(Consumable):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, effects, initialTarget, maxRange, useCondition = [], charges = [], targetCondition = []):
        super().__init__(x, y,tags, sprite_list, name, color, size, description, effects, useCondition, charges)
        self.tags.remove('target_self')
        self.tags += ['target_map']
        self.initialTarget = initialTarget(self)
        self.maxRange = maxRange
        self.conditions = targetCondition
    def getInitialTarget(self):
        return self.initialTarget.execute()
    def targetCondition(self, x, y):
        for condition in self.conditions:
            if not condition.execute(x, y):
                return False
        return True
    def use(self, x, y):
        for action in self.onUse:
            action.execute(x, y)
        if self.used:
            GAME.player.inventory.remove(self)

class ShortSword(Weapon):
    def attackTargets(self, relativePosition):
        return [creature for creature in GAME.creatures if creature is not self and (creature.x, creature.y) == (GAME.player.x, GAME.player.y) + relativePosition and 'monster' in creature.tags]
    def attackTiles(self, relativePosition):
        return [(GAME.player.x + relativePosition[0], GAME.player.y + relativePosition[1])]
class LongSword(Weapon):
    def attackTargets(self, relativePosition): # TODO: Fix this behavior
        if relativePosition[0] == 0:
            return [creature for creature in GAME.creatures if creature is not self and creature.x in [GAME.player.x + 1, GAME.player.x, GAME.player.x - 1] and creature.y == GAME.player.y + relativePosition[1] and 'monster' in creature.tags]
        elif relativePosition[1] == 0:
            return [creature for creature in GAME.creatures if creature is not self and creature.x == GAME.player.x + relativePosition[0] and creature.y in [GAME.player.y + 1, GAME.player.y, GAME.player.y - 1] and 'monster' in creature.tags]
    def attackTiles(self, relativePosition):
        if relativePosition[0] == 0:
            return [(GAME.player.x - 1, GAME.player.y + relativePosition[1]), (GAME.player.x, GAME.player.y + relativePosition[1]), (GAME.player.x + 1, GAME.player.y + relativePosition[1])]
        elif relativePosition[1] == 0:
            return [(GAME.player.x + relativePosition[0], GAME.player.y - 1), (GAME.player.x + relativePosition[0], GAME.player.y), (GAME.player.x + relativePosition[0], GAME.player.y + 1)]
class Spear(Weapon):
    def attackTargets(self, relativePosition): # TODO: Check if this is working as intended
        return [creature for creature in GAME.creatures if creature is not self and ((creature.x, creature.y) == (GAME.player.x, GAME.player.y) + relativePosition or (creature.x, creature.y) == (GAME.player.x, GAME.player.y) + relativePosition*2) and 'monster' in creature.tags]

class Potion:
    def __init__(self, name, sprite_list, actions, conditions, startCharges, maxCharges, description):
        self.name = name
        self.sprite_list = sprite_list
        self.actions = actions
        self.conditions = conditions
        self.charges = startCharges
        self.maxCharges = maxCharges
        self.description = description
    def drink(self):
        if self.charges > 0 and all([condition.execute() for condition in self.conditions]):
            for action in self.actions:
                action.execute()
            self.charges -= 1

class Spell:
    def __init__(self, name, description, sprite_list, effects, costs, cd):
        self.name = name
        self.description = description
        self.sprite_list = sprite_list
        self.effects = effects
        self.costs = costs
        self.cd = cd

class Component:
    def __init__(self, parent):
        self.parent = parent
class Skill:
    def __init__(self, index, pos, name, description, sprite, move, req, maxRank):
        self.index = index
        self.x , self.y = pos
        self.name = name
        self.description = description
        self.sprite = sprite
        self.move = move
        self.req = req
        self.maxRank = maxRank
        self.rank = 0
    def onBuy(self):
        if self.maxRank != -1:
            self.rank += 1
    def isMaxed(self):
        return self.rank == self.maxRank
    def isNotMaxed(self):
        return not self.isMaxed()
