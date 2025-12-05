import pygame
import sys
import os
from datetime import datetime

# Import configuration
import config

# Import game components (will be created)
from game_logic.game_manager import GameManager
from ui.game_window import GameWindow
from utils.logger import setup_logger, log_info, log_error


def initialize_pygame():
    """Initialize Pygame and create the game window"""
    try:
        pygame.init()
        pygame.font.init()

        # Create the main display window
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("β-bot: Multi-Agent Chess AI")

        # Set window icon (if available)
        icon_path = os.path.join(config.UI_DIR, 'icon.png')
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)

        # Initialize clock for FPS control
        clock = pygame.time.Clock()

        log_info("Pygame initialized successfully")
        return screen, clock

    except Exception as e:
        log_error(f"Failed to initialize Pygame: {e}")
        sys.exit(1)


def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logger('main')
    log_info("=" * 60)
    log_info("β-bot: Multi-Agent Chess AI Starting")
    log_info("=" * 60)

    # Validate configuration
    config_errors = config.validate_config()
    if config_errors:
        log_error("Configuration errors found:")
        for error in config_errors:
            log_error(f"  - {error}")
        print("\n⚠️  Configuration errors detected. Please check logs.")

    # Initialize Pygame
    screen, clock = initialize_pygame()

    # Create game window manager
    game_window = GameWindow(screen)

    # Create game manager
    game_manager = GameManager()

    # Initialize game
    try:
        log_info("Initializing game systems...")
        game_manager.initialize_game()
        log_info("Game initialized successfully")
    except Exception as e:
        log_error(f"Failed to initialize game: {e}")
        pygame.quit()
        sys.exit(1)

    # Game state
    running = True
    paused = False
    show_fps = config.SHOW_FPS

    log_info("Entering main game loop")
    print("\n🎮 β-bot is ready! Window opened.")
    print("   - ESC: Quit")
    print("   - SPACE: Pause/Resume")
    print("   - F: Toggle FPS display")
    print("   - R: Reset game\n")

    # Main game loop
    frame_count = 0
    try:
        while running:
            # Handle events
            for event in pygame.event.get():
                # Quit event
                if event.type == pygame.QUIT:
                    running = False
                    log_info("Quit event received")

                # Keyboard events
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        log_info("ESC pressed - quitting")

                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        status = "paused" if paused else "resumed"
                        log_info(f"Game {status}")
                        print(f"⏸️  Game {status}")

                    elif event.key == pygame.K_f:
                        show_fps = not show_fps
                        log_info(f"FPS display toggled: {show_fps}")

                    elif event.key == pygame.K_r:
                        log_info("Reset game requested")
                        game_manager.reset_game()
                        print("🔄 Game reset")

                # Mouse events
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not paused:
                        game_manager.handle_mouse_click(event.pos)

                # Pass other events to game window
                game_window.handle_event(event)

            # Update game state (if not paused)
            if not paused:
                try:
                    game_manager.update()
                except Exception as e:
                    log_error(f"Error in game update: {e}")
                    # Don't crash, just log and continue

            # Render everything
            try:
                # Clear screen
                screen.fill(config.BACKGROUND_COLOR)

                # Render game
                game_window.render(game_manager)

                # Show FPS if enabled
                if show_fps:
                    fps = int(clock.get_fps())
                    font = pygame.font.Font(None, 24)
                    fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
                    screen.blit(fps_text, (10, 10))

                # Show pause indicator
                if paused:
                    font = pygame.font.Font(None, 48)
                    pause_text = font.render("PAUSED", True, (255, 255, 0))
                    text_rect = pause_text.get_rect(center=(config.SCREEN_WIDTH // 2, 50))
                    screen.blit(pause_text, text_rect)

                # Update display
                pygame.display.flip()

            except Exception as e:
                log_error(f"Error in rendering: {e}")

            # Control frame rate
            clock.tick(config.FPS)
            frame_count += 1

            # Periodic status log (every 5 seconds)
            if config.DEBUG_MODE and frame_count % (config.FPS * 5) == 0:
                log_info(f"Game running - Frame {frame_count}, FPS: {int(clock.get_fps())}")

    except KeyboardInterrupt:
        log_info("Keyboard interrupt received")
        print("\n⚠️  Interrupted by user")

    except Exception as e:
        log_error(f"Unexpected error in main loop: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        log_info("Shutting down...")
        print("\n👋 Shutting down β-bot...")

        try:
            game_manager.cleanup()
        except Exception as e:
            log_error(f"Error during cleanup: {e}")

        pygame.quit()
        log_info("β-bot shutdown complete")
        log_info("=" * 60)
        print("✅ Goodbye!\n")


if __name__ == "__main__":
    main()