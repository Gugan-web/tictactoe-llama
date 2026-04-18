# TicTacToeAI

A desktop Tic-Tac-Toe game built with Python and Tkinter, powered by a local AI opponent through `autogen` and Ollama.

The app gives you a clean graphical board, lets you enter your name, randomly assigns symbols, and plays against an AI that chooses its next move from the current board state.

## Features

- Simple Tkinter desktop interface
- Human vs AI gameplay
- Local AI opponent using Ollama
- Randomized starting player each round
- Randomized player symbol assignment (`X` or `O`)
- Restart button for quick replay
- Background AI move generation so the GUI stays responsive

## How It Works

The game UI is implemented in [`tictactoe_gui.py`](/d:/TicTacToeAI/tictactoe_gui.py).  
When it is the AI's turn, the current board is converted into a prompt and sent to an `autogen.ConversableAgent`, which calls a local Ollama model running at:

`http://localhost:11434/v1`

The current code is configured to use:

`llama3.2`

If the model response is invalid or unusable, the app safely falls back to a random valid move.

## Project Structure

```text
TicTacToeAI/
|-- tictactoe_gui.py
|-- requirements.txt
`-- README.md
```

## Requirements

Before running the project, make sure you have:

- Python 3.10 or newer recommended
- Ollama installed locally
- The `llama3.2` model downloaded in Ollama

Tkinter is included with most standard Python installations, especially on Windows.

## Installation

1. Clone or download this project.
2. Create and activate a virtual environment.
3. Install the Python dependencies.
4. Start Ollama.
5. Pull the required model.
6. Run the app.

Example setup:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.2
ollama serve
python tictactoe_gui.py
```

## Usage

1. Launch the application.
2. Enter your name.
3. Click a square to place your move.
4. Wait for the AI to respond.
5. Press `Restart` to start a new round.

At the beginning of each game:

- You may be assigned either `X` or `O`
- Either you or the AI may go first

## Dependencies

The project currently lists these packages in [`requirements.txt`](/d:/TicTacToeAI/requirements.txt):

- `streamlit`
- `chess==1.11.1`
- `autogen==0.6.1`
- `cairosvg`
- `pillow`

For the current GUI app, the key dependency is `autogen`. Some listed packages may be leftovers from earlier experiments or future ideas and are not directly used by `tictactoe_gui.py` right now.

## Troubleshooting

### AI does not move

Check that:

- Ollama is installed
- Ollama is running
- The `llama3.2` model has been pulled
- Ollama is available at `http://localhost:11434/v1`

### Import errors

Make sure your virtual environment is activated and dependencies were installed successfully:

```powershell
pip install -r requirements.txt
```

### Tkinter does not open

Use a standard Python installation that includes Tkinter. On most Windows Python installs, this is available by default.

## Notes

- The AI is local-first and does not require a cloud API key in the current setup.
- The application uses threads so the window stays responsive while the AI is "thinking".
- If you want to change the AI model, update the `ollama_config` inside [`tictactoe_gui.py`](/d:/TicTacToeAI/tictactoe_gui.py).

