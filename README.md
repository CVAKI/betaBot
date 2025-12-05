# beta Bot- Chess
Core Architecture Overview
Hierarchical Decision-Making System:
16 independent AI agents (pieces) with varying IQ levels
Queen as strategic coordinator (IQ: 9.0-9.99)
King as final approver with veto power (3 denials max) (IQ: 8.0-8.99)
Pieces propose moves → Queen synthesizes strategy → King approves/denies
Technical Stack Implementation
1. AI/ML Components
TensorFlow: Neural networks for move evaluation per piece
PyTorch: Reinforcement learning for piece coordination
LLM Integration: For natural language communication between pieces (consider using a lightweight model like GPT-2 or a fine-tuned small LLM)
2. IQ Level Ranges
Queen:  9.0 ≤ IQ < 10.0
King:   8.0 ≤ IQ < 9.0
Knight: 7.0 ≤ IQ < 8.0
Bishop: 6.0 ≤ IQ < 7.0
Rook:   5.0 ≤ IQ < 6.0
Pawn:   1.0 ≤ IQ < 5.0
3. Game Flow Architecture
1. Each piece analyzes board → generates move suggestions
2. Pieces communicate with nearby pieces (adjacency-based)
3. All suggestions sent to Queen
4. Queen evaluates strategies → selects best move
5. King reviews → Approve/Deny (tracks denial count)
6. If denied: Queen reconsiders from all previous + current suggestions
7. After 3 denials: King must approve or choose from history
Key Implementation Considerations
Pygame Structure
Main game board rendering
Chat panel (side/bottom display)
Piece sprites with your custom assets
Emotion emoji overlay on pieces
Communication System
Proximity Chat: Pieces can only talk to adjacent squares (or within 2-3 squares)
Queen Channel: All pieces can report to Queen
Chat Log: Display real-time conversations with timestamps and emojis
Neural Network Design
Each piece needs:
Input: Board state (64 squares + piece positions)
Hidden layers: Scaled by IQ level (higher IQ = deeper networks)
Output: Move probabilities + confidence score
Personality & Emotion System
Map game states to emotions:
Under threat → 😰😭😱
Sacrifice situation → 😔🫡
Successful capture → 😊😤
Supporting teammate → 🤝💪
Suggested Project Structure
β-bot/
├── main.py                 # Game loop
├── chess_engine/
│   ├── board.py           # Chess rules
│   ├── piece_base.py      # Base piece class
│   └── pieces/            # Individual piece AI
│       ├── queen.py
│       ├── king.py
│       ├── knight.py
│       └── ...
├── ai_brain/
│   ├── neural_net.py      # TensorFlow/PyTorch models
│   ├── decision_maker.py  # Queen's strategy synthesis
│   └── llm_chat.py        # LLM integration for dialogue
├── ui/
│   ├── board_renderer.py  # Pygame board
│   ├── chat_display.py    # Chat interface
│   └── assets/            # Your sprites/images
└── utils/
    ├── emotion_mapper.py  # Emotion → Emoji
    └── communication.py   # Piece-to-piece messaging
Challenges to Consider
Performance: Running 16 neural networks simultaneously may be computationally expensive
LLM Integration: Real-time text generation might cause delays; consider caching common phrases
Training: You'll need to train each piece type's network with different complexity levels
Balancing: Ensuring the bot plays reasonably well while maintaining the "debate" feature
Next Steps Recommendation
Would you like me to create:
A starter code framework with the class hierarchy?
A specific component (like the Queen's decision synthesizer)?
The Pygame UI layout with chat integration?
The neural network architecture for different piece types? 
This is a fascinating project that combines game AI, multi-agent systems, and creative personality simulation! 🎮🤖  β-bot: Autonomous Chess AI with Hierarchical Multi-Agent Decision System
Project Overview
β-bot is an innovative Python-based chess engine that revolutionizes traditional chess AI by implementing a decentralized, multi-agent decision-making architecture. Unlike conventional chess bots that operate as a single computational entity, β-bot assigns independent "brains" to each of the 16 chess pieces, creating a collaborative AI ecosystem where pieces think, communicate, and strategize collectively.
Core Concept
The project introduces a unique hierarchical governance model inspired by organizational decision-making structures:
Distributed Intelligence Architecture
Each chess piece operates as an autonomous agent with its own neural network "brain," capable of:
Analyzing the current board state independently
Generating move suggestions based on its tactical understanding
Communicating with nearby pieces and the command hierarchy
Expressing emotions and personality through dialogue
Hierarchical Decision-Making Process
Piece-Level Analysis: All 16 pieces simultaneously evaluate the board and propose potential moves
Lateral Communication: Pieces discuss strategies with adjacent teammates, forming micro-consensus
Strategic Synthesis: The Queen receives all suggestions and synthesizes them into coherent strategic options
Executive Approval: The King reviews the Queen's decision with veto power (limited to 3 denials)
Final Execution: After approval or exhaustion of veto rights, the chosen move is executed
Intelligence Hierarchy
β-bot implements a sophisticated IQ-based cognitive stratification system:
Piece Type
IQ Range
Strategic Role
Queen
9.0 - 9.99
Master Strategist & Decision Synthesizer
King
8.0 - 8.99
Executive Validator & Final Authority
Knight
7.0 - 7.99
Tactical Specialist
Bishop
6.0 - 6.99
Positional Analyst
Rook
5.0 - 5.99
Structural Coordinator
Pawn
1.0 - 4.99
Frontline Scout & Sacrifice Unit
The IQ levels directly influence:
Neural network complexity (depth and layer count)
Strategic thinking capability
Communication sophistication
Risk assessment accuracy
Technical Innovation
Multi-Agent AI Framework
TensorFlow: Powers individual piece neural networks for move evaluation
PyTorch: Manages reinforcement learning for inter-piece coordination
LLM Integration: Enables natural language communication between pieces, creating personality-driven dialogue
Emotional Intelligence System
Pieces exhibit context-aware emotional responses displayed through emojis:
Under threat: 😭😰😱 (fear, anxiety)
Sacrifice situations: 😔🫡 (resignation, duty)
Victory moments: 😊😤💪 (joy, pride)
Team support: 🤝🫂 (solidarity, encouragement)
Real-Time Communication Interface
A dynamic chat panel displays piece-to-piece conversations:
Pawn[1]: (😭) Am I going to die?
Knight[Right]: (😔) Sacrifice for us, Pawn[1]!
Pawn[1]: (🙂‍↕) Alright! For the team!
Queen: (👑) Your bravery is noted. Advance to e4.
King: (✅) Approved. Execute.
Governance Protocol
The Veto System
The King possesses limited executive power:
3 Denial Rights: Can reject the Queen's decisions up to three times
Post-Veto Obligation: After exhausting denials, must approve subsequent decisions OR select from previous suggestions
Decision History: All denied strategies remain in the selection pool
This creates dynamic tension between tactical caution (King) and strategic ambition (Queen).
User Experience Features
Visual Interface (Pygame)
Custom piece sprites and assets
Dual-panel layout: chess board + live chat window
Emoji overlays on pieces showing current emotional state
Move animation and highlight effects
Transparency & Entertainment
Players can observe:
Internal AI deliberations in real-time
Piece personality dynamics (fearful pawns, aggressive knights)
Strategic debates between Queen and King
Emotional reactions to game events
Unique Value Proposition
β-bot transforms chess from a computational problem into a social simulation, where victory isn't just about optimal moves, but about:
Effective communication between agents
Hierarchical decision-making under pressure
Balancing individual piece survival with team objectives
Managing limited executive veto power strategically
Technical Challenges & Solutions
Computational Load: 16 simultaneous neural networks → optimized inference pipelines
Real-time LLM Generation: Cached dialogue templates with dynamic variable insertion
Training Complexity: Piece-specific training datasets reflecting IQ stratification
Game Balance: Ensuring the "debate" mechanism doesn't compromise competitive play
Future Potential
Multi-player variant: Human players command different pieces
Personality customization: Users define piece character traits
Tournament mode: β-bot teams with different "political structures"
Educational tool: Teaching hierarchical decision-making and AI coordination # β-bot File Purpose Documentation

## 📁 Root Directory Files

### *main.py*
Purpose: Application entry point and main game loop orchestrator
- Initializes all game systems (Pygame, AI brains, UI components)
- Runs the primary game loop handling events, updates, and rendering
- Coordinates frame rate and timing
- Manages game state transitions (menu → game → end screen)
- Handles graceful shutdown and cleanup

### *config.py*
Purpose: Centralized configuration and constant definitions
- Defines IQ ranges for each piece type (Queen: 9.0-9.99, King: 8.0-8.99, etc.)
- Screen resolution and UI layout constants
- Color schemes (board colors, UI colors, text colors)
- Neural network hyperparameters (layer sizes, learning rates)
- Game rules constants (board size: 8x8, piece counts)
- File paths for assets and models
- LLM API keys and endpoints

### *requirements.txt*
Purpose: Python dependency specification
- Lists all required Python packages with version numbers
- Ensures reproducible environment setup
- Used by pip for automatic installation: pip install -r requirements.txt
- Includes: pygame, tensorflow, pytorch, transformers, numpy, etc.

### *README.md*
Purpose: Project documentation and user guide
- Project overview and concept explanation
- Installation instructions
- Usage guidelines
- Feature descriptions
- Contribution guidelines
- License information
- Credits and acknowledgments

---

## 🎨 assets/ - Visual and Audio Resources

### *assets/pieces/white/ & assets/pieces/black/*
Purpose: Chess piece sprite images
- Individual PNG files for each piece type (king, queen, rook, bishop, knight, pawn)
- Separate folders for white and black pieces
- Used by piece_renderer.py to display pieces on the board
- Recommended size: 64x64 or 128x128 pixels with transparency

### *assets/board/*
- *board_background.png*: The chess board grid background (alternating light/dark squares)
- *square_highlight.png*: Transparent overlay for highlighting selected squares
- *move_indicator.png*: Visual markers showing legal move destinations

### *assets/ui/*
- *chat_panel_bg.png*: Background texture for the chat interface panel
- *button_approve.png*: King's "Approve" button graphic
- *button_deny.png*: King's "Deny" button graphic  
- *crown_icon.png*: Decorative icon for hierarchical indicators

### *assets/emojis/*
Purpose: Emotion visualization sprites
- Individual emoji images (happy.png, sad.png, scared.png, confident.png, neutral.png)
- Displayed as overlays on pieces to show their emotional state
- Mapped from emotion types in emotion_engine.py
- Size: 24x24 or 32x32 pixels recommended

### *assets/sounds/* (Optional)
- *move.wav*: Sound effect when a piece moves
- *capture.wav*: Sound effect when a piece is captured
- *chat_notification.wav*: Sound when new chat message appears

---

## ♟ chess_engine/ - Core Chess Logic

### *_init_.py*
Purpose: Makes the directory a Python package
- Allows importing modules from this directory
- Can contain package-level initialization code
- May expose commonly used classes/functions for easier importing

### *board.py*
Purpose: Chess board representation and state management
- Maintains 8x8 grid data structure representing piece positions
- Tracks which squares are occupied and by which pieces
- Provides methods to get/set piece positions
- Handles board rotation for different player perspectives
- Stores captured pieces list
- Example methods: get_piece_at(row, col), move_piece(from_pos, to_pos), is_square_empty(pos)

### *move.py*
Purpose: Move representation and validation
- Defines Move class containing: start position, end position, piece type, special flags
- Handles special moves: castling, en passant, pawn promotion
- Validates move syntax and format
- Converts between algebraic notation (e4, Nf3) and coordinate notation
- Methods: is_valid(), to_algebraic(), from_algebraic()

### *game_state.py*
Purpose: Complete game state management
- Tracks whose turn it is (white/black)
- Stores move history for the entire game
- Manages game phase (opening, midgame, endgame)
- Tracks castling rights for both sides
- En passant eligibility tracking
- Stores King veto count (0-3)
- Provides undo/redo functionality
- Methods: get_current_player(), switch_turn(), add_to_history(move)

### *rules.py*
Purpose: Chess rule enforcement engine
- Generates all legal moves for a given piece
- Check detection: determines if King is in check
- Checkmate detection: determines if game is over
- Stalemate detection: determines if no legal moves available
- Validates special move legality (castling through check, etc.)
- Pin detection: pieces that cannot move because they'd expose King
- Methods: get_legal_moves(piece), is_in_check(color), is_checkmate(color)

---

## 🧠 ai_brain/ - AI and Neural Network Systems

### *_init_.py*
Purpose: AI module package initialization

### *neural_network.py*
Purpose: Base neural network architecture definition
- Defines abstract neural network class used by all pieces
- Implements forward propagation logic
- Configurable layer sizes based on IQ level
- Input: Board state (64 squares × piece type encoding = ~768 features)
- Output: Move probabilities + confidence score
- Higher IQ = more layers and neurons (Queen: 5-6 layers, Pawn: 2-3 layers)

### *piece_brain.py*
Purpose: Individual piece AI brain wrapper
- Wraps neural network with piece-specific behavior
- Loads appropriate pre-trained model based on piece type
- Processes board state into neural network input format
- Converts neural network output into move suggestions
- Includes exploration vs exploitation logic (epsilon-greedy)
- Methods: suggest_move(board_state), evaluate_position(board_state), get_confidence()

### *training/trainer.py*
Purpose: Training orchestration for all piece models
- Manages training loops for each piece type separately
- Implements reinforcement learning algorithms (Q-learning, Policy Gradient)
- Handles batch training data processing
- Saves model checkpoints periodically
- Logs training metrics (loss, accuracy, win rate)
- Supports transfer learning from stronger pieces to weaker ones

### *training/data_generator.py*
Purpose: Generates training data for neural networks
- Creates synthetic chess positions for training
- Simulates games between pieces at different skill levels
- Extracts board states and optimal moves from chess databases
- Augments data with rotations and reflections
- Balances dataset across different game phases
- Methods: generate_positions(count), simulate_game(), extract_from_pgn()

### *training/models/ (Directory)*
Purpose: Storage for trained neural network models
- Contains saved PyTorch .pth files for each piece type
- Organized by piece type: queen_model.pth, king_model.pth, etc.
- Version controlled to track model improvements
- Loaded by piece_brain.py during game initialization

### *decision_maker.py*
Purpose: Queen's strategic synthesis engine
- Receives move suggestions from all 16 pieces
- Evaluates each suggestion's strategic value
- Considers piece coordination and synergy
- Weights suggestions by piece IQ and position importance
- Synthesizes multiple suggestions into coherent strategy
- Generates explanation for chosen move (for chat display)
- Methods: synthesize_strategy(all_proposals), evaluate_synergy(), generate_explanation()

### *king_validator.py*
Purpose: King's approval/veto logic system
- Reviews Queen's proposed move against safety criteria
- Evaluates risk level of proposed strategy
- Implements veto decision algorithm (IQ: 8.0-8.99)
- Tracks veto count (max 3 denials)
- After 3 vetoes: selects best option from history OR approves current
- Generates reasoning for approval/denial (for chat display)
- Methods: validate_move(queen_decision), assess_risk(), select_from_history()

### *move_evaluator.py*
Purpose: Board position evaluation utilities
- Calculates positional advantage score
- Material counting (pawn=1, knight=3, bishop=3, rook=5, queen=9)
- Positional factors: piece activity, king safety, pawn structure
- Used by all piece brains to assess board state
- Methods: evaluate_board(board_state), calculate_material(), assess_king_safety()

---

## 💬 llm_integration/ - Language Model for Communication

### *_init_.py*
Purpose: LLM module package initialization

### *llm_client.py*
Purpose: LLM API wrapper and connection manager
- Connects to OpenAI API, Hugging Face, or local LLM server
- Handles authentication and API key management
- Implements retry logic for failed requests
- Rate limiting to avoid API quota exhaustion
- Error handling for network issues
- Methods: generate_response(prompt), check_connection(), set_model(model_name)

### *dialogue_generator.py*
Purpose: Generates contextual piece conversations
- Creates prompts for LLM based on game situation
- Includes piece personality traits in prompts
- Formats responses into chat message format
- Assigns appropriate emotions to generated text
- Handles different conversation types: piece-to-piece, piece-to-Queen, Queen-to-King
- Methods: generate_piece_dialogue(piece, context), format_chat_message(), determine_emotion()

### *prompt_templates.py*
Purpose: Pre-defined LLM prompt templates
- Stores reusable prompt structures for common situations
- Templates for: move suggestion, sacrifice discussion, celebration, fear expression
- Includes personality parameters: bravery, loyalty, tactical awareness
- Example template: "You are {piece_type} with IQ {iq_level}. The board situation is {context}. Express your thoughts on {topic} in {tone}."
- Reduces repetitive prompt construction
- Methods: get_template(template_name), fill_template(template, variables)

### *cache_manager.py*
Purpose: Caches common LLM responses for performance
- Stores frequently generated responses in memory/disk
- Reduces API calls and latency
- Implements cache invalidation strategies
- Handles cache size limits
- Useful for common phrases: "Yes, Your Majesty", "I'm ready to sacrifice", "Danger ahead!"
- Methods: get_cached_response(key), cache_response(key, value), clear_cache()

---

## ♟ pieces/ - Individual Piece Agent Classes

### *_init_.py*
Purpose: Pieces module package initialization

### *base_piece.py*
Purpose: Abstract base class for all chess pieces
- Defines common properties: position, color, IQ level, piece type, has_moved
- Common methods all pieces share: get_position(), set_position(), get_iq()
- Abstract methods subclasses must implement: suggest_move(), generate_dialogue()
- Handles communication interface with other pieces
- Manages piece's neural network brain
- Tracks piece's current emotion state

### *queen.py*
Purpose: Queen agent implementation (IQ: 9.0-9.99)
- Inherits from base_piece.py
- Implements strategic synthesis logic
- Receives and processes all piece suggestions
- Generates comprehensive strategic plans
- Communicates decisions to King
- Has authority to command all other pieces
- Personality traits: Confident, strategic, commanding

### *king.py*
Purpose: King agent implementation (IQ: 8.0-8.99)
- Inherits from base_piece.py
- Implements approval/veto logic
- Reviews Queen's decisions for safety
- Manages veto counter (0-3)
- Has final decision authority
- Prioritizes safety over aggression
- Personality traits: Cautious, wise, protective

### *knight.py*
Purpose: Knight agent implementation (IQ: 7.0-7.99)
- Inherits from base_piece.py
- Specialized in tactical jumping maneuvers
- Evaluates fork opportunities (attacking multiple pieces simultaneously)
- Suggests unconventional tactical moves
- Personality traits: Tactical, agile, opportunistic

### *bishop.py*
Purpose: Bishop agent implementation (IQ: 6.0-6.99)
- Inherits from base_piece.py
- Focuses on diagonal control and long-range positioning
- Evaluates diagonal pressure and fianchetto positions
- Suggests positional strategic moves
- Personality traits: Positional, patient, analytical

### *rook.py*
Purpose: Rook agent implementation (IQ: 5.0-5.99)
- Inherits from base_piece.py
- Focuses on file/rank control and structural play
- Suggests open file occupation
- Coordinates with other rook for doubled rooks
- Personality traits: Structural, powerful, straightforward

### *pawn.py*
Purpose: Pawn agent implementation (IQ: 1.0-4.99)
- Inherits from base_piece.py
- Simplest decision-making logic
- Often expresses fear when threatened
- Willing to sacrifice for team
- Dreams of promotion to Queen
- Personality traits: Brave, expendable, hopeful

---

## 📡 communication/ - Inter-Piece Communication System

### *_init_.py*
Purpose: Communication module package initialization

### *message.py*
Purpose: Message data structure definition
- Defines Message class with fields: sender, recipient(s), content, timestamp, emotion
- Message types: suggestion, agreement, concern, celebration, question
- Serialization methods for logging
- Priority levels for urgent messages
- Example fields: from_piece, to_piece, message_text, emotion_emoji, timestamp

### *communication_hub.py*
Purpose: Central message routing system
- Acts as message broker between all pieces
- Routes messages based on recipient
- Implements Queen's broadcast channel (Queen can message all pieces)
- Implements King's private channel with Queen
- Queues messages for sequential processing
- Methods: send_message(message), broadcast(sender, content), get_messages_for(piece)

### *proximity_manager.py*
Purpose: Determines which pieces can communicate
- Calculates spatial relationships between pieces
- Defines proximity rules (adjacent squares, within 2-square radius, etc.)
- Allows nearby pieces to have "side conversations"
- Enforces that distant pieces cannot directly communicate (must go through Queen)
- Methods: are_pieces_adjacent(piece1, piece2), get_nearby_pieces(piece), can_communicate(piece1, piece2)

### *chat_logger.py*
Purpose: Logs all communications for display and analysis
- Records every message sent between pieces
- Formats messages for chat panel display
- Timestamps all communications
- Stores conversation history
- Provides search/filter functionality
- Methods: log_message(message), get_chat_history(), filter_by_piece(piece_name), export_log()

---

## 😊 emotion/ - Emotional Intelligence System

### *_init_.py*
Purpose: Emotion module package initialization

### *emotion_engine.py*
Purpose: Maps game states to emotional responses
- Analyzes current board state to determine piece emotions
- Factors considered: piece under threat, piece about to capture, piece supporting teammate, piece isolated
- Intensity calculation (mild concern vs. extreme fear)
- Context-aware emotion assignment (pawn sacrifice = 😔, queen capture = 😭)
- Updates piece emotions every turn
- Methods: determine_emotion(piece, game_state), calculate_threat_level(), assess_isolation()

### *emotion_types.py*
Purpose: Emotion enumeration definitions
- Defines all possible emotion states as enum
- Example emotions: HAPPY, SAD, SCARED, CONFIDENT, ANGRY, NEUTRAL, ANXIOUS, PROUD, RESIGNED
- Each emotion has: name, intensity level, display color
- Used throughout the system for type-safe emotion handling
- Example: Emotion.SCARED, Emotion.CONFIDENT

### *emoji_mapper.py*
Purpose: Maps emotions to emoji representations
- Converts emotion enums to visual emoji characters/sprites
- Mapping examples: HAPPY → 😊, SCARED → 😰, CONFIDENT → 😤, RESIGNED → 😔
- Loads emoji sprites from assets/emojis/
- Provides fallback text emojis if sprites unavailable
- Methods: get_emoji_for_emotion(emotion), load_emoji_sprite(emotion_name)

---

## 🎮 ui/ - Pygame User Interface

### *_init_.py*
Purpose: UI module package initialization

### *game_window.py*
Purpose: Main game window manager
- Initializes Pygame display window
- Manages window title, icon, and size
- Handles window events (close, minimize, resize)
- Coordinates rendering order (board → pieces → UI → chat)
- Manages screen layout: board area vs. chat panel area
- Methods: initialize(), handle_events(), render_all(), close()

### *board_renderer.py*
Purpose: Chess board rendering system
- Draws the 8x8 chess board grid
- Alternates light and dark square colors
- Draws coordinate labels (a-h, 1-8)
- Highlights selected squares
- Shows legal move indicators
- Renders move history annotations on board
- Methods: draw_board(), highlight_square(pos), draw_coordinates(), show_legal_moves()

### *chat_panel.py*
Purpose: Chat interface display component
- Renders chat panel background
- Displays scrollable message history
- Formats messages with: sender name, emoji, timestamp, message text
- Auto-scrolls to newest messages
- Color-codes messages by sender type (Queen = gold, King = purple, etc.)
- Handles chat panel resizing
- Methods: draw_chat_panel(), add_message(message), scroll_to_bottom(), update()

### *piece_renderer.py*
Purpose: Piece sprite rendering with emotional overlays
- Loads piece sprites from assets
- Renders pieces at correct board positions
- Draws emotion emoji overlays on pieces
- Handles piece selection highlighting
- Animates piece emotions (subtle bounce, glow effects)
- Scales sprites appropriately for board size
- Methods: draw_piece(piece, position), draw_emotion_overlay(piece), highlight_selected_piece()

### *move_animator.py*
Purpose: Move animation handler
- Smoothly animates piece movement from source to destination
- Implements easing functions (ease-in, ease-out)
- Handles capture animations (fading out captured piece)
- Animates special moves (castling shows both King and Rook moving)
- Manages animation timing and frame updates
- Methods: animate_move(piece, from_pos, to_pos), animate_capture(), is_animating()

### *button.py*
Purpose: UI button component class
- Creates clickable button UI elements
- Handles hover effects (color change, border highlight)
- Detects mouse clicks on button area
- Renders button text and icons
- Used for: Approve/Deny buttons, Reset game, Settings, etc.
- Methods: draw(), is_clicked(mouse_pos), set_enabled(bool)

### *text_renderer.py*
Purpose: Text and font rendering utilities
- Loads and manages fonts (title font, chat font, UI font)
- Renders text with anti-aliasing
- Supports multi-line text wrapping
- Text alignment (left, center, right)
- Shadow/outline effects for readability
- Methods: render_text(text, font, color, pos), wrap_text(text, width), draw_multiline()

---

## 🔧 utils/ - Utility Functions and Helpers

### *_init_.py*
Purpose: Utils module package initialization

### *logger.py*
Purpose: Logging configuration and management
- Configures Python logging system
- Sets log levels (DEBUG, INFO, WARNING, ERROR)
- Creates separate log files for different subsystems
- Formats log messages with timestamps
- Rotates log files to prevent excessive size
- Methods: setup_logger(name), log_info(message), log_error(exception)

### *position.py*
Purpose: Position and coordinate utilities
- Converts between different coordinate systems: algebraic (e4) ↔ array indices (4,4) ↔ pixel coordinates (320, 240)
- Validates position legality (within 8x8 board)
- Calculates distances between positions
- Determines relative positions (north, south, diagonal, etc.)
- Methods: algebraic_to_index(notation), index_to_pixel(row, col), get_distance(pos1, pos2)

### *color_manager.py*
Purpose: Color constants and management
- Defines all color constants used in UI
- Board colors: LIGHT_SQUARE, DARK_SQUARE
- Piece colors: WHITE, BLACK
- UI colors: BACKGROUND, TEXT, HIGHLIGHT, BUTTON_HOVER
- Provides color utility functions
- Methods: get_color(name), lighten(color, amount), darken(color, amount)

### *timer.py*
Purpose: Game timing utilities
- Tracks frame rate for smooth animation
- Implements turn timers (optional time control)
- Measures AI thinking time
- Provides delay/sleep functions
- FPS counter for performance monitoring
- Methods: get_elapsed_time(), start_timer(), wait(milliseconds), get_fps()

### *save_load.py*
Purpose: Save and load game state functionality
- Serializes game state to JSON/pickle format
- Saves: board position, move history, piece emotions, chat log, veto count
- Loads saved games for replay or continuation
- Validates loaded data integrity
- Implements versioning for save file compatibility
- Methods: save_game(filename, game_state), load_game(filename), export_pgn()

---

## 🎯 game_logic/ - High-Level Game Orchestration

### *_init_.py*
Purpose: Game logic module package initialization

### *game_manager.py*
Purpose: Main game flow controller
- Orchestrates overall game execution
- Manages game states: MENU, PLAYING, PAUSED, GAME_OVER
- Initializes all subsystems (AI, UI, communication)
- Handles game reset and new game creation
- Coordinates between chess engine, AI, and UI
- Implements game loop logic
- Methods: initialize_game(), run_game_loop(), reset_game(), end_game()

### *turn_manager.py*
Purpose: Turn-based logic coordinator
- Manages whose turn it is (white/black)
- Enforces turn order
- Triggers AI decision process at start of each turn
- Handles turn timeout (if time controls enabled)
- Switches turns after move execution
- Updates turn counter
- Methods: start_turn(), end_turn(), get_current_player(), increment_turn_count()

### *decision_pipeline.py*
Purpose: Piece → Queen → King decision pipeline
- Stage 1: Collects move suggestions from all 16 pieces
- Stage 2: Facilitates proximity-based piece discussions
- Stage 3: Queen synthesizes suggestions into strategy
- Stage 4: King validates and approves/denies
- Stage 5: If denied, loop back with constraints
- Stage 6: Execute approved move
- Manages pipeline state and error handling
- Methods: execute_pipeline(), collect_proposals(), synthesize(), validate(), execute()

### *history_tracker.py*
Purpose: Move and decision history tracking
- Records every move made in the game
- Stores Queen's rejected strategies (for King's review after 3 vetoes)
- Tracks King's veto count and reasons
- Enables move replay and analysis
- Supports undo/redo functionality
- Provides game summary statistics
- Methods: add_move(move), add_denied_strategy(strategy), get_veto_history(), get_full_history()

---

## 🧪 tests/ - Unit and Integration Tests

### *_init_.py*
Purpose: Tests module package initialization

### *test_chess_engine.py*
Purpose: Tests for chess logic correctness
- Tests legal move generation for all piece types
- Validates check/checkmate detection
- Tests special moves: castling, en passant, promotion
- Verifies board state consistency
- Edge case testing (stalemate, repetition)

### *test_ai_brain.py*
Purpose: Tests for AI decision-making
- Tests neural network output validity
- Validates move suggestion quality
- Tests Queen's synthesis logic
- Tests King's veto logic
- Performance benchmarks for AI thinking time

### *test_communication.py*
Purpose: Tests for message passing system
- Tests message routing accuracy
- Validates proximity restrictions
- Tests broadcast channels
- Verifies message queue ordering
- Tests chat logging functionality

### *test_pieces.py*
Purpose: Tests for individual piece agents
- Tests each piece type's move suggestion logic
- Validates IQ-appropriate behavior
- Tests personality trait expression
- Verifies emotion assignment
- Tests piece-to-piece communication

### *test_ui.py*
Purpose: Tests for UI components
- Tests rendering performance
- Validates click detection on buttons
- Tests animation smoothness
- Verifies text wrapping and formatting
- Tests responsive layout

---

## 📊 data/ - Data Files and Configurations

### *piece_personalities.json*
Purpose: Defines personality traits per piece type
json
{
  "queen": {
    "confidence": 0.95,
    "leadership": 0.98,
    "aggression": 0.75,
    "dialogue_style": "commanding"
  },
  "pawn": {
    "confidence": 0.30,
    "bravery": 0.65,
    "loyalty": 0.90,
    "dialogue_style": "submissive"
  }
}


### *dialogue_templates.json*
Purpose: Pre-written dialogue snippets for variety
json
{
  "sacrifice_acceptance": [
    "For the kingdom! I'm ready!",
    "It's my honor to serve.",
    "Take care of my position..."
  ],
  "fear_expression": [
    "I sense danger approaching...",
    "This doesn't look good for me...",
    "Can anyone help me?"
  ]
}


### *emotion_mappings.json*
Purpose: Maps game situations to emotions
json
{
  "under_attack_high_value": "SCARED",
  "captured_enemy_piece": "PROUD",
  "supporting_ally": "CONFIDENT",
  "isolated": "ANXIOUS",
  "about_to_promote": "EXCITED"
}


### *iq_configurations.json*
Purpose: Neural network configurations per IQ level
json
{
  "queen": {
    "iq_range": [9.0, 9.99],
    "layers": [768, 512, 256, 128, 64],
    "dropout": 0.2,
    "learning_rate": 0.0001
  },
  "pawn": {
    "iq_range": [1.0, 4.99],
    "layers": [768, 128, 64],
    "dropout": 0.3,
    "learning_rate": 0.001
  }
}


---

## 📝 logs/ - Runtime Logs

### *logs/game_logs/*
Purpose: Stores game event logs
- Records each move with timestamp
- Logs AI decision-making steps
- Performance metrics (FPS, AI think time)
- Filename format: game_YYYY-MM-DD_HH-MM-SS.log

### *logs/chat_logs/*
Purpose: Stores conversation transcripts
- Complete chat history for each game
- Useful for analyzing piece communication patterns
- Can be replayed for entertainment
- Filename format: chat_YYYY-MM-DD_HH-MM-SS.txt

### *logs/error_logs/*
Purpose: Stores error and exception information
- Stack traces for debugging
- Warning messages
- Critical errors that caused crashes
- Filename format: error_YYYY-MM-DD.log

---

## 📓 notebooks/ - Jupyter Notebooks

### *model_training.ipynb*
Purpose: Interactive model training experimentation
- Visualize training progress with graphs
- Experiment with different hyperparameters
- Compare model performance across piece types
- Save best models for deployment

### *data_analysis.ipynb*
Purpose: Analyze game data and statistics
- Visualize piece communication patterns
- Analyze win/loss rates by strategy type
- Study emotion distribution during games
- Generate reports on AI behavior

### *testing_playground.ipynb*
Purpose: Interactive testing environment
- Test individual components in isolation
- Prototype new features
- Debug complex issues
- Quick experimentation without running full game

---

## 📚 docs/ - Additional Documentation

### *architecture.md*
Purpose: Detailed system architecture documentation
- High-level system design diagrams
- Component interaction flows
- Design decisions and rationale
- Technology stack justification

### *ai_design.md*
Purpose: AI system design specification
- Neural network architectures explained
- Training methodology
- IQ level implementation details
- Decision-making algorithms

### *communication_protocol.md*
Purpose: Inter-piece communication specification
- Message format definitions
- Communication rules and constraints
- Proximity rules explained
- Queen/King special channels

### *api_reference.md*
Purpose: API documentation for developers
- Class and method documentation
- Usage examples
- Parameter specifications
- Return value descriptions

---

## Summary of File Purposes by Category

| Category | Purpose |
|----------|---------|
| Root Files | Entry point, configuration, dependencies, documentation |
| assets/ | Visual sprites, UI graphics, emojis, sounds |
| chess_engine/ | Pure chess logic: board, moves, rules, validation |
| ai_brain/ | Neural networks, training, decision synthesis |
| llm_integration/ | Language model connectivity for dialogue |
| pieces/ | Individual piece agent implementations |
| communication/ | Message passing and chat system |
| emotion/ | Emotional intelligence and emoji mapping |
| ui/ | Pygame rendering and user interface |
| utils/ | Helper functions and shared utilities |
| game_logic/ | High-level game orchestration |
| tests/ | Automated testing and validation |
| data/ | Configuration files and personalities |
| logs/ | Runtime logs and conversation history |
| notebooks/ | Interactive development and analysis |
| docs/ | Additional technical documentation |

=======
# betaBot
>>>>>>> 2e64a07a7c16ee33f54c61cbc2e00969b5285994
