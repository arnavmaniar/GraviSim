import pygame
import math
import pygame_gui
import os

pygame.init()

# init constants
width, height = 1400, 800
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gravitational Simulation")

plan_mass = 200 #arbitrary values the earht does not have a mass of 200kg
ship_mass = 1
G = 10
FPS = 60
planet_size = 50
object_size = 5
velocity_scale = 50

bg = pygame.transform.scale(pygame.image.load("bkg.jpg"), (width, height))
planet = pygame.transform.scale(pygame.image.load("earth.png"), (planet_size * 2, planet_size * 2))
moon = pygame.transform.scale(pygame.image.load("moon.jpeg"), (planet_size, planet_size))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# init GUI manager
manager = pygame_gui.UIManager((width, height))

# init classes
class Planet:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
    
    def draw(self):
        win.blit(planet, (self.x - planet_size, self.y - planet_size)) #draws planet

class Moon:
    def __init__(self, x, y, mass, distance_from_planet, angular_velocity):
        self.x = x
        self.y = y
        self.mass = mass
        self.distance_from_planet = distance_from_planet
        self.angular_velocity = angular_velocity
        self.angle = 0  #initial angle

    def update_position(self, planet):
        #update angle based on angular velo
        self.angle += self.angular_velocity
        
        #calc new pos based on angle/distance from planet
        self.x = planet.x + self.distance_from_planet * math.cos(self.angle)
        self.y = planet.y + self.distance_from_planet * math.sin(self.angle)

    def draw(self):
        win.blit(moon, (int(self.x) - planet_size // 2, int(self.y) - planet_size // 2)) #draws moon

class Spacecraft:
    spacecraft_count = 0
    def __init__(self, x, y, vel_x, vel_y, mass):
        self.x = x 
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.mass = mass
        self.in_orbit = False  # orbit flag
        Spacecraft.spacecraft_count += 1 #add 1 to counter 

    def move(self, planet, moon=None):
        distance_to_planet = math.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2)
        #if spacecraft is not in orbit but is within 100px:
        if not self.in_orbit and distance_to_planet <= 100:
            angle_to_planet = math.atan2(planet.y - self.y, planet.x - self.x) #finds angle based on positions
            self.in_orbit = True  #orbit flag true
            orbit_velocity = math.sqrt(G * planet.mass / distance_to_planet)
            self.vel_x = orbit_velocity * math.cos(angle_to_planet + math.pi / 2) 
            self.vel_y = orbit_velocity * math.sin(angle_to_planet + math.pi / 2) 
            
        else:
            #if not in 100px, calculate grav force
            force_from_planet = (G * self.mass * planet.mass) / distance_to_planet ** 2 #universal law of gravitation
            acceleration_from_planet = force_from_planet / self.mass # f= ma
            angle_to_planet = math.atan2(planet.y - self.y, planet.x - self.x) #angle using tangent

            acc_x_from_planet = acceleration_from_planet * math.cos(angle_to_planet)
            acc_y_from_planet = acceleration_from_planet * math.sin(angle_to_planet) #how much zoom does this have

            self.vel_x += acc_x_from_planet #zoom + zoom zoom
            self.vel_y += acc_y_from_planet #zoom + zoom zoom but other way

            #if moon is rendered, do this (functionality was meant so you could toggle moon but idk it didnt work)
            #this code is like the same as above lol
            
            if moon:
                distance_to_moon = math.sqrt((self.x - moon.x)**2 + (self.y - moon.y)**2)
                force_from_moon = (G * self.mass * moon.mass) / distance_to_moon ** 2 #law of gravitation

                acceleration_from_moon = force_from_moon / self.mass
                angle_to_moon = math.atan2(moon.y - self.y, moon.x - self.x)

                acc_x_from_moon = acceleration_from_moon * math.cos(angle_to_moon)
                acc_y_from_moon = acceleration_from_moon * math.sin(angle_to_moon)

                self.vel_x += acc_x_from_moon
                self.vel_y += acc_y_from_moon
        self.x += self.vel_x
        self.y += self.vel_y


    def get_velocity(self):
        return math.sqrt(self.vel_x ** 2 + self.vel_y ** 2) #uses pythag to return velocity

    def get_centripetal_acceleration(self, planet):
        distance_to_planet = math.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2) #r
        return self.get_velocity()**2 / distance_to_planet #v^2 / r

    def get_force_from_planet(self, planet):
        distance_to_planet = math.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2)
        return (G * self.mass * planet.mass) / distance_to_planet ** 2 #universal law of grav

    def draw(self):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), object_size) #draws spacecraft (its a dot but ykwhat i mean)

def create_ship(location, mouse):
    tx, ty = location 
    mx, my = mouse 
    vel_x = (mx - tx) / velocity_scale
    vel_y = (my - ty) / velocity_scale
    obj = Spacecraft(tx, ty, vel_x, vel_y, ship_mass) #this is so cool i used the class finally omg
    return obj

def clear_objects(objects):
    objects.clear() #clear
    Spacecraft.spacecraft_count = 0

def main():
    running = True
    clock = pygame.time.Clock()

    planet_obj = Planet(width // 2, height // 2, plan_mass) #USING THE CLASS LETS GOOOOO
    moon_obj = Moon(width // 2 + 200, height // 2, 10, 200, 0.01) #USING THE CLASS LETS GOOOOO
    objects = []
    temp_pos = None
    new_object = None
    font = pygame.font.Font(None, 36) #font 1 for spacecraft counter
    font2 = pygame.font.Font(None, 22) #font 2  for data on orbit text

    auto_orbit_enabled = True  # init auto orbit state

    # gui thingies 
    button_clear = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((width - 150, 50), (100, 50)),
        text='Clear', manager=manager
    )
    button_orbit_toggle = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((width - 200, 120), (150, 50)),
        text='Toggle Orbit', manager=manager
    )
    button_orbit_toggle.colours['toggled_bg'] = pygame.Color(255, 0, 0, 255)
    button_orbit_toggle.rebuild()

    while running:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button_clear:
                        clear_objects(objects) #kaboom cleared
                        Spacecraft.spacecraft_count = 0 #resets spacecraft counter
                    elif event.ui_element == button_orbit_toggle:

                        auto_orbit_disabled = not auto_orbit_enabled
                        
                        bg_color = pygame.Color(0, 255, 0, 255)
                        btn_text = 'Orbit Enabled'

                        if auto_orbit_disabled:
                            btn_text = "Orbit Disabled"
                            bg_color = pygame.Color(255, 0, 0, 255)

                        button_orbit_toggle.set_text(btn_text)
                        button_orbit_toggle.colours['normal_bg'] = bg_color

                        button_orbit_toggle.rebuild()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    temp_pos = event.pos
                elif event.button == 3:
                    if temp_pos:
                        new_object = create_ship(temp_pos, event.pos) #make spacesrcaft
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    if new_object:
                        objects.append(new_object)
            manager.process_events(event)

        # Render background and GUI elements
        win.blit(bg, (0, 0))
        spacecraft_count_text = font.render(f"Spacecraft Active: {Spacecraft.spacecraft_count}", True, WHITE)
        win.blit(spacecraft_count_text, (10, height - 40))

        if temp_pos:
            #draws the user figuring out how long and far they want to send the spacecraft
            pygame.draw.line(win, WHITE, temp_pos, pygame.mouse.get_pos(), 2)
            pygame.draw.circle(win, BLUE, temp_pos, object_size)

        # Update spacecraft movement with button toggle
        for obj in objects[:]:
            obj.draw()
            obj.in_orbit = auto_orbit_enabled  # Enable or disable in_orbit functionality
            obj.move(planet_obj, moon_obj)
            off_screen = obj.x < 0 or obj.x > width or obj.y < 0 or obj.y > height 
            collided_with_planet = math.sqrt((obj.x - planet_obj.x)**2 + (obj.y - planet_obj.y)**2) <= planet_size #checks for collision
            collided_with_moon = math.sqrt((obj.x - moon_obj.x)**2 + (obj.y - moon_obj.y)**2) <= planet_size 
            if off_screen or collided_with_planet or collided_with_moon:
                objects.remove(obj)
                Spacecraft.spacecraft_count -= 1

        planet_obj.draw() #draw
        moon_obj.draw() #DRAW
        moon_obj.update_position(planet_obj) #UPDATE IT

        manager.update(time_delta)
        manager.draw_ui(win)

        if new_object != None and (new_object.in_orbit or not auto_orbit_enabled):
            velocity = new_object.get_velocity() #returns v
            centripetal_acceleration = new_object.get_centripetal_acceleration(planet_obj) #returns ac
            force_from_planet = new_object.get_force_from_planet(planet_obj) #returns f
            
            velocity_text = font2.render(f"Velocity: {velocity:.2f} pixels/frame", True, WHITE) #defines render (#nyoom)
            acceleration_text = font2.render(f"Centripetal Acceleration: {centripetal_acceleration:.2f} pixels/frame^2", True, WHITE) 
            force_text = font2.render(f"Force from Planet: {force_from_planet:.2f} Newtons (scaled)", True, WHITE) #scaled for the sake of the simulation
            
            win.blit(velocity_text, (10, 10)) #blits render
            win.blit(acceleration_text, (10, 25))
            win.blit(force_text, (10, 40))


        manager.update(time_delta)
        manager.draw_ui(win)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main() #happy days its DONE