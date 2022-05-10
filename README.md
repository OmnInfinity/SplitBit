# SplitBit

## Instructions

### Build
  1. Check that the NanoVNA Saver is installed in the path right above this project so that Python can access it somehow for imports
  2. Check that the </nanovnacmd.py> script from Kevin O'Brien is up-to-date (the current version as of writing is included here in this repo)
  3. Check for any uninstalled dependencies, running `pip` as needed, when running the program

### Execution
  1. Connect NanoVNA to a port and you may need to enable access to said device (i.e. run `sudo chmod 666 /dev/ttyACM0` or whatever block device path it is to allow permissions to access, on Linux)
  2. Run </splitBit.py> for the refactored and cleaned up version (or the </splitBitDemo.py> for the original used in the final presentation demo)
  3. Calibrate the first stage if not already done through the program
  4. Wait for the second stage of calibration to complete, leaving the antenna in a steady state
  5. "Run" with the ID so that it moves across the antenna's field path and registers it as an edge for crossing, used to trigger the stopwatch (can later be configured for a more specific resonant frequency for tracking different objects, or even across multiple antennas to produce "start" and "end" points for a track)

