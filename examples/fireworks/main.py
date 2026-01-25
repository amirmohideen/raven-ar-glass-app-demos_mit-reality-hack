# Fireworks App - Double click to launch fireworks!
from random import randint, uniform, choice
from dataclasses import dataclass
from typing import List

from PySide6.QtCore import QEvent
from PySide6.QtGui import QCursor

from raven_framework.core.raven_app import RavenApp
from raven_framework.core.run_app import RunApp
from raven_framework.components.container import Container
from raven_framework.components.text_box import TextBox
from raven_framework.helpers.routine import Routine

# Window offset (app is 640x640 within 720x720 window)
WINDOW_OFFSET = 40

# Firework colors
FIREWORK_COLORS = [
    "#FF0000",  # Red
    "#FF6600",  # Orange
    "#FFFF00",  # Yellow
    "#00FF00",  # Green
    "#00FFFF",  # Cyan
    "#0066FF",  # Blue
    "#FF00FF",  # Magenta
    "#FF69B4",  # Pink
    "#FFD700",  # Gold
    "#FFFFFF",  # White
]


@dataclass
class Particle:
    """A single firework particle."""
    x: float
    y: float
    vx: float  # velocity x
    vy: float  # velocity y
    color: str
    size: int
    life: int  # frames remaining
    is_rocket: bool = False


class FireworksApp(RavenApp):
    """Fireworks app - Blink Twice to launch fireworks!"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        # Particle system
        self.particles: List[Particle] = []
        self.particle_widgets: dict = {}  # Map particle to widget
        
        # Animation routine
        self.animation_routine = Routine(
            interval_ms=33,  # ~30 FPS
            invoke=self._update_particles,
        )
        
        # Install event filter for double-click detection
        self.app.installEventFilter(self)
        
        # Draw initial UI
        self.init_ui()

    def eventFilter(self, obj, event):
        """Detect double-click events to launch fireworks."""
        if event.type() == QEvent.Type.MouseButtonDblClick:
            # Get cursor position relative to app
            global_pos = QCursor.pos()
            local_pos = self.app.mapFromGlobal(global_pos)
            x = local_pos.x()
            y = local_pos.y()
            
            # Launch firework at click position
            self._launch_firework(x, y)
            return True
        return super().eventFilter(obj, event)

    def init_ui(self):
        """Initialize the UI."""
        self.app.clear()
        self.particle_widgets.clear()
        
        # Dark background
        background = Container(
            width=640,
            height=640,
            background_color="#0a0a1a",
        )
        self.app.add(background, x=0, y=0)
        
        # Instructions
        instructions = TextBox(
            text="Blink Twice to launch fireworks! 🎆",
            font_type="headline",
            alignment="center",
            width=640,
            text_color="#FFFFFF",
        )
        self.app.add(instructions, x=0, y=580)

    def _launch_firework(self, x: int, y: int):
        """Launch a firework rocket from bottom to the click position."""
        # Create rocket particle that travels from bottom to click position
        start_x = x
        start_y = 640  # Bottom of screen
        
        # Calculate velocity to reach target
        distance_y = y - start_y
        frames_to_reach = 20  # Frames to reach target
        vy = distance_y / frames_to_reach
        vx = 0  # Straight up
        
        rocket = Particle(
            x=start_x,
            y=start_y,
            vx=vx,
            vy=vy,
            color="#FFAA00",
            size=8,
            life=frames_to_reach + 5,  # Extra life to ensure explosion
            is_rocket=True,
        )
        rocket.target_y = y  # Store target for explosion
        self.particles.append(rocket)

    def _explode_firework(self, x: float, y: float):
        """Create explosion particles at position."""
        color = choice(FIREWORK_COLORS)
        num_particles = randint(60, 100)
        
        for _ in range(num_particles):
            # Random direction and speed
            angle = uniform(0, 6.28)  # 0 to 2*PI
            speed = uniform(2, 8)
            
            import math
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            particle = Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                color=color if randint(0, 3) > 0 else choice(FIREWORK_COLORS),
                size=randint(4, 8),
                life=randint(20, 40),
            )
            self.particles.append(particle)

    def _update_particles(self):
        """Update all particles each frame."""
        # Redraw background
        self.app.clear()
        self.particle_widgets.clear()
        
        background = Container(
            width=640,
            height=640,
            background_color="#0a0a1a",
        )
        self.app.add(background, x=0, y=0)
        
        # Update and draw particles
        new_particles = []
        explosions = []
        
        for particle in self.particles:
            # Update position
            particle.x += particle.vx
            particle.y += particle.vy
            
            # Apply gravity (except for rockets going up)
            if not particle.is_rocket:
                particle.vy += 0.2  # Gravity
            
            # Decrease life
            particle.life -= 1
            
            if particle.life > 0:
                # Check if rocket reached target
                if particle.is_rocket and particle.y <= particle.target_y:
                    # Explode!
                    explosions.append((particle.x, particle.y))
                else:
                    new_particles.append(particle)
                    
                    # Draw particle
                    if 0 <= particle.x <= 640 and 0 <= particle.y <= 640:
                        # Fade out based on remaining life
                        opacity = min(1.0, particle.life / 20)
                        size = int(particle.size * opacity) + 2
                        
                        particle_widget = Container(
                            width=size,
                            height=size,
                            background_color=particle.color,
                            corner_radius=size // 2,
                        )
                        self.app.add(
                            particle_widget,
                            x=int(particle.x - size // 2),
                            y=int(particle.y - size // 2),
                        )
        
        self.particles = new_particles
        
        # Create explosions
        for ex, ey in explosions:
            self._explode_firework(ex, ey)
        
        # Instructions at bottom
        instructions = TextBox(
            text="Blink Twice to launch fireworks! 🎆",
            font_type="body",
            alignment="center",
            width=640,
            text_color="#FFFFFF",
        )
        self.app.add(instructions, x=0, y=580)


if __name__ == "__main__":
    RunApp.run(lambda: FireworksApp(), app_id="", app_key="")
