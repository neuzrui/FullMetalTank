import os, pygame, random, uuid, math

class Timer(object):
    """ Timer class remains unchanged from the code base """

    def __init__(self):
        self.timers = []

    def add(self, interval, f, repeat = -1):
        options = {
            "interval"	: interval,
            "callback"	: f,
            "repeat"		: repeat,
            "times"			: 0,
            "time"			: 0,
            "uuid"			: uuid.uuid4()
        }
        self.timers.append(options)
        return options["uuid"]

    def destroy(self, uuid_nr):
        for timer in self.timers:
            if timer["uuid"] == uuid_nr:
                self.timers.remove(timer)
                return

    def update(self, time_passed):
        for timer in self.timers:
            timer["time"] += time_passed
            if timer["time"] > timer["interval"]:
                timer["time"] -= timer["interval"]
                timer["times"] += 1
                if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
                    self.timers.remove(timer)
                try:
                    timer["callback"]()
                except:
                    try:
                        self.timers.remove(timer)
                    except:
                        pass

class Castle():
    """
    Castle class remains unchanged from the code base
    Player's castle/fortress
    """

    (STATE_STANDING, STATE_DESTROYED, STATE_EXPLODING) = range(3)

    def __init__(self):
        global sprites
        # images
        self.img_undamaged = sprites.subsurface(0, 15*2, 16*2, 16*2)
        self.img_destroyed = sprites.subsurface(16*2, 15*2, 16*2, 16*2)

        # init position
        self.rect = pygame.Rect(12*16, 24*16, 32, 32)

        # start w/ undamaged and shiny castle
        self.rebuild()

    def draw(self):
        """ Draw castle """
        global screen
        screen.blit(self.image, self.rect.topleft)
        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.state = self.STATE_DESTROYED
                del self.explosion
            else:
                self.explosion.draw()

    def rebuild(self):
        """ Reset castle """
        self.state = self.STATE_STANDING
        self.image = self.img_undamaged
        self.active = True

    def destroy(self):
        """ Destroy castle """
        self.state = self.STATE_EXPLODING
        self.explosion = Explosion(self.rect.topleft)
        self.image = self.img_destroyed
        self.active = False



class Bonus():
    """
    Bonus class remains unchanged from the code base
    Various power-ups
    When bonus is spawned, it begins flashing and after some time dissapears
    Available bonusses:
        grenade	: Picking up the grenade power up instantly wipes out ever enemy presently on the screen, including Armor Tanks regardless of how many times you've hit them. You do not, however, get credit for destroying them during the end-stage bonus points.
        helmet	: The helmet power up grants you a temporary force field that makes you invulnerable to enemy shots, just like the one you begin every stage with.
        shovel	: The shovel power up turns the walls around your fortress from brick to stone. This makes it impossible for the enemy to penetrate the wall and destroy your fortress, ending the game prematurely. The effect, however, is only temporary, and will wear off eventually.
        star		: The star power up grants your tank with new offensive power each time you pick one up, up to three times. The first star allows you to fire your bullets as fast as the power tanks can. The second star allows you to fire up to two bullets on the screen at one time. And the third star allows your bullets to destroy the otherwise unbreakable steel walls. You carry this power with you to each new stage until you lose a life.
        tank		: The tank power up grants you one extra life. The only other way to get an extra life is to score 20000 points.
        timer		: The timer power up temporarily freezes time, allowing you to harmlessly approach every tank and destroy them until the time freeze wears off.
    """
    # bonus types
    (BONUS_GRENADE, BONUS_HELMET, BONUS_SHOVEL, BONUS_STAR, BONUS_TANK, BONUS_TIMER) = range(6)
    def __init__(self, level):
        global sprites
        # to know where to place
        self.level = level
        # bonus lives only for a limited period of time
        self.active = True
        # blinking state
        self.visible = True
        self.rect = pygame.Rect(random.randint(0, 416-32), random.randint(0, 416-32), 32, 32)
        self.bonus = random.choice([
            self.BONUS_GRENADE,
            self.BONUS_HELMET,
            self.BONUS_SHOVEL,
            self.BONUS_STAR,
            self.BONUS_TANK,
            self.BONUS_TIMER
        ])
        self.image = sprites.subsurface(16*2*self.bonus, 32*2, 16*2, 15*2)
    def draw(self):
        """ draw bonus """
        global screen
        if self.visible:
            screen.blit(self.image, self.rect.topleft)

    def toggleVisibility(self):
        """ Toggle bonus visibility """
        self.visible = not self.visible

class Bullet():
    """
    We did some modification to this class
    Added functions:
        def isDangerous(...)
        def nextMove(...)
    """

    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    # bullet's stated
    (STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)
    (OWNER_PLAYER, OWNER_ENEMY) = range(2)

    def __init__(self, level, position, direction, damage = 100, speed = 5):
        global sprites

        self.level = level
        self.direction = direction
        self.damage = damage
        self.owner = None
        self.owner_class = None

        # 1-regular everyday normal bullet
        # 2-can destroy steel
        self.power = 1

        self.image = sprites.subsurface(75*2, 74*2, 3*2, 4*2)

        # position is player's top left corner, so we'll need to
        # recalculate a bit. also rotate image itself.
        if direction == self.DIR_UP:
            self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
        elif direction == self.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.image, 270)
            self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
        elif direction == self.DIR_DOWN:
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
        elif direction == self.DIR_LEFT:
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = pygame.Rect(position[0] - 8 , position[1] + 11, 8, 6)

        self.explosion_images = [
            sprites.subsurface(0, 80*2, 32*2, 32*2),
            sprites.subsurface(32*2, 80*2, 32*2, 32*2),
            ]
        self.speed = speed
        self.state = self.STATE_ACTIVE

    def draw(self):
        """ draw bullet """
        global screen
        if self.state == self.STATE_ACTIVE:
            screen.blit(self.image, self.rect.topleft)
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()

    def update(self):
        global castle, players, enemies, bullets

        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.destroy()
                del self.explosion

        if self.state != self.STATE_ACTIVE:
            return

        """ move bullet """
        if self.direction == self.DIR_UP:
            self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
            if self.rect.top < 0:
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_RIGHT:
            self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
            if self.rect.left > (416 - self.rect.width):
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_DOWN:
            self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
            if self.rect.top > (416 - self.rect.height):
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_LEFT:
            self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
            if self.rect.left < 0:
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return

        has_collided = False

        # check for collisions with walls. one bullet can destroy several (1 or 2)
        # tiles but explosion remains 1
        rects = self.level.obstacle_rects
        collisions = self.rect.collidelistall(rects)
        if collisions != []:
            for i in collisions:
                if self.level.hitTile(rects[i].topleft, self.power, self.owner == self.OWNER_PLAYER):
                    has_collided = True
        if has_collided:
            self.explode()
            return

        # check for collisions with other bullets
        for bullet in bullets:
            if self.state == self.STATE_ACTIVE and bullet.owner != self.owner and bullet != self and self.rect.colliderect(bullet.rect):
                self.destroy()
                self.explode()
                return

        # check for collisions with players
        for player in players:
            if player.state == player.STATE_ALIVE and self.rect.colliderect(player.rect):
                if player.bulletImpact(self.owner == self.OWNER_PLAYER, self.damage, self.owner_class):
                    self.destroy()
                    return

        # check for collisions with enemies
        for enemy in enemies:
            if enemy.state == enemy.STATE_ALIVE and self.rect.colliderect(enemy.rect):
                if enemy.bulletImpact(self.owner == self.OWNER_ENEMY, self.damage, self.owner_class):
                    self.destroy()
                    return

        # check for collision with castle
        if castle.active and self.rect.colliderect(castle.rect):
            castle.destroy()
            self.destroy()
            return

    def explode(self):
        """ start bullets's explosion """
        global screen
        if self.state != self.STATE_REMOVED:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion([self.rect.left-13, self.rect.top-13], None, self.explosion_images)

    def destroy(self):
        self.state = self.STATE_REMOVED

    ##################################################
    # THE FOLLOWING FUNCTIONS ARE ADDED BY TEAM BETA #
    ##################################################

    def isDangerous(self, dangerousAreaRects):
        """
        This method returns true if the bullet itself is within the dangerous
        areas of the AI player tank and the bullet is moving towards the tank.
        Input: dangerous area rects of the AI player tank
        Out: boolean indicating the bullet itselft is dangerous or not
        """
        i = 0
        dangerous = False
        for area in dangerousAreaRects:
            in_area = self.rect.centerx in range(area.left, area.left + area.width)\
                    and self.rect.centery in range(area.top, area.top + area.height)
            # first dangerous area is the upper area of the AI
            if i == 0:
                dangerous = in_area and self.direction == self.DIR_DOWN
            # second dangerous area is the lower area of the AI
            elif i == 1:
                dangerous = in_area and self.direction == self.DIR_UP
            # third dangerous area is the left side area of the AI
            elif i == 2:
                dangerous = in_area and self.direction == self.DIR_RIGHT
            # fourth dangerous area is the right side area of the AI
            else:
                dangerous = in_area and self.direction == self.DIR_LEFT
            i += 1
        return dangerous

    def nextMove(self):
        """
        This method return the expected rect of the bullet.
        Input: none
        Output: the expected rect of the bullet if the bullet got moved
        """

        cur_x = self.rect.left
        cur_y = self.rect.top
        speedratio = 1
        if self.direction == self.DIR_UP:
            nextrect = pygame.Rect(cur_x, cur_y - self.speed * speedratio, 6, 8)
            if self.rect.top - self.speed < 0:
                return None
            return
        elif self.direction == self.DIR_RIGHT:
            nextrect = pygame.Rect(cur_x + self.speed * speedratio, cur_y, 6, 8)
            if self.rect.left > (416 - self.rect.width):
                return None
            return nextrect
        elif self.direction == self.DIR_DOWN:
            nextrect = pygame.Rect(cur_x, cur_y + self.speed * speedratio, 6, 8)
            if self.rect.top > (416 - self.rect.height):
                return None
            return nextrect
        elif self.direction == self.DIR_LEFT:
            nextrect = pygame.Rect(cur_x - self.speed * speedratio, cur_y, 6, 8)
            if self.rect.left < 0:
                return None
            return nextrect
        return None

class Label():
    """
    Label class remains unchanged from the code base
    """
    def __init__(self, position, text = "", duration = None):
        self.position = position
        self.active = True
        self.text = text
        self.font = pygame.font.SysFont("Arial", 13)
        if duration != None:
            gtimer.add(duration, lambda :self.destroy(), 1)

    def draw(self):
        """ draw label """
        global screen
        screen.blit(self.font.render(self.text, False, (200,200,200)), [self.position[0]+4, self.position[1]+8])

    def destroy(self):
        self.active = False


class Explosion():
    """
    Explosion class remains unchanged from the code base
    """
    def __init__(self, position, interval = None, images = None):
        global sprites
        self.position = [position[0]-16, position[1]-16]
        self.active = True
        if interval == None:
            interval = 100
        if images == None:
            images = [
                sprites.subsurface(0, 80*2, 32*2, 32*2),
                sprites.subsurface(32*2, 80*2, 32*2, 32*2),
                sprites.subsurface(64*2, 80*2, 32*2, 32*2)
            ]
        images.reverse()
        self.images = [] + images
        self.image = self.images.pop()
        gtimer.add(interval, lambda :self.update(), len(self.images) + 1)

    def draw(self):
        global screen
        """ draw current explosion frame """
        screen.blit(self.image, self.position)

    def update(self):
        """ Advace to the next image """
        if len(self.images) > 0:
            self.image = self.images.pop()
        else:
            self.active = False

class Level():
    """
    Level class remains unchanged from the code base
    """
    # tile constants
    (TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)
    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, level_nr = None):
        """ There are total 35 different levels. If level_nr is larger than 35, loop over
        to next according level so, for example, if level_nr ir 37, then load level 2 """
        global sprites
        # max number of enemies simultaneously  being on map
        self.max_active_enemies = 4
        tile_images = [
            pygame.Surface((8*2, 8*2)),
            sprites.subsurface(48*2, 64*2, 8*2, 8*2),
            sprites.subsurface(48*2, 72*2, 8*2, 8*2),
            sprites.subsurface(56*2, 72*2, 8*2, 8*2),
            sprites.subsurface(64*2, 64*2, 8*2, 8*2),
            sprites.subsurface(64*2, 64*2, 8*2, 8*2),
            sprites.subsurface(72*2, 64*2, 8*2, 8*2),
            sprites.subsurface(64*2, 72*2, 8*2, 8*2)
        ]
        self.tile_empty = tile_images[0]
        self.tile_brick = tile_images[1]
        self.tile_steel = tile_images[2]
        self.tile_grass = tile_images[3]
        self.tile_water = tile_images[4]
        self.tile_water1= tile_images[4]
        self.tile_water2= tile_images[5]
        self.tile_froze = tile_images[6]

        level_nr = 1 if level_nr == None else level_nr%10
        if level_nr == 0:
            level_nr = 10

        self.loadLevel(level_nr)

        # tiles' rects on map, tanks cannot move over
        self.obstacle_rects = []
        self.impenetrable_obstacle_rects = []

        # update these tiles
        self.updateObstacleRects()
        gtimer.add(400, lambda :self.toggleWaves())

    def hitTile(self, pos, power = 1, sound = False):
        """
            Hit the tile
            @param pos Tile's x, y in px
            @return True if bullet was stopped, False otherwise
        """
        global play_sounds, sounds
        for tile in self.mapr:
            if tile[1].topleft == pos:
                if tile[0] == self.TILE_BRICK:
                    if play_sounds and sound:
                        sounds["brick"].play()
                    self.mapr.remove(tile)
                    self.updateObstacleRects()
                    return True
                elif tile[0] == self.TILE_STEEL:
                    if play_sounds and sound:
                        sounds["steel"].play()
                    if power == 2:
                        self.mapr.remove(tile)
                        self.updateObstacleRects()
                    return True
                else:
                    return False

    def toggleWaves(self):
        """ Toggle water image """
        if self.tile_water == self.tile_water1:
            self.tile_water = self.tile_water2
        else:
            self.tile_water = self.tile_water1

    def loadLevel(self, level_nr = 1):
        """ Load specified level
        @return boolean Whether level was loaded
        """
        filename = "levels/"+str(level_nr)
        if (not os.path.isfile(filename)):
            return False
        level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.mapr.append((self.TILE_BRICK, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "@":
                    self.mapr.append((self.TILE_STEEL, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "~":
                    self.mapr.append((self.TILE_WATER, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "%":
                    self.mapr.append((self.TILE_GRASS, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "-":
                    self.mapr.append((self.TILE_FROZE, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                x += self.TILE_SIZE
            x = 0
            y += self.TILE_SIZE
        return True


    def draw(self, tiles = None):
        """ Draw specified map on top of existing surface """
        global screen
        if tiles == None:
            tiles = [TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE]

        for tile in self.mapr:
            if tile[0] in tiles:
                if tile[0] == self.TILE_BRICK:
                    screen.blit(self.tile_brick, tile[1].topleft)
                elif tile[0] == self.TILE_STEEL:
                    screen.blit(self.tile_steel, tile[1].topleft)
                elif tile[0] == self.TILE_WATER:
                    screen.blit(self.tile_water, tile[1].topleft)
                elif tile[0] == self.TILE_FROZE:
                    screen.blit(self.tile_froze, tile[1].topleft)
                elif tile[0] == self.TILE_GRASS:
                    screen.blit(self.tile_grass, tile[1].topleft)

    def updateObstacleRects(self):
        """ Set self.obstacle_rects to all tiles' rects that players can destroy
        with bullets """
        global castle
        self.obstacle_rects = [castle.rect]
        self.impenetrable_obstacle_rects = [castle.rect]

        for tile in self.mapr:
            if tile[0] in (self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER):
                self.obstacle_rects.append(tile[1])
                if tile[0] is not self.TILE_WATER:
                    self.impenetrable_obstacle_rects.append(tile[1])

    def buildFortress(self, tile):
        """ Build walls around castle made from tile """
        positions = [
            (11*self.TILE_SIZE, 23*self.TILE_SIZE),
            (11*self.TILE_SIZE, 24*self.TILE_SIZE),
            (11*self.TILE_SIZE, 25*self.TILE_SIZE),
            (14*self.TILE_SIZE, 23*self.TILE_SIZE),
            (14*self.TILE_SIZE, 24*self.TILE_SIZE),
            (14*self.TILE_SIZE, 25*self.TILE_SIZE),
            (12*self.TILE_SIZE, 23*self.TILE_SIZE),
            (13*self.TILE_SIZE, 23*self.TILE_SIZE)
        ]
        obsolete = []
        for i, rect in enumerate(self.mapr):
            if rect[1].topleft in positions:
                obsolete.append(rect)
        for rect in obsolete:
            self.mapr.remove(rect)

        for pos in positions:
            self.mapr.append((tile, pygame.Rect(pos, [self.TILE_SIZE, self.TILE_SIZE])))

        self.updateObstacleRects()

class Tank():
    """
    We did some modification to this class
    Added functions:
        def getManhattanDistance(...)
        def isOverlapping(...)
    """

    # possible directions
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    # states
    (STATE_SPAWNING, STATE_DEAD, STATE_ALIVE, STATE_EXPLODING) = range(4)
    # sides
    (SIDE_PLAYER, SIDE_ENEMY) = range(2)

    def __init__(self, level, side, position = None, direction = None, filename = None):

        global sprites

        # health. 0 health means dead
        self.health = 100

        # tank can't move but can rotate and shoot
        self.paralised = False

        # tank can't do anything
        self.paused = False

        # tank is protected from bullets
        self.shielded = False

        # px per move
        self.speed = 2

        # how many bullets can tank fire simultaneously
        self.max_active_bullets = 1

        # friend or foe
        self.side = side

        # flashing state. 0-off, 1-on
        self.flash = 0

        # 0 - no superpowers
        # 1 - faster bullets
        # 2 - can fire 2 bullets
        # 3 - can destroy steel
        self.superpowers = 0

        # each tank can pick up 1 bonus
        self.bonus = None

        # navigation keys: fire, up, right, down, left
        self.controls = [pygame.K_SPACE, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

        # currently pressed buttons (navigation only)
        self.pressed = [False] * 4

        self.shield_images = [
            sprites.subsurface(0, 48*2, 16*2, 16*2),
            sprites.subsurface(16*2, 48*2, 16*2, 16*2)
        ]
        self.shield_image = self.shield_images[0]
        self.shield_index = 0

        self.spawn_images = [
            sprites.subsurface(32*2, 48*2, 16*2, 16*2),
            sprites.subsurface(48*2, 48*2, 16*2, 16*2)
        ]
        self.spawn_image = self.spawn_images[0]
        self.spawn_index = 0

        self.level = level

        if position != None:
            self.rect = pygame.Rect(position, (26, 26))
        else:
            self.rect = pygame.Rect(0, 0, 26, 26)

        if direction == None:
            self.direction = random.choice([self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT])
        else:
            self.direction = direction

        self.state = self.STATE_SPAWNING

        # spawning animation
        self.timer_uuid_spawn = gtimer.add(100, lambda :self.toggleSpawnImage())

        # duration of spawning
        self.timer_uuid_spawn_end = gtimer.add(1000, lambda :self.endSpawning())

    def endSpawning(self):
        """ End spawning
        Player becomes operational
        """
        self.state = self.STATE_ALIVE
        gtimer.destroy(self.timer_uuid_spawn_end)


    def toggleSpawnImage(self):
        """ advance to the next spawn image """
        if self.state != self.STATE_SPAWNING:
            gtimer.destroy(self.timer_uuid_spawn)
            return
        self.spawn_index += 1
        if self.spawn_index >= len(self.spawn_images):
            self.spawn_index = 0
        self.spawn_image = self.spawn_images[self.spawn_index]

    def toggleShieldImage(self):
        """ advance to the next shield image """
        if self.state != self.STATE_ALIVE:
            gtimer.destroy(self.timer_uuid_shield)
            return
        if self.shielded:
            self.shield_index += 1
            if self.shield_index >= len(self.shield_images):
                self.shield_index = 0
            self.shield_image = self.shield_images[self.shield_index]


    def draw(self):
        """ draw tank """
        global screen
        if self.state == self.STATE_ALIVE:
            screen.blit(self.image, self.rect.topleft)
            if self.shielded:
                screen.blit(self.shield_image, [self.rect.left-3, self.rect.top-3])
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()
        elif self.state == self.STATE_SPAWNING:
            screen.blit(self.spawn_image, self.rect.topleft)

    def explode(self):
        """ start tanks's explosion """
        if self.state != self.STATE_DEAD:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion(self.rect.topleft)

            if self.bonus:
                self.spawnBonus()

    def fire(self, forced = False):
        """ Shoot a bullet
        @param boolean forced. If false, check whether tank has exceeded his bullet quota. Default: True
        @return boolean True if bullet was fired, false otherwise
        """
        global bullets, labels

        if self.state != self.STATE_ALIVE:
            gtimer.destroy(self.timer_uuid_fire)
            return False

        if self.paused:
            return False

        if not forced:
            active_bullets = 0
            for bullet in bullets:
                if bullet.owner_class == self and bullet.state == bullet.STATE_ACTIVE:
                    active_bullets += 1
            if active_bullets >= self.max_active_bullets:
                return False

        bullet = Bullet(self.level, self.rect.topleft, self.direction)

        # if superpower level is at least 1
        if self.superpowers > 0:
            bullet.speed = 8

        # if superpower level is at least 3
        if self.superpowers > 2:
            bullet.power = 2

        if self.side == self.SIDE_PLAYER:
            bullet.owner = self.SIDE_PLAYER
        else:
            bullet.owner = self.SIDE_ENEMY
            self.bullet_queued = False

        bullet.owner_class = self
        bullets.append(bullet)
        return True

    def rotate(self, direction, fix_position = True):
        """ Rotate tank
        rotate, update image and correct position
        """
        self.direction = direction

        if direction == self.DIR_UP:
            self.image = self.image_up
        elif direction == self.DIR_RIGHT:
            self.image = self.image_right
        elif direction == self.DIR_DOWN:
            self.image = self.image_down
        elif direction == self.DIR_LEFT:
            self.image = self.image_left

        if fix_position:
            new_x = self.nearest(self.rect.left, 8) + 3
            new_y = self.nearest(self.rect.top, 8) + 3

            if (abs(self.rect.left - new_x) < 5):
                self.rect.left = new_x

            if (abs(self.rect.top - new_y) < 5):
                self.rect.top = new_y

    def turnAround(self):
        """ Turn tank into opposite direction """
        if self.direction in (self.DIR_UP, self.DIR_RIGHT):
            self.rotate(self.direction + 2, False)
        else:
            self.rotate(self.direction - 2, False)

    def update(self, time_passed):
        """ Update timer and explosion (if any) """
        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.state = self.STATE_DEAD
                del self.explosion

    def nearest(self, num, base):
        """ Round number to nearest divisible """
        return int(round(num / (base * 1.0)) * base)


    def bulletImpact(self, friendly_fire = False, damage = 100, tank = None):
        """ Bullet impact
        Return True if bullet should be destroyed on impact. Only enemy friendly-fire
        doesn't trigger bullet explosion
        """

        global play_sounds, sounds

        if self.shielded:
            return True

        if not friendly_fire:
            self.health -= damage
            if self.health < 1:
                if self.side == self.SIDE_ENEMY:
                    tank.trophies["enemy"+str(self.type)] += 1
                    points = (self.type+1) * 100
                    tank.score += points
                    if play_sounds:
                        sounds["explosion"].play()

                    labels.append(Label(self.rect.topleft, str(points), 500))

                self.explode()
            return True

        if self.side == self.SIDE_ENEMY:
            return False
        elif self.side == self.SIDE_PLAYER:
            if not self.paralised:
                self.setParalised(True)
                self.timer_uuid_paralise = gtimer.add(10000, lambda :self.setParalised(False), 1)
            return True

    def setParalised(self, paralised = True):
        """ set tank paralise state
        @param boolean paralised
        @return None
        """
        if self.state != self.STATE_ALIVE:
            gtimer.destroy(self.timer_uuid_paralise)
            return
        self.paralised = paralised

    ##################################################
    # THE FOLLOWING FUNCTIONS ARE ADDED BY TEAM BETA #
    ##################################################
    def getManhattanDistance(self, target):
        """
        This method returns the Manhattan Distance from the given target tank
        to the tank object who calls this method
        Input: a target tank object
        Output: the  Manhattan Distance between the target and self
        """
        x = self.rect.center[0]
        y = self.rect.center[1]
        target_x = target.rect.center[0]
        target_y = target.rect.center[1]
        return abs(target_x - x) + abs(target_y - y)

    @staticmethod
    def isOverlapping(tank_rect1, tank_rect2):
        """
        This method returns true if the given two rects of the tanks are
        overlapping with each other
        Input: two rects of the tanks
        Output: a boolean indicates whether the given two rects overlaps or not
        """
        tank1_centerx = tank_rect1.centerx
        tank1_centery = tank_rect1.centery
        tank2_centerx = tank_rect2.centerx
        tank2_centery = tank_rect2.centery
        if abs(tank1_centerx - tank2_centerx) < tank_rect1.width \
                and abs(tank1_centery - tank2_centery) < tank_rect1.height:
            return True
        else:
            return False


class Enemy(Tank):
    """
    We did some modification to this class
    Added functions:
        def isNearBase(...)
        def getNextRect(...)
        def checkPos(..)
        def getDistance(...)
        def getAttackPosition(...)
    """
    (TYPE_BASIC, TYPE_FAST, TYPE_POWER, TYPE_ARMOR) = range(4)

    def __init__(self, level, type, position = None, direction = None, filename = None):
        Tank.__init__(self, level, type, position = None, direction = None, filename = None)

        global enemies, sprites

        # if true, do not fire
        self.bullet_queued = False

        # chose type on random
        if len(level.enemies_left) > 0:
            self.type = level.enemies_left.pop()
        else:
            self.state = self.STATE_DEAD
            return

        if self.type == self.TYPE_BASIC:
            self.speed = 1
        elif self.type == self.TYPE_FAST:
            self.speed = 1
        elif self.type == self.TYPE_POWER:
            self.superpowers = 1
        elif self.type == self.TYPE_ARMOR:
            self.health = 400

        # 1 in 5 chance this will be bonus carrier, but only if no other tank is
        if random.randint(1, 5) == 1:
            self.bonus = True
            for enemy in enemies:
                if enemy.bonus:
                    self.bonus = False
                    break

        images = [
            sprites.subsurface(32*2, 0, 13*2, 15*2),
            sprites.subsurface(48*2, 0, 13*2, 15*2),
            sprites.subsurface(64*2, 0, 13*2, 15*2),
            sprites.subsurface(80*2, 0, 13*2, 15*2),
            sprites.subsurface(32*2, 16*2, 13*2, 15*2),
            sprites.subsurface(48*2, 16*2, 13*2, 15*2),
            sprites.subsurface(64*2, 16*2, 13*2, 15*2),
            sprites.subsurface(80*2, 16*2, 13*2, 15*2)
        ]

        self.image = images[self.type+0]

        self.image_up = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        if self.bonus:
            self.image1_up = self.image_up
            self.image1_left = self.image_left
            self.image1_down = self.image_down
            self.image1_right = self.image_right

            self.image2 = images[self.type+4]
            self.image2_up = self.image2;
            self.image2_left = pygame.transform.rotate(self.image2, 90)
            self.image2_down = pygame.transform.rotate(self.image2, 180)
            self.image2_right = pygame.transform.rotate(self.image2, 270)

        self.rotate(self.direction, None)

        if position == None:
            self.rect.topleft = self.getFreeSpawningPosition()
            if not self.rect.topleft:
                self.state = self.STATE_DEAD
                return

        # list of map coords where tank should go next
        self.path = self.generatePath(self.direction)

        # 1000 is duration between shots
        self.timer_uuid_fire = gtimer.add(1000, lambda :self.fire())

        # turn on flashing
        if self.bonus:
            self.timer_uuid_flash = gtimer.add(200, lambda :self.toggleFlash())

    def toggleFlash(self):
        """ Toggle flash state """
        if self.state not in (self.STATE_ALIVE, self.STATE_SPAWNING):
            gtimer.destroy(self.timer_uuid_flash)
            return
        self.flash = not self.flash
        if self.flash:
            self.image_up = self.image2_up
            self.image_right = self.image2_right
            self.image_down = self.image2_down
            self.image_left = self.image2_left
        else:
            self.image_up = self.image1_up
            self.image_right = self.image1_right
            self.image_down = self.image1_down
            self.image_left = self.image1_left
        self.rotate(self.direction, False)

    def spawnBonus(self):
        """ Create new bonus if needed """

        global bonuses

        if len(bonuses) > 0:
            return
        bonus = Bonus(self.level)
        bonuses.append(bonus)
        gtimer.add(500, lambda :bonus.toggleVisibility())
        gtimer.add(10000, lambda :bonuses.remove(bonus), 1)


    def getFreeSpawningPosition(self):

        global players, enemies

        available_positions = [
            [(self.level.TILE_SIZE * 2 - self.rect.width) / 2, (self.level.TILE_SIZE * 2 - self.rect.height) / 2],
            [12 * self.level.TILE_SIZE + (self.level.TILE_SIZE * 2 - self.rect.width) / 2, (self.level.TILE_SIZE * 2 - self.rect.height) / 2],
            [24 * self.level.TILE_SIZE + (self.level.TILE_SIZE * 2 - self.rect.width) / 2,  (self.level.TILE_SIZE * 2 - self.rect.height) / 2]
        ]

        random.shuffle(available_positions)

        for pos in available_positions:

            enemy_rect = pygame.Rect(pos, [26, 26])

            # collisions with other enemies
            collision = False
            for enemy in enemies:
                if enemy_rect.colliderect(enemy.rect):
                    collision = True
                    continue

            if collision:
                continue

            # collisions with players
            collision = False
            for player in players:
                if enemy_rect.colliderect(player.rect):
                    collision = True
                    continue

            if collision:
                continue

            return pos
        return False

    def move(self):
        """ move enemy if possible """

        global players, enemies, bonuses

        if self.state != self.STATE_ALIVE or self.paused or self.paralised:
            return

        if self.path == []:
            self.path = self.generatePath(None, True)

        new_position = self.path.pop(0)

        # move enemy
        if self.direction == self.DIR_UP:
            if new_position[1] < 0:
                self.path = self.generatePath(self.direction, True)
                return
        elif self.direction == self.DIR_RIGHT:
            if new_position[0] > (416 - 26):
                self.path = self.generatePath(self.direction, True)
                return
        elif self.direction == self.DIR_DOWN:
            if new_position[1] > (416 - 26):
                self.path = self.generatePath(self.direction, True)
                return
        elif self.direction == self.DIR_LEFT:
            if new_position[0] < 0:
                self.path = self.generatePath(self.direction, True)
                return

        new_rect = pygame.Rect(new_position, [26, 26])

        # collisions with tiles
        if new_rect.collidelist(self.level.obstacle_rects) != -1:
            self.path = self.generatePath(self.direction, True)
            return

        # collisions with other enemies
        for enemy in enemies:
            if enemy != self and new_rect.colliderect(enemy.rect):
                self.turnAround()
                self.path = self.generatePath(self.direction)
                return

        # collisions with players
        for player in players:
            if new_rect.colliderect(player.rect):
                self.turnAround()
                self.path = self.generatePath(self.direction)
                return

        # collisions with bonuses
        for bonus in bonuses:
            if new_rect.colliderect(bonus.rect):
                bonuses.remove(bonus)

        # if no collision, move enemy
        self.rect.topleft = new_rect.topleft


    def update(self, time_passed):
        Tank.update(self, time_passed)
        if self.state == self.STATE_ALIVE and not self.paused:
            self.move()

    def generatePath(self, direction = None, fix_direction = False):
        """ If direction is specified, try continue that way, otherwise choose at random
        """

        all_directions = [self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT]

        if direction == None:
            if self.direction in [self.DIR_UP, self.DIR_RIGHT]:
                opposite_direction = self.direction + 2
            else:
                opposite_direction = self.direction - 2
            directions = all_directions
            random.shuffle(directions)
            directions.remove(opposite_direction)
            directions.append(opposite_direction)
        else:
            if direction in [self.DIR_UP, self.DIR_RIGHT]:
                opposite_direction = direction + 2
            else:
                opposite_direction = direction - 2

            if direction in [self.DIR_UP, self.DIR_RIGHT]:
                opposite_direction = direction + 2
            else:
                opposite_direction = direction - 2
            directions = all_directions
            random.shuffle(directions)
            directions.remove(opposite_direction)
            directions.remove(direction)
            directions.insert(0, direction)
            directions.append(opposite_direction)

        # at first, work with general units (steps) not px
        x = int(round(self.rect.left / 16))
        y = int(round(self.rect.top / 16))

        new_direction = None

        for direction in directions:
            if direction == self.DIR_UP and y > 1:
                new_pos_rect = self.rect.move(0, -8)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == self.DIR_RIGHT and x < 24:
                new_pos_rect = self.rect.move(8, 0)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == self.DIR_DOWN and y < 24:
                new_pos_rect = self.rect.move(0, 8)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == self.DIR_LEFT and x > 1:
                new_pos_rect = self.rect.move(-8, 0)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break

        # if we can go anywhere else, turn around
        if new_direction == None:
            new_direction = opposite_direction
            print "nav izejas. griezhamies"

        # fix tanks position
        if fix_direction and new_direction == self.direction:
            fix_direction = False

        self.rotate(new_direction, fix_direction)

        positions = []

        x = self.rect.left
        y = self.rect.top

        if new_direction in (self.DIR_RIGHT, self.DIR_LEFT):
            axis_fix = self.nearest(y, 16) - y
        else:
            axis_fix = self.nearest(x, 16) - x
        axis_fix = 0

        pixels = self.nearest(random.randint(1, 12) * 32, 32) + axis_fix + 3

        if new_direction == self.DIR_UP:
            for px in range(0, pixels, self.speed):
                positions.append([x, y-px])
        elif new_direction == self.DIR_RIGHT:
            for px in range(0, pixels, self.speed):
                positions.append([x+px, y])
        elif new_direction == self.DIR_DOWN:
            for px in range(0, pixels, self.speed):
                positions.append([x, y+px])
        elif new_direction == self.DIR_LEFT:
            for px in range(0, pixels, self.speed):
                positions.append([x-px, y])
        return positions


    ##################################################
    # THE FOLLOWING FUNCTIONS ARE ADDED BY TEAM BETA #
    ##################################################
    def isNearBase(self):
        """
        returns True if the enemy is near the base
        """
        base_rect = pygame.Rect((1,195), (388, 194))
        if self.rect.colliderect(base_rect):
            return True
        return False

    def isDangerous(self, dangerousAreaRects):
        """
        returns True if the enemy is within the dangerous araes of the AI
        """
        for area in dangerousAreaRects:
            return self.rect.centerx in range(area.left, area.left + area.width) \
                and self.rect.centery in range(area.top, area.top + area.height)
        return False

    def getNextRect(self):
        """
        returns the expected rect of the enemy
        """
        return pygame.Rect((self.rect.left + self.speed, self.rect.top + self.speed),
                           (self.rect.width, self.rect.height))

    def checkPos(self, pos):
        """ check pos availability"""
        global players, enemies, bonuses
        current_rect = pygame.Rect(pos, [26, 26])

        # collisions with tiles
        if current_rect.collidelist(self.level.obstacle_rects) != -1:
            return False
        return True

    def getDistance(self, posOne, posTwo):
        """
        return the distance of the given two position
        """
        return math.pow(abs(posOne[0]-posTwo[0]), 2)+math.pow(abs(posOne[1]-posTwo[1]), 2)

    def getAttackPosition(self, player):
        """
        return the  position where the AI is able to attack the enemy
        if there are multiple position attackable, return the nearest one
        """
        playerX = player.rect.topleft[0]
        playerY = player.rect.topleft[1]
        cur_x = self.rect.topleft[0]
        cur_y = self.rect.topleft[1]
        playerTuple = (playerX, playerY)
        nearest = (cur_x, cur_y)
        distance = self.getDistance(playerTuple, nearest)
        #up
        new_pos_up = (cur_x, cur_y-1)

        while(new_pos_up[1] >= 0 and self.checkPos(new_pos_up)):
            new_dis = self.getDistance(new_pos_up, playerTuple)
            if( new_dis < distance):
                nearest = new_pos_up
                distance = new_dis
            new_pos_up = (new_pos_up[0], new_pos_up[1]-1)

        #right
        new_pos_right = (cur_x+1, cur_y)
        while(new_pos_right[0] <= (416 - 26) and self.checkPos(new_pos_right)):
            new_dis = self.getDistance(new_pos_right, playerTuple)
            if(new_dis < distance):
                nearest = new_pos_right
                distance = new_dis
            new_pos_right = (new_pos_right[0]+1, new_pos_right[1])

        #down
        new_pos_down = (cur_x, cur_y+1)
        while(new_pos_down[1] <= (416 - 26) and self.checkPos(new_pos_down)):
            new_dis = self.getDistance(new_pos_down, playerTuple)
            if(new_dis < distance):
                nearest = new_pos_down
                distance = new_dis
            new_pos_down = (new_pos_down[0], new_pos_down[1]+1)

        #left
        new_pos_left = (cur_x-1, cur_y)
        while(new_pos_left[0] >= 0 and self.checkPos(new_pos_left)):
            new_dis = self.getDistance(new_pos_left, playerTuple)
            if(new_dis < distance):
                nearest = new_pos_left
                distance = new_dis
            new_pos_left = (new_pos_left[0]-1, new_pos_left[1])

        return nearest


class Player(Tank):
    """
    We did some modification to this class
    Addes attributes:
        self.dangerousAreas
        self.visited
        self.map
        self.target_enemy

    We'd modified all the functions in this class in order to
    enable the player play the game intelligently as a AI agent

    We also added all the functions we need to implement our hybrid
    algorithm
    """

    def __init__(self, level, type, position = None, direction = None, filename = None):

        Tank.__init__(self, level, type, position = None, direction = None, filename = None)

        global sprites

        self.dangerousAreas = self.getDangerousAreas()

        self.visited = set([])
        # map info, point -> obstacle value
        self.map = []

        if filename == None:
            filename = (0, 0, 16*2, 16*2)

        self.start_position = position
        self.start_direction = direction

        self.lives = 3

        # total score
        self.score = 0

        # store how many bonuses in this stage this player has collected
        self.trophies = {
            "bonus" : 0,
            "enemy0" : 0,
            "enemy1" : 0,
            "enemy2" : 0,
            "enemy3" : 0
        }

        self.image = sprites.subsurface(filename)
        self.image_up = self.image;
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        if direction == None:
            self.rotate(self.DIR_UP, False)
        else:
            self.rotate(direction, False)

        self.target_enemy = None

    def getDangerousAreas(self):
        """
        Get the rects of the dangerous area of the AI player
        Dangerous areas are the areas of the 4 directions
        """
        dangerous_rects = []

        # AI upper area
        player_upper_rect_y = 0
        player_upper_rect_height = abs(self.rect.top - player_upper_rect_y)
        # AI lower area
        player_lower_rect_y = self.rect.bottom
        player_lower_rect_height = abs(416 - player_lower_rect_y)
        # AI left area
        player_left_rect_x = 0
        player_left_rect_width = abs(self.rect.left - player_left_rect_x)
        # AI right area
        player_right_rect_x = self.rect.right
        player_right_rect_width = abs(416 - player_right_rect_x)

        for obstacle in self.level.impenetrable_obstacle_rects:
            # obstacle is vertically inline with player
            if obstacle.centerx in range(self.rect.left, self.rect.right):
                #  obstacle above player
                if obstacle.centery < self.rect.centery:
                    if obstacle.bottom > player_upper_rect_y:
                        player_upper_rect_y = obstacle.bottom
                        player_upper_rect_height = abs(obstacle.bottom - self.rect.top)
                #  obstacle under player
                else:
                    if abs(obstacle.top - self.rect.bottom) < player_lower_rect_height:
                        player_lower_rect_height = abs(obstacle.top - self.rect.bottom)

            if obstacle.centery in range(self.rect.top, self.rect.bottom):
                # obstacle on player left
                if obstacle.centerx < self.rect.centerx:
                    if obstacle.right > player_left_rect_x:
                        player_left_rect_x = obstacle.right
                        player_left_rect_width = abs(obstacle.right - self.rect.left)
                # obstacle on player right
                else:
                    if abs(obstacle.left - self.rect.right) < player_right_rect_width:
                        player_right_rect_width = abs(obstacle.left - self.rect.right)

        # four direction dangerous area
        # up
        dangerous_rects.append(pygame.Rect((self.rect.left, player_upper_rect_y), (self.rect.width, player_upper_rect_height)))
        # down
        dangerous_rects.append(pygame.Rect((self.rect.left, self.rect.bottom), (self.rect.width, player_lower_rect_height)))
        # left
        dangerous_rects.append(pygame.Rect((player_left_rect_x, self.rect.top), (player_left_rect_width, self.rect.height)))
        # right
        dangerous_rects.append(pygame.Rect((self.rect.right, self.rect.top), (player_right_rect_width, self.rect.height)))
        return dangerous_rects

    def getMDistance(self, posOne, posTwo):
        """
        Get Manhattan distance of given two position
        """
        return abs(posOne[0]-posTwo[0]) + abs(posOne[1]-posTwo[1])

    def killDangerousTarget(self):
        """
        Contorl the AI to kill the dangerous bullets and enemies
        """
        self.dangerousAreas = self.getDangerousAreas()
        global enemies, bullets
        # sort the enemies and bullets
        sorted_enemies = sorted(enemies, key = lambda e : Tank.getManhattanDistance(self, e))
        sorted_bullets = sorted(bullets, key = lambda b : Tank.getManhattanDistance(self, b))

        # handle bullets first because they are more dangerous
        for bullet in sorted_bullets:
            if bullet.isDangerous(self.dangerousAreas):
                print "dangerous bullet found!!!!"
                self.aimAndFire(bullet.rect)

        # handle the enemies then
        for enemy in sorted_enemies:
            if enemy.state == enemy.STATE_ALIVE:
                if enemy.rect.colliderect(self.rect):
                    self.aimAndFire(enemy.rect)
                    enemy.bulletImpact(damage=400, tank=self)
                if enemy.isDangerous(self.dangerousAreas):
                    print "kill dangerous enemy found!!!!"
                    self.aimAndFire(enemy.rect)
            else:
                pass

    def playerMove(self, next_position, path):
        """
        Contorl the AI to move to the given position
        """
        if self.state != Tank.STATE_ALIVE:
            return
        # kill dangerous target before we do anything
        self.killDangerousTarget()

        # rotate tank if we need
        new_direction = self.direction
        if next_position[0] - self.rect.left == self.speed:
            new_direction = Tank.DIR_RIGHT
        elif next_position[0] - self.rect.left == -self.speed:
            new_direction = Tank.DIR_LEFT
        elif next_position[1] - self.rect.top == self.speed:
            new_direction = Tank.DIR_DOWN
        elif next_position[1] - self.rect.top == -self.speed:
            new_direction = Tank.DIR_UP
        self.rotate(new_direction)

        global enemies, bullets
        player_next_rect = pygame.Rect(next_position, (self.rect.width, self.rect.height))
        for enemy in enemies:
            if enemy.state == enemy.STATE_ALIVE:
                # if enemy is going to overlap with the player
                enemy_next_rect = enemy.getNextRect()
                if player_next_rect.colliderect(enemy_next_rect):
                    self.aimAndFire(enemy_next_rect)
            else:
                pass

        # if our AI gonna hit enemies' bullets, do something
        standby = False
        for bullet in bullets:
            if bullet.state == bullet.STATE_ACTIVE:
                will_hit = self.whetherGonnaHit(path, bullet)
                standby = standby or will_hit
        if standby:
            # standby and kill dangerous targets
            print "stop!!!"
            self.killDangerousTarget()
            return

        next_pos = path.pop(0)
        self.rect.topleft = next_pos
        self.visited.add(next_pos)

        # if our AI hit the bonuses, enable bonuses
        global bonuses
        # collisions with bonuses
        for bonus in bonuses:
            if self.rect.colliderect(bonus.rect):
                self.bonus = bonus

    def whetherGonnaHit(self, path, bullet):
        """
        returns True if the given bullet will hit our AI if our AI
        moves according to the path
        """
        bulletrect = bullet.rect
        for pos in path:
            player_next_rect = pygame.Rect(pos, [26, 26])
            if bulletrect is None:
                return False
            if player_next_rect.colliderect(bulletrect):
                return True
            bulletrect = self.nextMove(bulletrect.topleft, bullet);
        return False

    def nextMove(self, bulletPos, bullet):
        """
        returns the expected rect of the given bullet
        """
        cur_x = bulletPos[0]
        cur_y = bulletPos[1]
        bulletRect = pygame.Rect(cur_x, cur_y, 6, 8)
        speedratio = 1
        if bullet.direction == bullet.DIR_UP:
            nextrect = pygame.Rect(cur_x, cur_y - bullet.speed * speedratio, 6, 8)
            if bulletRect.top - bullet.speed < 0:
                return None
            return nextrect
        elif bullet.direction == bullet.DIR_RIGHT:
            nextrect = pygame.Rect(cur_x + bullet.speed * speedratio, cur_y, 6, 8)
            if bulletRect.left > (416 - bulletRect.width):
                return None
            return nextrect
        elif bullet.direction == bullet.DIR_DOWN:
            nextrect = pygame.Rect(cur_x, cur_y + bullet.speed * speedratio, 6, 8)
            if bulletRect.top > (416 - bulletRect.height):
                return None
            return nextrect
        elif bullet.direction == bullet.DIR_LEFT:
            nextrect = pygame.Rect(cur_x - bullet.speed * speedratio, cur_y, 6, 8)
            if bulletRect.left < 0:
                return None
            return nextrect
        return None

    def goToAttackPosition(self, position):
        """
        generate the path to the attack position
        """
        next_pos = self.getPath(position)
        if next_pos is None or next_pos in self.visited:
            path = self.aStar(position)
            return path
        path = []
        path.append(next_pos)
        return path

    def getPath(self, position):
        """
        returns the next position which is closest to the goal
        """
        cur_x = self.rect.topleft[0]
        cur_y = self.rect.topleft[1]
        around = self.getAroundAvailablePosition((cur_x, cur_y))
        max_distance = 2 * 26 * 16
        result = None

        for pos in around:
            dis = abs(pos[0] - position[0]) + abs(pos[1] - position[1])
            if dis < max_distance:
                max_distance = dis
                result = pos

        return result

    def getPathBFS(self, position):
        """
        This method is not used in our final version,
        but it was implemented before A*
        We found A* is better than BFS. Leave it here for future reference
        """
        print "bfs called"
        visit_cal = set([])
        cur_x = self.rect.topleft[0]
        cur_y = self.rect.topleft[1]
        roads = [[(cur_x, cur_y)]]
        visit_cal.add((cur_x, cur_y))

        while roads != []:
            new_roads = []
            for path in roads:
                last = path[-1]
                around = self.getAroundAvailablePosition(last)
                for pos in around:
                    if (abs(pos[0] - position[0]) + abs(pos[1] - position[1])) <= 2:
                        path.append(position)
                        return path
                    if pos in visit_cal:
                        continue
                    visit_cal.add(pos)
                    new_path = list(path)
                    new_path.append(pos)
                    new_roads.append(new_path)
            roads = new_roads
        return roads

    def aStar(self, target):
        """
        A* algorithm to find a optimal path to the target
        """
        print "a star called!!!!!!!! targer: x", target[0], " y:",target[1]

        cur_x = self.rect.topleft[0]
        cur_y = self.rect.topleft[1]
        current = Tile(cur_x, cur_y)
        end = Tile(target[0], target[1])

        openList = {}
        closedList = {}
        path = []

        openList[(current.x, current.y)] = current
        while len(openList) is not 0:
            current = min(openList.itervalues(), key=lambda inst:inst.H)
            if abs(current.x - end.x) <= self.speed - 1 and abs(current.y - end.y) <= self.speed - 1:
                self.retracePath(current, path)
                return path

            openList.pop((current.x, current.y))
            closedList[(current.x, current.y)] = current

            x = current.x
            y = current.y

            around = self.getAroundAvailablePosition((x, y))
            for pos in around:
                tile = Tile(pos[0], pos[1])
                if pos not in closedList:
                    tile.H = (abs(end.x-tile.x)+abs(end.y-tile.y))*10
                    if pos not in openList:
                        openList[pos] = tile
                    tile.parent = current
        return path

    def retracePath(self, c, path):
        """
        for A* to retrace the path
        """
        path.insert(0,(c.x, c.y))
        if c.parent == None:
            return
        self.retracePath(c.parent, path)

    def getAroundAvailablePosition(self, pos):
        """
        get the available postions around the given position
        """
        current_rect = pygame.Rect(pos, [26, 26])
        available = []
        # move player
        new_position_up = (current_rect.left, current_rect.top - self.speed)
        if not new_position_up[1] < 0:
            if self.checkPos(new_position_up):
                available.append(new_position_up)

        new_position_right = (current_rect.left + self.speed, current_rect.top)
        if not new_position_right[0] > (416 - 26):
            if self.checkPos(new_position_right):
                available.append(new_position_right)

        new_position_down = (current_rect.left, current_rect.top + self.speed)
        if not new_position_down[1] > (416 - 26):
            if self.checkPos(new_position_down):
                available.append(new_position_down)

        new_position_left = (current_rect.left - self.speed, current_rect.top)
        if not new_position_left[0] < 0:
            if self.checkPos(new_position_left):
                available.append(new_position_left)

        return available

    def checkPos(self, pos):
        """ check pos availability"""

        global players, enemies, bonuses

        player_rect = pygame.Rect(pos, [26, 26])

        # collisions with tiles
        if player_rect.collidelist(self.level.obstacle_rects) != -1:
            return False

        return True


    def loadLevel(self, level_nr = 1):
        """ Load specified level
        @return boolean Whether level was loaded
        """
        filename = "levels/"+str(1)
        if (not os.path.isfile(filename)):
            return False
        level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        #print "start load map"
        x, y = 0, 0
        for row in data:
            self.map.append([])
            for ch in row:
                if ch == ".":
                    self.map[y].append(0)  # none
                elif ch == "#":
                    self.map[y].append(10) # brick
                elif ch == "@":
                    self.map[y].append(100)  # steel, 100, unavailable
                elif ch == "~":
                    self.map[y].append(100)  # water, 100, unavailable
                elif ch == "%":
                    self.map[y].append(0)  # grass, 0, available
                elif ch == "-":
                    self.map[y].append(0)  # frozen, 0, available
                x += 1
            x = 0
            y += 1
        #print "end load map"
        return True

    def reset(self):
        """ reset player """
        print "reset player:", self.start_position
        self.rotate(self.start_direction, False)
        self.rect.topleft = self.start_position
        self.superpowers = 0
        self.max_active_bullets = 2
        self.health = 100
        self.paralised = False
        self.paused = False
        self.pressed = [False] * 4
        self.state = self.STATE_ALIVE

    def getNearBaseTarget(self):
        """
        to target the enemy who is nearest to base
        """
        if self.target_enemy is not None and self.target_enemy.state != self.target_enemy.STATE_DEAD :
            if self.target_enemy.isNearBase():
                return True

        global enemies
        base_target = None
        distance = 100000
        for enemy in enemies:
            if enemy.isNearBase():
                dis = self.getMDistance((192,384), enemy.rect.topleft)
                if dis < distance:
                    base_target = enemy
                    distance = dis

        if base_target is None:
            return False
        else:
            print "found near base!!!"
            self.target_enemy = base_target
            return True


    def aimAndFire(self, enemy_rect):
        """
        Rotate the AI tank to aim at the given target and fire at target
        """
        if self.state != Tank.STATE_ALIVE:
            return
        enemy_direction = self.getEnemyDirection(enemy_rect)
        #print "in aim and fire"
        if enemy_direction is None:
            pass
        else:
            if self.direction != enemy_direction:
                self.rotate(enemy_direction)
            #print "start fire"
            if self.lives > 0:
                self.fire()


    def getEnemyDirection(self, enemy_rect):
        """
        Returns which direction that the given target is at using terget's coordinates
        """
        if enemy_rect.centerx in range(self.rect.left, self.rect.left + self.rect.width):
            if enemy_rect.centery < self.rect.centery:
                return Tank.DIR_UP
            else:
                return Tank.DIR_DOWN
        if enemy_rect.centery in range(self.rect.top, self.rect.top + self.rect.height):
            if enemy_rect.centerx < self.rect.centerx:
                return Tank.DIR_LEFT
            else:
                return Tank.DIR_RIGHT
        return None

    def targetNearestEnemy(self):
        """
        target the nearest enemy from AI
        """
        global enemies
        closest_enemy = None
        for enemy in enemies:
            if closest_enemy is None:
                closest_enemy = enemy
            else:
                if self.getManhattanDistance(enemy) < self.getManhattanDistance(closest_enemy):
                    closest_enemy = enemy
        self.target_enemy = closest_enemy


class Tile():
    """
    Tile class remains unchanged from the code base
    Player's castle/fortress
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.H = None

class Game():
    """
    We did some modification to this class

    1. We remove some code from the showMenu() funtion
    in order to remove the player selection page, becasue we
    only allow one AI player in our game

    2. We add a while loop in the nextLevel() function to
    control the AI player and the whole game flow
    """

    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    TILE_SIZE = 16

    def __init__(self):

        global screen, sprites, play_sounds, sounds

        # center window
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.init()

        pygame.display.set_caption("Battle City")

        size = width, height = 480, 416
        screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()

        # load sprites (funky version)
        #sprites = pygame.transform.scale2x(pygame.image.load("images/sprites.gif"))
        # load sprites (pixely version)
        sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])
        #screen.set_colorkey((0,138,104))

        pygame.display.set_icon(sprites.subsurface(0, 0, 13*2, 13*2))

        # load sounds
        if play_sounds:
            pygame.mixer.init(44100, -16, 1, 512)

            sounds["start"] = pygame.mixer.Sound("sounds/gamestart.ogg")
            sounds["end"] = pygame.mixer.Sound("sounds/gameover.ogg")
            sounds["score"] = pygame.mixer.Sound("sounds/score.ogg")
            sounds["bg"] = pygame.mixer.Sound("sounds/background.ogg")
            sounds["fire"] = pygame.mixer.Sound("sounds/fire.ogg")
            sounds["bonus"] = pygame.mixer.Sound("sounds/bonus.ogg")
            sounds["explosion"] = pygame.mixer.Sound("sounds/explosion.ogg")
            sounds["brick"] = pygame.mixer.Sound("sounds/brick.ogg")
            sounds["steel"] = pygame.mixer.Sound("sounds/steel.ogg")

        self.enemy_life_image = sprites.subsurface(81*2, 57*2, 7*2, 7*2)
        self.player_life_image = sprites.subsurface(89*2, 56*2, 7*2, 8*2)
        self.flag_image = sprites.subsurface(64*2, 49*2, 16*2, 15*2)

        # this is used in intro screen
        self.player_image = pygame.transform.rotate(sprites.subsurface(0, 0, 13*2, 13*2), 270)

        # if true, no new enemies will be spawn during this time
        self.timefreeze = False

        # load custom font
        self.font = pygame.font.Font("fonts/prstart.ttf", 16)

        # pre-render game over text
        self.im_game_over = pygame.Surface((64, 40))
        self.im_game_over.set_colorkey((0,0,0))
        self.im_game_over.blit(self.font.render("GAME", False, (127, 64, 64)), [0, 0])
        self.im_game_over.blit(self.font.render("OVER", False, (127, 64, 64)), [0, 20])
        self.game_over_y = 416+40

        # number of players. here is defined preselected menu value
        self.nr_of_players = 1

        del players[:]
        del bullets[:]
        del enemies[:]
        del bonuses[:]


    def triggerBonus(self, bonus, player):
        """ Execute bonus powers """

        global enemies, labels, play_sounds, sounds

        if play_sounds:
            sounds["bonus"].play()

        player.trophies["bonus"] += 1
        player.score += 500

        if bonus.bonus == bonus.BONUS_GRENADE:
            for enemy in enemies:
                enemy.explode()
        elif bonus.bonus == bonus.BONUS_HELMET:
            self.shieldPlayer(player, True, 10000)
        elif bonus.bonus == bonus.BONUS_SHOVEL:
            self.level.buildFortress(self.level.TILE_STEEL)
            gtimer.add(10000, lambda :self.level.buildFortress(self.level.TILE_BRICK), 1)
        elif bonus.bonus == bonus.BONUS_STAR:
            player.superpowers += 1
            if player.superpowers == 2:
                player.max_active_bullets = 2
        elif bonus.bonus == bonus.BONUS_TANK:
            player.lives += 1
        elif bonus.bonus == bonus.BONUS_TIMER:
            self.toggleEnemyFreeze(True)
            gtimer.add(10000, lambda :self.toggleEnemyFreeze(False), 1)
        bonuses.remove(bonus)

        labels.append(Label(bonus.rect.topleft, "500", 500))

    def shieldPlayer(self, player, shield = True, duration = None):
        """ Add/remove shield
        player: player (not enemy)
        shield: true/false
        duration: in ms. if none, do not remove shield automatically
        """
        player.shielded = shield
        if shield:
            player.timer_uuid_shield = gtimer.add(100, lambda :player.toggleShieldImage())
        else:
            gtimer.destroy(player.timer_uuid_shield)

        if shield and duration != None:
            gtimer.add(duration, lambda :self.shieldPlayer(player, False), 1)


    def spawnEnemy(self):
        """ Spawn new enemy if needed
        Only add enemy if:
            - there are at least one in queue
            - map capacity hasn't exceeded its quota
            - now isn't timefreeze
        """

        global enemies

        if len(enemies) >= self.level.max_active_enemies:
            return
        if len(self.level.enemies_left) < 1 or self.timefreeze:
            return
        enemy = Enemy(self.level, 1)

        # if len(enemies) == 0:
        enemies.append(enemy)



    def respawnPlayer(self, player, clear_scores = False):
        """ Respawn player """
        player.reset()

        if clear_scores:
            player.trophies = {
                "bonus" : 0, "enemy0" : 0, "enemy1" : 0, "enemy2" : 0, "enemy3" : 0
            }

        self.shieldPlayer(player, True, 4000)

    def gameOver(self):
        """ End game and return to menu """
        global play_sounds, sounds

        print "Game Over"
        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()
            sounds["end"].play()

        self.game_over_y = 416+40

        self.game_over = True
        gtimer.add(3000, lambda :self.showScores(), 1)

    def gameOverScreen(self):
        """ Show game over screen """
        global screen
        # stop game main loop (if any)
        self.running = False
        screen.fill([0, 0, 0])

        self.writeInBricks("game", [125, 140])
        self.writeInBricks("over", [125, 220])
        pygame.display.flip()

        while 1:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.showMenu()
                        return

    def showMenu(self):
        """ Show game menu
        Redraw screen only when up or down key is pressed. When enter is pressed,
        exit from this screen and start the game with selected number of players
        """
        global players, screen
        # stop game main loop (if any)
        self.running = False

        # clear all timers
        del gtimer.timers[:]

        self.stage = 0
        self.nr_of_players = 1
        self.drawIntroScreen()
        del players[:]
        self.nextLevel()

    def reloadPlayers(self):
        """ Init players
        If players already exist, just reset them
        """

        global players

        if len(players) == 0:
            # first player
            x = 8 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
            y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2

            player = Player(
                self.level, 0, [x, y], self.DIR_UP, (0, 0, 13*2, 13*2)
            )
            players.append(player)

            # second player
            if self.nr_of_players == 2:
                x = 16 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                player = Player(
                    self.level, 0, [x, y], self.DIR_UP, (16*2, 0, 13*2, 13*2)
                )
                player.controls = [102, 119, 100, 115, 97]
                players.append(player)

        for player in players:
            player.level = self.level
            self.respawnPlayer(player, True)

    def showScores(self):
        """ Show level scores """

        global screen, sprites, players, play_sounds, sounds

        # stop game main loop (if any)
        self.running = False

        # clear all timers
        del gtimer.timers[:]

        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()

        hiscore = self.loadHiscore()

        # update hiscore if needed
        if players[0].score > hiscore:
            hiscore = players[0].score
            self.saveHiscore(hiscore)
        if self.nr_of_players == 2 and players[1].score > hiscore:
            hiscore = players[1].score
            self.saveHiscore(hiscore)

        img_tanks = [
            sprites.subsurface(32*2, 0, 13*2, 15*2),
            sprites.subsurface(48*2, 0, 13*2, 15*2),
            sprites.subsurface(64*2, 0, 13*2, 15*2),
            sprites.subsurface(80*2, 0, 13*2, 15*2)
        ]

        img_arrows = [
            sprites.subsurface(81*2, 48*2, 7*2, 7*2),
            sprites.subsurface(88*2, 48*2, 7*2, 7*2)
        ]

        screen.fill([0, 0, 0])

        # colors
        black = pygame.Color("black")
        white = pygame.Color("white")
        purple = pygame.Color(127, 64, 64)
        pink = pygame.Color(191, 160, 128)

        screen.blit(self.font.render("HI-SCORE", False, purple), [105, 35])
        screen.blit(self.font.render(str(hiscore), False, pink), [295, 35])

        screen.blit(self.font.render("STAGE"+str(self.stage).rjust(3), False, white), [170, 65])

        screen.blit(self.font.render("I-PLAYER", False, purple), [25, 95])

        #player 1 global score
        screen.blit(self.font.render(str(players[0].score).rjust(8), False, pink), [25, 125])

        if self.nr_of_players == 2:
            screen.blit(self.font.render("II-PLAYER", False, purple), [310, 95])

            #player 2 global score
            screen.blit(self.font.render(str(players[1].score).rjust(8), False, pink), [325, 125])

        # tanks and arrows
        for i in range(4):
            screen.blit(img_tanks[i], [226, 160+(i*45)])
            screen.blit(img_arrows[0], [206, 168+(i*45)])
            if self.nr_of_players == 2:
                screen.blit(img_arrows[1], [258, 168+(i*45)])

        screen.blit(self.font.render("TOTAL", False, white), [70, 335])

        # total underline
        print "print line!!!!!"
        pygame.draw.line(screen, white, [170, 330], [307, 330], 4)

        # pygame.draw.circle(screen, white, (170,330), 10, 10)
        pygame.display.flip()

        self.clock.tick(2)

        interval = 5

        # points and kills
        for i in range(4):

            # total specific tanks
            tanks = players[0].trophies["enemy"+str(i)]

            for n in range(tanks+1):
                if n > 0 and play_sounds:
                    sounds["score"].play()

                # erase previous text
                screen.blit(self.font.render(str(n-1).rjust(2), False, black), [170, 168+(i*45)])
                # print new number of enemies
                screen.blit(self.font.render(str(n).rjust(2), False, white), [170, 168+(i*45)])
                # erase previous text
                screen.blit(self.font.render(str((n-1) * (i+1) * 100).rjust(4)+" PTS", False, black), [25, 168+(i*45)])
                # print new total points per enemy
                screen.blit(self.font.render(str(n * (i+1) * 100).rjust(4)+" PTS", False, white), [25, 168+(i*45)])
                pygame.display.flip()
                self.clock.tick(interval)

            if self.nr_of_players == 2:
                tanks = players[1].trophies["enemy"+str(i)]

                for n in range(tanks+1):

                    if n > 0 and play_sounds:
                        sounds["score"].play()

                    screen.blit(self.font.render(str(n-1).rjust(2), False, black), [277, 168+(i*45)])
                    screen.blit(self.font.render(str(n).rjust(2), False, white), [277, 168+(i*45)])

                    screen.blit(self.font.render(str((n-1) * (i+1) * 100).rjust(4)+" PTS", False, black), [325, 168+(i*45)])
                    screen.blit(self.font.render(str(n * (i+1) * 100).rjust(4)+" PTS", False, white), [325, 168+(i*45)])

                    pygame.display.flip()
                    self.clock.tick(interval)

            self.clock.tick(interval)

        # total tanks
        tanks = sum([i for i in players[0].trophies.values()]) - players[0].trophies["bonus"]
        screen.blit(self.font.render(str(tanks).rjust(2), False, white), [170, 335])
        if self.nr_of_players == 2:
            tanks = sum([i for i in players[1].trophies.values()]) - players[1].trophies["bonus"]
            screen.blit(self.font.render(str(tanks).rjust(2), False, white), [277, 335])

        pygame.display.flip()

        # do nothing for 2 seconds
        self.clock.tick(1)
        self.clock.tick(1)

        if self.game_over:
            self.gameOverScreen()
        else:
            self.nextLevel()


    def draw(self):
        global screen, castle, players, enemies, bullets, bonuses
        screen.fill([0, 0, 0])

        self.level.draw([self.level.TILE_EMPTY, self.level.TILE_BRICK, self.level.TILE_STEEL, self.level.TILE_FROZE, self.level.TILE_WATER])

        castle.draw()

        for enemy in enemies:
            enemy.draw()

        for label in labels:
            label.draw()

        for player in players:
            player.draw()

        for bullet in bullets:
            bullet.draw()

        for bonus in bonuses:
            bonus.draw()

        self.level.draw([self.level.TILE_GRASS])

        if self.game_over:
            if self.game_over_y > 188:
                self.game_over_y -= 4
            screen.blit(self.im_game_over, [176, self.game_over_y]) # 176=(416-64)/2

        self.drawSidebar()

        pygame.display.flip()

    def drawSidebar(self):

        global screen, players, enemies

        x = 416
        y = 0
        screen.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))

        xpos = x + 16
        ypos = y + 16

        # draw enemy lives
        for n in range(len(self.level.enemies_left) + len(enemies)):
            screen.blit(self.enemy_life_image, [xpos, ypos])
            if n % 2 == 1:
                xpos = x + 16
                ypos+= 17
            else:
                xpos += 17

        # players' lives
        if pygame.font.get_init():
            text_color = pygame.Color('black')
            for n in range(len(players)):
                if n == 0:
                    screen.blit(self.font.render(str(n+1)+"P", False, text_color), [x+16, y+200])
                    screen.blit(self.font.render(str(players[n].lives), False, text_color), [x+31, y+215])
                    screen.blit(self.player_life_image, [x+17, y+215])
                else:
                    screen.blit(self.font.render(str(n+1)+"P", False, text_color), [x+16, y+240])
                    screen.blit(self.font.render(str(players[n].lives), False, text_color), [x+31, y+255])
                    screen.blit(self.player_life_image, [x+17, y+255])

            screen.blit(self.flag_image, [x+17, y+280])
            screen.blit(self.font.render(str(self.stage), False, text_color), [x+17, y+312])


    def drawIntroScreen(self, put_on_surface = True):
        """ Draw intro (menu) screen
        @param boolean put_on_surface If True, flip display after drawing
        @return None
        """
        global screen

        screen.fill([0, 0, 0])

        if pygame.font.get_init():

            hiscore = self.loadHiscore()

            screen.blit(self.font.render("HI- "+str(hiscore), True, pygame.Color('white')), [170, 35])

            screen.blit(self.font.render("1 PLAYER", True, pygame.Color('white')), [165, 250])
            screen.blit(self.font.render("2 PLAYERS", True, pygame.Color('white')), [165, 275])

            screen.blit(self.font.render("(c) 1980 1985 NAMCO LTD.", True, pygame.Color('white')), [50, 350])
            screen.blit(self.font.render("ALL RIGHTS RESERVED", True, pygame.Color('white')), [85, 380])


        if self.nr_of_players == 1:
            screen.blit(self.player_image, [125, 245])
        elif self.nr_of_players == 2:
            screen.blit(self.player_image, [125, 270])

        self.writeInBricks("battle", [65, 80])
        self.writeInBricks("city", [129, 160])

        if put_on_surface:
            pygame.display.flip()

    def animateIntroScreen(self):
        """ Slide intro (menu) screen from bottom to top
        If Enter key is pressed, finish animation immediately
        @return None
        """
        global screen

        self.drawIntroScreen(False)
        screen_cp = screen.copy()

        screen.fill([0, 0, 0])

        y = 416
        while (y > 0):
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        y = 0
                        break

            screen.blit(screen_cp, [0, y])
            pygame.display.flip()
            y -= 5

        screen.blit(screen_cp, [0, 0])
        pygame.display.flip()


    def chunks(self, l, n):
        """ Split text string in chunks of specified size
        @param string l Input string
        @param int n Size (number of characters) of each chunk
        @return list
        """
        return [l[i:i+n] for i in range(0, len(l), n)]

    def writeInBricks(self, text, pos):
        """ Write specified text in "brick font"
        Only those letters are available that form words "Battle City" and "Game Over"
        Both lowercase and uppercase are valid input, but output is always uppercase
        Each letter consists of 7x7 bricks which is converted into 49 character long string
        of 1's and 0's which in turn is then converted into hex to save some bytes
        @return None
        """

        global screen, sprites

        bricks = sprites.subsurface(56*2, 64*2, 8*2, 8*2)
        brick1 = bricks.subsurface((0, 0, 8, 8))
        brick2 = bricks.subsurface((8, 0, 8, 8))
        brick3 = bricks.subsurface((8, 8, 8, 8))
        brick4 = bricks.subsurface((0, 8, 8, 8))

        alphabet = {
            "a" : "0071b63c7ff1e3",
            "b" : "01fb1e3fd8f1fe",
            "c" : "00799e0c18199e",
            "e" : "01fb060f98307e",
            "g" : "007d860cf8d99f",
            "i" : "01f8c183060c7e",
            "l" : "0183060c18307e",
            "m" : "018fbffffaf1e3",
            "o" : "00fb1e3c78f1be",
            "r" : "01fb1e3cff3767",
            "t" : "01f8c183060c18",
            "v" : "018f1e3eef8e08",
            "y" : "019b3667860c18"
        }

        abs_x, abs_y = pos

        for letter in text.lower():

            binstr = ""
            for h in self.chunks(alphabet[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self.chunks(binstr, 7)):
                for i, bit in enumerate(row):
                    if bit == "1":
                        if i%2 == 0 and j%2 == 0:
                            surf_letter.blit(brick1, [x, y])
                        elif i%2 == 1 and j%2 == 0:
                            surf_letter.blit(brick2, [x, y])
                        elif i%2 == 1 and j%2 == 1:
                            surf_letter.blit(brick3, [x, y])
                        elif i%2 == 0 and j%2 == 1:
                            surf_letter.blit(brick4, [x, y])
                        if x > letter_w:
                            letter_w = x
                    x += 8
                x = 0
                y += 8
            screen.blit(surf_letter, [abs_x, abs_y])
            abs_x += letter_w + 16

    def toggleEnemyFreeze(self, freeze = True):
        """ Freeze/defreeze all enemies """

        global enemies

        for enemy in enemies:
            enemy.paused = freeze
        self.timefreeze = freeze


    def loadHiscore(self):
        """ Load hiscore
        Really primitive version =] If for some reason hiscore cannot be loaded, return 20000
        @return int
        """
        filename = ".hiscore"
        if (not os.path.isfile(filename)):
            return 20000

        f = open(filename, "r")
        hiscore = int(f.read())

        if hiscore > 19999 and hiscore < 1000000:
            return hiscore
        else:
            print "cheater =["
            return 20000

    def saveHiscore(self, hiscore):
        """ Save hiscore
        @return boolean
        """
        try:
            f = open(".hiscore", "w")
        except:
            print "Can't save hi-score"
            return False
        f.write(str(hiscore))
        f.close()
        return True


    def finishLevel(self):
        """ Finish current level
        Show earned scores and advance to the next stage
        """

        global play_sounds, sounds

        if play_sounds:
            sounds["bg"].stop()

        self.active = False
        gtimer.add(3000, lambda :self.showScores(), 1)

        print "Stage "+str(self.stage)+" completed"

    def nextLevel(self):
        """ Start next level """

        global castle, players, bullets, bonuses, play_sounds, sounds

        del bullets[:]
        del enemies[:]
        del bonuses[:]
        castle.rebuild()
        del gtimer.timers[:]

        # load level
        self.stage += 1
        self.level = Level(self.stage)
        self.timefreeze = False

        # set number of enemies by types (basic, fast, power, armor) according to level
        levels_enemies = (
            (18,2,0,0), (14,4,0,2), (14,4,0,2), (2,5,10,3), (8,5,5,2),
            (9,2,7,2), (7,4,6,3), (7,4,7,2), (6,4,7,3), (12,2,4,2),
            (5,5,4,6), (0,6,8,6), (0,8,8,4), (0,4,10,6), (0,2,10,8),
            (16,2,0,2), (8,2,8,2), (2,8,6,4), (4,4,4,8), (2,8,2,8),
            (6,2,8,4), (6,8,2,4), (0,10,4,6), (10,4,4,2), (0,8,2,10),
            (4,6,4,6), (2,8,2,8), (15,2,2,1), (0,4,10,6), (4,8,4,4),
            (3,8,3,6), (6,4,2,8), (4,4,4,8), (0,10,4,6), (0,6,4,10)
        )

        if self.stage <= 10:
            enemies_l = levels_enemies[self.stage - 1]
        else:
            enemies_l = levels_enemies[34]

        self.level.enemies_left = [0]*enemies_l[0] + [1]*enemies_l[1] + [2]*enemies_l[2] + [3]*enemies_l[3]
        random.shuffle(self.level.enemies_left)

        if play_sounds:
            sounds["start"].play()
            gtimer.add(4330, lambda :sounds["bg"].play(-1), 1)

        self.reloadPlayers()

        self.spawnEnemy()
        gtimer.add(3000, lambda :self.spawnEnemy())

        # if True, start "game over" animation
        self.game_over = False

        # if False, game will end w/o "game over" bussiness
        self.running = True

        # if False, players won't be able to do anything
        self.active = True

        self.draw()

        #############################################
        # THE FOLLOWING CODE ARE ADDED BY TEAM BETA #
        #############################################
        player = players[0]
        player.lives = 3
        player.visited = set([])
        path = []
        while self.running:
            time_passed = self.clock.tick(50)
            # kill dangerours target before move
            player.killDangerousTarget()

            # get a target enemy which is near base
            # if there is no enemy near base
            # target on the nearest enemy
            if not player.getNearBaseTarget():
                player.targetNearestEnemy()

            # generate a path to go to the attackcable position
            # to destroy the target enemy
            if player.target_enemy is not None:
                current_attack_position = player.target_enemy.getAttackPosition(player)
                cur_x = player.rect.topleft[0]
                cur_y = player.rect.topleft[1]
                if abs(cur_x - current_attack_position[0]) < 2 and abs(cur_y - current_attack_position[1]) < 2:
                    player.aimAndFire(player.target_enemy.rect)
                else:
                    if len(path) == 0:
                        path = player.goToAttackPosition(current_attack_position)
                        if len(path) == 0:
                            player.visited = set([])
                            continue
                    player.playerMove(path[0], path)

            # kill dangerous target after move
            player.killDangerousTarget()

            # update enemies
            player.update(time_passed)
            for enemy in enemies:
                if enemy.state == enemy.STATE_DEAD and not self.game_over and self.active:
                    enemies.remove(enemy)
                    if len(self.level.enemies_left) == 0 and len(enemies) == 0:
                        self.finishLevel()
                else:
                    enemy.update(time_passed)

            # update AI player
            if not self.game_over and self.active:
                for player in players:
                    if player.state == player.STATE_ALIVE:
                        if player.bonus != None and player.side == player.SIDE_PLAYER:
                            self.triggerBonus(bonus, player)
                            player.bonus = None
                    elif player.state == player.STATE_DEAD:
                        self.superpowers = 0
                        player.lives -= 1
                        if player.lives > 0:
                            self.respawnPlayer(player)
                            # reset the path for AI player
                            path = []
                            player.visited = set([])
                        else:
                            print "player has no lives"
                            self.gameOver()
                            self.gameOverScreen()
                            return

            # update bullets
            for bullet in bullets:
                if bullet.state == bullet.STATE_REMOVED:
                    bullets.remove(bullet)
                else:
                    bullet.update()

            # update bonuses
            for bonus in bonuses:
                if bonus.active == False:
                    bonuses.remove(bonus)

            # update labels
            for label in labels:
                if not label.active:
                    labels.remove(label)

            if not self.game_over:
                if not castle.active:
                    print "base attacked"
                    self.gameOver()
                    self.gameOverScreen()
                    return

            gtimer.update(time_passed)
            self.draw()


if __name__ == "__main__":

    gtimer = Timer()

    sprites = None
    screen = None
    players = []
    enemies = []
    bullets = []
    bonuses = []
    labels = []

    play_sounds = True
    sounds = {}

    game = Game()
    castle = Castle()
    game.showMenu()