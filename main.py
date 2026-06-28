import sys
import os
import json
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAR_TYPES, SAVE_FILE, COLOR_TEXT, COLOR_PANEL, COLOR_WHITE, COLOR_RED, COLOR_NITRO, COLOR_GREEN, COLOR_YELLOW
from cars.player import PlayerCar
from cars.enemy import EnemyCar
from tracks.track1 import Track
from systems.physics import PhysicsEngine
from systems.collision import CollisionSystem
from systems.ai import AISystem

class GameManager:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced 2D Racing Engine")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 42, bold=True)

        # Game State Core Variables
        self.state = "MAIN_MENU"  # MAIN_MENU, GARAGE, RACING, PAUSED, GAME_OVER
        self.race_total_laps = 3
        self.selected_car_model = "Interceptor"
        self.bank_credits = 500
        self.car_upgrades = {"engine": 0, "tires": 0, "brakes": 0}
        self.unlocked_cars = ["Interceptor"]
        
        # Active Level Entity Variables
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.track = None
        self.race_timer = 0.0
        self.winner_announced = ""
        
        self.load_progress_profile()

    def load_progress_profile(self):
        """Loads data from the JSON save file configuration mapping blocks."""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                    self.bank_credits = data.get("credits", 500)
                    self.car_upgrades = data.get("upgrades", {"engine": 0, "tires": 0, "brakes": 0})
                    self.unlocked_cars = data.get("unlocked", ["Interceptor"])
            except Exception as e:
                print(f"Error loading save profile: {e}")

    def save_progress_profile(self):
        """Saves current variables into profile structures."""
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump({
                    "credits": self.bank_credits,
                    "upgrades": self.car_upgrades,
                    "unlocked": self.unlocked_cars
                }, f, indent=4)
        except Exception as e:
            print(f"Error executing profile write operations: {e}")

    def init_race_session(self):
        """Prepares entity matrices, maps, layouts, and tracking metrics to start a race."""
        self.track = Track()
        
        # Position vehicles near the start line
        self.player = PlayerCar(250, 450, self.selected_car_model, self.car_upgrades)
        self.player.angle = 90.0 # Point Northwards facing forward grid blocks
        
        self.enemies.empty()
        for idx in range(3):
            # Staggered grid launch layout placement allocations
            bot = EnemyCar(200 + (idx * 45), 520 + (idx * 55), idx, difficulty="Medium")
            bot.angle = 90.0
            self.enemies.add(bot)
            
        self.race_timer = 0.0
        self.winner_announced = ""
        self.state = "RACING"

    def execute_core_loop(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            # Force stabilization limits against structural delta spikes during transitions
            if dt > 0.1: dt = 0.1 
            
            self.process_events()
            self.update_game_states(dt)
            self.render_game_view()

    def process_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.save_progress_profile()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state == "MAIN_MENU":
                    if event.key == pygame.K_RETURN:
                        self.init_race_session()
                    elif event.key == pygame.K_g:
                        self.state = "GARAGE"
                elif self.state == "GARAGE":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MAIN_MENU"
                elif self.state == "RACING":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PAUSED"
                elif self.state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "RACING"
                    elif event.key == pygame.K_q:
                        self.state = "MAIN_MENU"
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.state = "MAIN_MENU"

            # Route UI operations directly into action handler functions
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click_interactions(event.pos)

    def handle_click_interactions(self, mouse_pos):
        """Maps screens space screen coordination bounds into execution routines."""
        if self.state == "MAIN_MENU":
            # Start button bounding metrics box
            if 540 <= mouse_pos[0] <= 740 and 320 <= mouse_pos[1] <= 370:
                self.init_race_session()
            # Garage transition button bounding metrics box
            if 540 <= mouse_pos[0] <= 740 and 400 <= mouse_pos[1] <= 450:
                self.state = "GARAGE"
                
        elif self.state == "GARAGE":
            # Selection switching logic operations loops
            mx, my = mouse_pos
            if 100 <= my <= 250:
                for idx, model in enumerate(CAR_TYPES.keys()):
                    if 100 + (idx * 300) <= mx <= 350 + (idx * 300):
                        if model in self.unlocked_cars:
                            self.selected_car_model = model
                        elif self.bank_credits >= CAR_TYPES[model]["cost"]:
                            self.bank_credits -= CAR_TYPES[model]["cost"]
                            self.unlocked_cars.append(model)
                            self.selected_car_model = model
                            self.save_progress_profile()

            # Upgrade logic operations blocks
            if 420 <= my <= 470:
                # Engine Upgrade Button
                if 200 <= mx <= 400 and self.car_upgrades["engine"] < 5 and self.bank_credits >= 150:
                    self.bank_credits -= 150
                    self.car_upgrades["engine"] += 1
                # Tires Upgrade Button
                if 500 <= mx <= 700 and self.car_upgrades["tires"] < 5 and self.bank_credits >= 150:
                    self.bank_credits -= 150
                    self.car_upgrades["tires"] += 1
                # Brakes Upgrade Button
                if 800 <= mx <= 1000 and self.car_upgrades["brakes"] < 5 and self.bank_credits >= 150:
                    self.bank_credits -= 150
                    self.car_upgrades["brakes"] += 1
                self.save_progress_profile()
                
            # Exit bounding box
            if 540 <= mx <= 740 and 600 <= my <= 650:
                self.state = "MAIN_MENU"

    def update_game_states(self, dt):
        if self.state != "RACING":
            return

        self.race_timer += dt
        keys = pygame.key.get_pressed()
        
        # 1. Update Player Input, Physics, and Timers
        self.player.process_inputs(keys)
        self.player.update_timers(dt)
        PhysicsEngine.update_vehicle(self.player, dt)
        self.player.render_transform()

        # 2. Update AI Drivers
        for bot in self.enemies:
            AISystem.process_agent(bot, self.track, dt)
            PhysicsEngine.update_vehicle(bot, dt)
            bot.render_transform()

        # 3. Handle Obstacle & Boundary Collisions
        CollisionSystem.check_track_boundaries(self.player, self.track)
        for bot in self.enemies:
            CollisionSystem.check_track_boundaries(bot, self.track)

        # 4. Handle Vehicle-to-Vehicle Collisions
        for bot in self.enemies:
            CollisionSystem.resolve_car_to_car(self.player, bot)
        bot_list = self.enemies.sprites()
        for i in range(len(bot_list)):
            for j in range(i + 1, len(bot_list)):
                CollisionSystem.resolve_car_to_car(bot_list[i], bot_list[j])

        # 5. Process Item Pickups
        CollisionSystem.process_pickups(self.player, self.track)
        for bot in self.enemies:
            CollisionSystem.process_pickups(bot, self.track)

        # 6. Evaluate Checkpoint Progress and Lap Splits
        self.evaluate_race_progress(self.player, "Player")
        for idx, bot in enumerate(self.enemies):
            self.evaluate_race_progress(bot, f"AI Agent #{idx+1}")

        # 7. Check Game Over Conditions
        if self.player.health <= 0:
            self.winner_announced = "Car Destroyed! Total Wreckage."
            self.state = "GAME_OVER"

    def evaluate_race_progress(self, vehicle, entity_name):
        """Tracks passing checkpoints and handles lap progression mechanics."""
        for idx, cp_rect in enumerate(self.track.checkpoints):
            if vehicle.rect.colliderect(cp_rect):
                # Verify that checkpoints are passed in sequential order
                if idx == vehicle.last_checkpoint + 1:
                    vehicle.last_checkpoint = idx
                elif idx == 0 and vehicle.last_checkpoint == len(self.track.checkpoints) - 1:
                    # Completed a full lap around the track circuit loop
                    vehicle.last_checkpoint = 0
                    vehicle.current_lap += 1
                    
                    if vehicle.current_lap > self.race_total_laps:
                        if not self.winner_announced:
                            self.winner_announced = f"{entity_name} Wins the Race!"
                            if entity_name == "Player":
                                self.bank_credits += 400 # Add reward funds
                            else:
                                self.bank_credits += 100 # Add participation funds
                            self.save_progress_profile()
                        self.state = "GAME_OVER"

    def render_game_view(self):
        self.screen.fill((10, 10, 10))
        
        if self.state == "MAIN_MENU":
            self.render_main_menu_canvas()
        elif self.state == "GARAGE":
            self.render_garage_canvas()
        elif self.state in ["RACING", "PAUSED", "GAME_OVER"]:
            self.render_active_race_viewport()
            
        pygame.display.flip()

    def render_main_menu_canvas(self):
        title = self.large_font.render("2D RACING SIMULATOR ENGINE", True, COLOR_RED)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        
        # Start Button
        pygame.draw.rect(self.screen, COLOR_GREEN, (540, 320, 200, 50), border_radius=4)
        lbl_start = self.font.render("START RACE", True, COLOR_WHITE)
        self.screen.blit(lbl_start, (640 - lbl_start.get_width() // 2, 332))
        
        # Garage Button
        pygame.draw.rect(self.screen, COLOR_WHITE, (540, 400, 200, 50), border_radius=4)
        lbl_garage = self.font.render("ENTER GARAGE", True, (20, 20, 20))
        self.screen.blit(lbl_garage, (640 - lbl_garage.get_width() // 2, 412))
        
        credits_lbl = self.font.render(f"Available Funds: ${self.bank_credits}", True, COLOR_TEXT)
        self.screen.blit(credits_lbl, (SCREEN_WIDTH // 2 - credits_lbl.get_width() // 2, 500))

    def render_garage_canvas(self):
        title = self.large_font.render("VEHICLE RECONGIGURATION GARAGE", True, COLOR_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        
        # Draw vehicle type options data columns layout structure
        for idx, (model, stats) in enumerate(CAR_TYPES.items()):
            bx = 100 + (idx * 300)
            rect = pygame.Rect(bx, 120, 260, 200)
            
            # Highlight selected vehicle chassis option block
            bg_col = (40, 70, 40) if self.selected_car_model == model else (30, 30, 30)
            pygame.draw.rect(self.screen, bg_col, rect, border_radius=6)
            pygame.draw.rect(self.screen, stats["color"], rect, 3, border_radius=6)
            
            m_lbl = self.font.render(model, True, COLOR_WHITE)
            self.screen.blit(m_lbl, (bx + 20, 135))
            
            # Status Text fields strings configuration values arrays
            status = "SELECTED" if self.selected_car_model == model else "UNLOCKED" if model in self.unlocked_cars else f"BUY: ${stats['cost']}"
            s_lbl = self.font.render(status, True, COLOR_YELLOW if "BUY" in status else COLOR_WHITE)
            self.screen.blit(s_lbl, (bx + 20, 165))
            
            spd_lbl = self.font.render(f"Speed: {stats['max_speed']}", True, COLOR_TEXT)
            self.screen.blit(spd_lbl, (bx + 20, 210))
            hnd_lbl = self.font.render(f"Handling: {stats['handling']}", True, COLOR_TEXT)
            self.screen.blit(hnd_lbl, (bx + 20, 240))

        # Upgrade Section Configuration Panel Blocks
        panel = pygame.Rect(100, 370, 1080, 180)
        pygame.draw.rect(self.screen, (25, 25, 25), panel, border_radius=6)
        
        upgrades_list = [("engine", 200), ("tires", 500), ("brakes", 800)]
        for name, ux in upgrades_list:
            lvl = self.car_upgrades[name]
            pygame.draw.rect(self.screen, COLOR_GREEN, (ux, 420, 200, 50), border_radius=4)
            lbl = self.font.render(f"UPGRADE {name.upper()} ({lvl}/5)", True, COLOR_WHITE)
            self.screen.blit(lbl, (ux + 10, 432))
            cost_lbl = self.font.render("Cost: $150", True, COLOR_TEXT)
            self.screen.blit(cost_lbl, (ux + 10, 480))

        # Exit Back interface button graphics
        pygame.draw.rect(self.screen, COLOR_RED, (540, 600, 200, 50), border_radius=4)
        exit_lbl = self.font.render("MAIN MENU", True, COLOR_WHITE)
        self.screen.blit(exit_lbl, (640 - exit_lbl.get_width() // 2, 612))
        
        credits_lbl = self.font.render(f"Available Funds: ${self.bank_credits}", True, COLOR_YELLOW)
        self.screen.blit(credits_lbl, (100, 612))

    def render_active_race_viewport(self):
        """Implements a dynamic tracking camera relative to player positioning vectors."""
        camera_x = self.player.x - SCREEN_WIDTH // 2
        camera_y = self.player.y - SCREEN_HEIGHT // 2
        
        # Clamp camera alignment to track dimensions
        camera_x = max(0, min(self.track.width - SCREEN_WIDTH, camera_x))
        camera_y = max(0, min(self.track.height - SCREEN_HEIGHT, camera_y))

        # Draw track within the active viewport view camera frame offset matrix bounds
        self.screen.blit(self.track.surface, (0, 0), (camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Render Pickups relative to camera positions
        for pickup in self.track.pickups:
            color = COLOR_NITRO if pickup["type"] == "nitro" else COLOR_GREEN if pickup["type"] == "repair" else (30, 144, 255)
            adjusted_rect = pickup["rect"].move(-camera_x, -camera_y)
            pygame.draw.rect(self.screen, color, adjusted_rect, border_radius=4)

        # Blit Computer AI drivers onto viewport surface canvas
        for bot in self.enemies:
            self.screen.blit(bot.image, (bot.rect.x - camera_x, bot.rect.y - camera_y))

        # Blit Human Player car model instance canvas metrics
        self.screen.blit(self.player.image, (self.player.rect.x - camera_x, self.player.rect.y - camera_y))

        # Render Core Heads-Up Display overlays
        self.render_heads_up_display_overlay()

        # Render overlay dialog panels context states
        if self.state == "PAUSED":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            p_lbl = self.large_font.render("SIMULATION PAUSED", True, COLOR_WHITE)
            self.screen.blit(p_lbl, (SCREEN_WIDTH // 2 - p_lbl.get_width() // 2, 300))
            h_lbl = self.font.render("Press [ESC] to Resume or [Q] to Terminate Session", True, COLOR_TEXT)
            self.screen.blit(h_lbl, (SCREEN_WIDTH // 2 - h_lbl.get_width() // 2, 380))
            
        elif self.state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 10, 210))
            self.screen.blit(overlay, (0, 0))
            
            w_lbl = self.large_font.render(self.winner_announced, True, COLOR_YELLOW)
            self.screen.blit(w_lbl, (SCREEN_WIDTH // 2 - w_lbl.get_width() // 2, 260))
            
            info_lbl = self.font.render("Press [ENTER] to return to Main Menu layout selection panels.", True, COLOR_WHITE)
            self.screen.blit(info_lbl, (SCREEN_WIDTH // 2 - info_lbl.get_width() // 2, 360))

    def render_heads_up_display_overlay(self):
        """Draws telemetry HUD elements (Speedometer, Nitro meter, and Damage tracks)."""
        # Top Left Stats Data Panels background wrapper boxes
        hud_bg = pygame.Surface((320, 160), pygame.SRCALPHA)
        hud_bg.fill(COLOR_PANEL)
        self.screen.blit(hud_bg, (15, 15))
        
        # Speed Calculations display rendering configurations
        computed_speed = abs(int(self.player.speed * 0.95))
        speed_lbl = self.font.render(f"VELOCITY: {computed_speed} KM/H", True, COLOR_WHITE)
        self.screen.blit(speed_lbl, (30, 25))
        
        # Lap Counters display structural layouts
        lap_string = f"LAP: {min(self.player.current_lap, self.race_total_laps)} / {self.race_total_laps}"
        lap_lbl = self.font.render(lap_string, True, COLOR_YELLOW)
        self.screen.blit(lap_lbl, (30, 55))
        
        # Timer metrics logs context elements
        timer_lbl = self.font.render(f"TIME: {self.race_timer:.2f} SEC", True, COLOR_TEXT)
        self.screen.blit(timer_lbl, (30, 85))

        # Structural Integrity Bar layout configurations
        health_pct = self.player.health / self.player.stats["max_health"]
        pygame.draw.rect(self.screen, (60, 10, 10), (30, 125, 120, 16), border_radius=3)
        pygame.draw.rect(self.screen, COLOR_GREEN, (30, 125, int(120 * health_pct), 16), border_radius=3)
        lbl_h = self.font.render("HULL", True, COLOR_WHITE)
        self.screen.blit(lbl_h, (30, 108))

        # Nitro Reserves Meter configurations
        nitro_pct = self.player.nitro_energy / 100.0
        pygame.draw.rect(self.screen, (20, 50, 60), (180, 125, 120, 16), border_radius=3)
        pygame.draw.rect(self.screen, COLOR_NITRO, (180, 125, int(120 * nitro_pct), 16), border_radius=3)
        lbl_n = self.font.render("NITRO", True, COLOR_WHITE)
        self.screen.blit(lbl_n, (180, 108))

        # Display Shield alert notifications
        if self.player.shield_active:
            sh_lbl = self.font.render(f"SHIELD ACTIVE: {self.player.shield_timer:.1f}S", True, COLOR_NITRO)
            self.screen.blit(sh_lbl, (30, 150))

if __name__ == "__main__":
    game_instance = GameManager()
    game_instance.execute_core_loop()