README
===============
Lauren Saunders

February 20, 2017

This repository contains various Python scripts and tools for running the He10
cryostat at Argonne National Laboratory.

Connection setup
----------------
Relevant Files:

- Driver files (xxxx.txt)

- lakeshore.py

- powersupply.py

- serial_connections.py

Currenty, we can connect to our power supplies and Lakeshore boxes through serial
connections. Each of these electronics boxes is plugged into a port on the MOXA
box, which runs a connection to the computer. However, because all power supplies
are different, we need to supply the computer an easy way to talk to these boxes.
This is done with driver files, which give a list of the remote interface commands,
as well as serial connection information, that can be used to communicate.

The driver files are stored as He4p.txt, He4s.txt, He3ICp.txt, He3ICs.txt,
He3UCp.txt, and He3UCs.txt.  Each driver file corresponds to one output on a
power supply, and takes the following format.  All of the keys in this list are
needed to make the connections and send the correct information, so it is important
to include all of them and ensure that the information matches that which your
power supply needs. In the case that a power supply does not take one of these keys
(i.e., if it only has one output), then the key can be set equal to None (note that
this is not the same as the parity option of none).

List of driver file keys:

  - port: the serial address of the power supply you are trying to acces

  - baudrate: the baud rate for the serial connection (9600)

  - parity: parity for the serial connection (odd, even, or none)

  - stopbits: the stop bits for the serial connection (none, 1, or 2)

  - bytesize: the number of bits for the serial connection (5, 6, 7, or 8)

  - timeout: a timeout for the serial connection (1)

  - term: termination character needed to end a command (\r\n)

  - v_ask: statement to query the voltage output

  - v_apply: statement to apply a voltage

  - select: statement to select the desired output

  - idn: statement to query the identification of the power supply

  - output_on: statement to turn on the output

  - remote: statement to set the power supply in remote mode

  - error_ask: statement to query errors

  - sep: separation character (for power supplies that require an output selection)

  - vmin: the output's minimum allowable voltage

  - vmax: the output's maximum allowable voltage

So, below, you will find an example of a driver file.
::
  port=/dev/ttyr12
  baudrate=9600
  parity=none
  stopbits=2
  bytesize=8
  timeout=1
  term=\r\n
  v_ask=MEAS:VOLT?
  v_apply=APPL
  select=INST:NSEL 2
  idn=*IDN?
  output_on=OUTP ON
  remote=SYST:REM
  error_ask=SYST:ERR?
  sep=;:
  vmin=0
  vmax=35


At present, the connections to the power supplies and PID heater are controlled
through two python modules, powersupply.py and lakeshore.py. Each of these
creates a class (PowerSupply or TempControl), which opens a serial connection to
the remote electronics. powersupply.py must also be supplied driver files
(.txt) which specify the type of connection and the remote interface commands.
Here, those driver files are stored as He4p.txt, He4s.txt, He3ICp.txt, He3ICs.txt,
He3UCp.txt, and He3UCs.txt.

The PowerSupply class is set up to retrieve text files from anl_fridge_control/control,
by the name of the text file. PowerSupply objects are called as such:

.. code:: python

  He4p = powersupply.PowerSupply('He4p.txt')

You can call as many or as few connections as you like; thus, you can use the
PowerSupply class for power supplies not normally involved in the He10 fridge
control (i.e., for sending current through a Helmholtz coil).

The serial_connections script establishes the power supply and ChaseLS class
objects.  Importing this script allows you to create a usable connection with
the power supplies and Lakeshore340 box via their serial ports; if you wish to
change the connections, you can do so by modifying the serial_connections script.

The PowerSupply class provides a number of functions for connecting with the
power supplies and troubleshooting problems.

  - who_am_i: asks the power supply to send its identification, and reads out
  this signal

    - Parameters: None

    - Returns: string of the power supply's identification

  - error: asks the power supply to send all errors in queue, and reads this out

    - Parameters: None

    - Returns: list of strings of errors

  - remote_set: sets the power supply to remote mode

    - Parameters: None

    - Returns: None

  - read_voltage: queries the power supply for the current voltage output, and
  reads back this message

    - Parameters: None

    - Returns: string of voltage output

  - set_voltage: sets the voltage to a specified number

    - Parameters: voltage (float)

    - Returns: None

  - set_vi: sets the voltage and current to specified numbers

    - Parameters: current (float), voltage (float)

    - Returns: None

If you want to send a query or command that is not one of the preset functions,
you can do so by accessing the serial connection (through the function serial_connex),
and writing the prompt that the power supply should be able to read.  For example,
if you wanted to know what the voltage you last set for the He4 pump was, you
could type

.. code:: python

  He4p.serial_connex.write('APPL?\r\n')
  He4p.serial_connex.readline()

The PowerSupply class is general enough to be used with a variety of power supplies,
provided you supply a driver file that includes all of the correct statements for
your specific power supply.

Similarly, the TempControl class provides a few ways of communicating with a
Lakeshore340 Temperature Controller:

  - set_PID_temp: sets the temperature of the heater for the UC Head

    - Parameters: loop (1), temperature (float, in Kelvin)

    - Returns: None

  - set_heater_range: sets the heater range, which controls power to the PID

    - Parameters: heater range (integer 0-5)

    -Returns: None

If you want to send a query or command that is not one of the preset functions,
you can do so with the connex function.  For example, if you wanted to query the
Celsius temperature for channel A, you could type

.. code:: python

  ChaseLS.connex.write('CRDG? A\r\n')
  ChaseLS.connex.readline()

Fridge logging
--------------
The fridge_logger_anl.py code (https://github.com/adamanderson/he10_fridge_control/blob/master/logger/fridge_logger_anl.py)
reads in data from Lakeshore340 and Lakeshore218 boxes. It then outputs data to
a .h5 file and a _read.h5 file, which are used to create plots and current
temperature readings on the website.

The fridge logger, as well as the web server that services it, are run in tmux sessions.
The steps for launching the fridge logger and monitoring temperatures are:

1. Open two tmux sessions by typing "tmux" into the terminal.

2. Attach to one of the tmux sessions by typing

.. code:: python

  tmux attach -t session_name

Then, in the session, type

.. code:: python

  python /home/spt3g/he10_fridge_control/logger/fridge_logger_anl.py

You will then be prompted for a filename, which should be inputted as

.. code:: python

  /home/spt3g/he10_logs/filename.h5

3. Leave the tmux session by typing Ctrl+B, then D.  Open the other tmux session,
and type

.. code:: python

  cd /home/spt3g/he10_fridge_control/website/

  python -m SimpleHTTPServer 8100

The fridge logger will now publish its read information to a local website, which
provides the most current measurements (a table that refreshes every few seconds)
and a plot of recent measurements (this needs to be refreshed in order to show
changes). The web page can be accessed at address localhost:8100.

Sometimes, the fridge logger encounters errors in reading the temperatures in
from the Lakeshore boxes. If this happens, the logger will print what the error
is, and will try 10 times to read back a valid response from the electronics.
This is done to prevent the code from crashing if a Lakeshore box sends an invalid
signal, which sometimes occurs.

Basic fridge control functions
------------------------------
The fridge control functions are generally found in anl_fridge_control/control.
Some functions are meant to be run from the terminal, and others need to be run
in an interactive Python session.  Before using any of the control code, ensure
that the power supplies and Lakeshore boxes are plugged in and powered on.

Generally in a cooldown, the first control code that you will need to run will be
to cycle the fridge. This allows the cooldown process to complete and the stage to
reach base temperature. Because this first cycle is slightly different from the
normal cycle that is run day-to-day, there is a separate Python script which controls it.
This script can be called as

.. code:: python

  python /home/spt3g/anl_fridge_control/control/first_cycle.py

The first thing that the first_cycle code does is prompt the user for a logfile.
This logfile should be the current temperature log (see the previous section for setup
procedures). After inputting the file name, the script will automatically run the cycle.
The script uses this logfile to check temperatures, using that information to
apply changes to voltages. At the end of the cycle, the power supplies will be applying
a voltage to each of the switches in order to keep the stage at base temperature.

Once the cryostat is at base temperature after the first cycle, there are a number
of important functions for cycling and changing temperatures. The first of these
is for running a cycle. In general, if the cryostat is being used to run tests,
it should be cycled no less than every other day. Heating and cooling using the
power supplies and PID heater will eventually cause the cryostat to lose the ability
to cool down to base temperature; however, cycling forces the helium to re-condense,
allowing the cryostat to cool to base again. To start a cycle, you can call the
following from the terminal.

.. code:: python

  python /home/spt3g/anl_fridge_control/control/autocycle.py

The script will first prompt the user for a logfile. This is the logfile output by
the temperature logger. It is generally best to input the version of the logfile
that ends with _read.h5. After this, the script will prompt the user for a
hardware map. The hardware map needs to be supplied in order to turn off the mezzanines.




Relevant files:

  - basic_functions.py

  - autocycle.py

  - first_cycle.py

basic_functions.py contains various functions for day-to-day fridge control.

- basic_functions.zero_everything: Turns all voltages to 0.00 V, and turns off the
PID heater.

  - Parameters: None

  - Returns: None

- basic_functions.start_of_day: Warms the UC Head to 650mK, then heats and tunes
SQUIDs and takes a rawdump.

  - Parameters: current temperature logfile, set_squid_feedback (default=False),
  set_gain (default=False)

    - The current logfile is whatever is created by the logger. You should be
    using the file called he10_logs/xxxx_read.h5
    - set_squid_feedback is a pydfmux call, which sets SQUID feedback if True
    - set_gain is a pydfmux call, which sets gain if True

  - Returns: some output directories for heating and tuning

  - At the end of start_of_day, the UC Head will be held at 650 mK, with the PID
  heater set to 650 mK at heater range 3 and He3 UC pump at 1.5 volts. If you
  want to lower the temperature, be sure to change the PID temperature and
  heater range as well as the He3 UC pump voltage.

  - It is suggested that the He3 UC pump voltage be set to 1.00 V if you want
    to sit at 600 mK, and be turned to 0.00 V if you are planning on moving to a
    lower temperature.

- basic_functions.finish_cycle: Runs the part of a cycle that waits for the heat exchanger temperature to rise and then cools the fridge to base.

  - Called by other scripts; can be called if you are manually calling part of
  the cycle (i.e. if something goes wrong midway through)

  - Parameters: current temperature logfile

    - The current logfile is whatever is created by the logger. You should be
    using the file called he10_logs/xxxx_read.h5

  - Returns: None

autocycle.py is a script that runs the day-to-day cycling code.  It should be
called from the command line.

- Parameters: None

-Raw inputs:

  - logfile: The file produced by anl_fridge_logger.py, which contains fridge
  temperature data.

  - hardware map yml file: The full path, starting at the home directory, to the
  hardware map.  This is used exclusively to turn off the IceBoard mezzanines.

- Returns: None

first_cycle.py is a script that runs the specialized script for the first cycle
of a cooldown. It should be called from the command line.

- Parameters: None

- Raw inputs:
  - logfile: The file produced by anl_fridge_logger.py, which contains fridge
  temperature data.

- Returns: None (but hopefully a nice, cold fridge!)

Wafer testing
-------------
Some functions for measuring and analyzing R(T) and G(T) are included.

- measure_GofT overbiases the bolometers at 650 mK, then drops temperature and
takes an I-V curve. It repeats this process for several temperatures in a
np.linspace that is specified at the start of the script. Things to change
before you run:

  1. hwm_dir should be set to your current hardware map (hwm_anl_complete.yml)

  2. Currently, the overbias is done by executing the anl_master_script.py file.
  This will be changed very soon.

    - Until it is fixed, anl_master_script should have zero_combs=True,
    overbias_bolos=True, and everything else set to False

  3. setpoints should be set to whatever you intend it to be (np.linspace with
  correct parameters)

- analyze_GofT is a file that has not been changed significantly from Adam's
original code. It includes some functions to measure and plot G(T) for the
bolometers.

- measure_RofT overbiases bolometers at 650 mK, turns on ledgerman, and sweeps
from high temperature to low temperature.

- rt_analysis_ledgerman parses the ledgerman information and provides the ability
to plot R(T) curves for each of the bolometers and find R_normal, R_parasitic,
and T_c for each bolometer. At present, it is best to be copied and pasted into
an ipython session, as it does not yet run straight through (it will break).

Miscellaneous
-------------
There are also some miscellaneous helper scripts for specific extra testing.

- sinusoidal.sinuvolt: generates sinusoidal voltages. The purpose of this
function has thus far been to generate a sinusoidally varying voltage to run
through a Helmholtz coil, for magnetic testing.

  - Parameters: driverfile, A, freq, tint, R, y (default=0), t0 (default=0)

    - driverfile: the driver file for the power supply, stored in he10_fridge_control/Lauren
    - A: amplitude (the highest number that you want the voltage to reach)
    - freq: the frequency of the sinusoidal curve (this is a mathematical
    property)
    - tint: the time interval between changing voltages
    - R: known resistance of a resistor in series with the power supply
    - y: the offset from 0 that you want the voltage to start fluctuating at
    - t0: start time (should usually be 0)
