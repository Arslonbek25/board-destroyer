# Board Destroyer

## Description

Board Destroyer is an intelligent automation tool that plays browser-based chess games on your behalf. It combines the power of YOLO for real-time chess piece detection and Stockfish for advanced board analysis and move planning. The project supports the default chess set from Chess.com and works best with the green theme.

## Features

- **Universal Compatibility**: Seamlessly integrates with any browser-based chess game.
- **YOLO-Powered**: Uses YOLO for precise and rapid chess piece identification.
- **Stockfish Engine**: Employs Stockfish for in-depth board analysis and optimal move selection.

## How to Use

1. Install the necessary dependencies by running `pip install -r requirements.txt`.
2. Activate the virtual environment.
3. Download and install the binary version of the Stockfish engine from the [official website](https://stockfishchess.org/download/). Ensure that it is added to your system's PATH.
4. Run `src/main.py`.
5. Open your favorite browser-based chess game.
6. Sit back and watch Board Destroyer dominate the board for you.

## Configuration

Time control and engine settings can be customized by editing the `config.py` file. Please refer to the file for more details on the available options and how to change them.

## License

MIT License

Contributions and issue reporting are welcome.
