# Board Destroyer

## Description

Board Destroyer is an intelligent automation tool that plays browser-based chess games on your behalf. It combines the power of YOLO for real-time chess piece detection and Stockfish for advanced board analysis and move planning. The project supports the default chess set from Chess.com and works best with the green theme.

## Compatibility

This project has been tested on MacOS Sonoma. It does not work on other operating systems.

## Features

- **Universal Compatibility**: Seamlessly integrates with any chess website.
- **YOLO-Powered**: Uses YOLO for precise and rapid chess piece identification.
- **Stockfish**: Employs Stockfish for in-depth board analysis and optimal move selection.
- **Customizable Settings**: Time control and engine settings can be customized through the UI.


## How to Use

1. Activate the virtual environment.
2. Install the necessary dependencies by running `pip install -r requirements.txt`.
3. Download and install the binary version of the Stockfish engine from the [official website](https://stockfishchess.org/download/). Make absolutely sure that it is added to your system's PATH so that it can be accessed by running 'stockfish' on the terminal. You should receive output when you run stockfish on terminal.
5. Open your preferred chess website, such as Chess.com or Lichess. If using Chess.com, ensure the default green theme is selected and set piece animations to "None" in the Chess.com settings.
4. With venv activated, run `src/app.py`.
6. Click the start button on the UI that pops up, sit back and watch Board Destroyer dominate the board for you.

## Troubleshooting

If the software does not run for some reason, it is due to an installation or configuration issue. The software has been thoroughly tested and works as expected on MacOS Sonoma. Make sure all steps are followed correctly.

## License

MIT License

Contributions and issue reporting are welcome.
