README
===============
Lauren Saunders

February 20, 2017

This repository contains various Python scripts and tools for running the He10
cryostat at Argonne National Laboratory.

The repository is divided into three directories: control, measurement, and analysis.
The control directory contains important codes for working directly with the
cryostat to change temperatures. The measurement directory contains codes that
can be used to make specific measurements of SPT-3G detectors. The analysis
directory contains some codes that can be used to interpret and plot these measurements.

The control codes contained in this repository are intended for use only with the
He10 system; it is not designed to be used with the ADR cryostat housed in Building
360, although certain parts of the codes are intended to be universally applicable
to certain types of hardware (these cases are noted in the following sections).
The measurement and analysis codes are inteded for use with the SPT-3G detectors
and readout electronics, and work with algorithms stored in other repositories,
such as pydfmux.

Hardware
--------
Before we start on the codes that can be used to control the cryostat temperature
and take data, we need to make sure that all of the correct hardware is in place.
You will need 3-4 power supplies, 1 Lakeshore 340 temperature controller,
1 Lakeshore diode reader, a MOXA box with a connection to the computer and correct
cables, and cables connecting the thermometry to the cryostat.

Before you begin, ensure that all of the hardware is plugged in correctly. You
should connect the power supplies and Lakeshore boxes to the MOXA box using the
cables that came with the box (one side of the cable looks like an ethernet
connector, while the other connects to the port underneath the power cord on the
power supplies and Lakeshore boxes). The thermometry cables should be connected
at the top of the cryostat.

Turn on the power supplies and Lakeshore boxes. The power supplies and Lakeshore
boxes can have two types of connections: RS-232 and GPIB. The system that we
have in place uses the RS-232 setting, as it allows for our connection with the
MOXA box and also reduces noise in the system.

To check that the power supplies are in RS-232 mode, press the I/O Config button
and turn the knob until RS-232 is displayed. Press the I/O Config button again.
Now the power supply will display the baud rate. The factory setting for baud rate
is 9600, and this is the setting that we commonly use; however, if you wish to
change the baud rate, you can do so by turning the knobs. Pressing the I/O Config
button again will display the parity and number of data bits. The setting that
we commonly use is NONE 8 BITS, but turning the dial will allow you to change to
ODD 7 BITS or EVEN 7 BITS. Pressing the I/O Config button again will save the
configuration.

To check the connection settings for the Lakeshore boxes, you can press the
Interface button. This will display the serial interface settings, including
baud rate, parity, and number of data bits. The Next Setting button allows you
to move to the next listed parameter. The up and down buttons allow you to change
to the desired setting.

If you are installing a new Lakeshore box or power supply, you will need to make
note of the baud rate, parity, number of data bits, byte size, and MOXA port for
the new box. This information is important for setting up the interface software,
which will be covered in the next section.

Cryostat control
----------------
This section will first go through the files contained in the control directory,
and then give some specific directions on how to perform certain tasks.

1. Control files

  a. Driver files

      Driver files are text documents that contain the keys for communicating with
      the power supplies that control the pumps and switches for heating and cooling
      the stages in the cryostat. There are seven driver files, most of which refer to a
      particular part of the fridge and either a pump or a switch (He4p.txt refers to
      the Helium-4 pump; He4s.txt to the He-4 switch; He3ICp.txt to the He-3 Interstage pump;
      He3ICs.txt to the He-3 Interstage switch; He3UCp.txt to the Ultrastage pump;
      He3UCs.txt to the He-3 Ultrastage switch; and Helmholtz.txt refers to the power
      supply used in Helmholtz coil testing (see sinusoidal.py)). Each driver file
      must only refer to one output of a power supply, and must give a list of keys,
      as follows.

      - port: the serial address of the power supply you are trying to access

      - baudrate: the baud rate for the serial connection

      - parity: parity for the serial connection

      - stopbits: the stop bits for the serial connection

      - bytesize: the number of bits for the serial connection

      - timeout: a timeout for the serial connection

      - term: termination character needed to end a command

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

      In order to add a new power supply or change a current power supply to a
      different one, you need to create or edit a driver file to include the commands
      that the power supply needs to read in order to execute what you want. Certain
      keys (select, output_on, remote, and sep) may not be applicable to your power
      supply; in this case, they can simply be set to None. An example driver file
      can be seen below.

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

  b. PowerSupply class

      Simply writing a driver file does not provide any connection with the device
      you are trying to communicate with; it is just a template for things that
      you should be able to write to the power supply. The PowerSupply class,
      which is contained in powersupply.py, is the Python class which allows you
      to set up connections.

      PowerSupply requires you to supply a driver file, which it uses to write
      to the power supplies. Currently, PowerSupply assumes that your driver
      file is stored in anl_fridge_control/control. An example of setting up one
      of these class objects is shown below.

      .. code:: python

        He4p = powersupply.PowerSupply('He4p.txt')

      PowerSupply provides functions for connecting with the power supplies and
      troubleshooting issues. The callable functions are listed below.

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

      This is not a comprehensive list of every query and command you can possibly
      send to the power supply, simply a group of commands that are commonly needed
      for our purposes. It is possible to send a command outside of this list. To
      do so, you will need to know the exact message required to get the result
      you are looking for, which can be found in the manual for the power supply.
      Then, to send the message, you can use the serial_connex.write() and
      serial_connex.readline() functions, as shown below.

      .. code:: python

        He4p.serial_connex.write('APPL?\r\n')
        He4p.serial_connex.readline()

      The PowerSupply class is intended to be general enough to be used with
      any power supply, so long as it is provided a driver file that includes
      all of the correct statements for your power supply. At present, the class
      can only be used with a serial connection; however, it can be amended to
      include other types of connections, such as IEEE-488 or ethernet.

  c. TempControl class

      The TempControl class, which is contained in lakeshore.py, also uses
      a serial connection to communicate with the Lakeshore340 Temperature
      Controller. It does not require a driver file, and does not attempt to be
      general to all temperature controllers. It does, however, require a serial
      address and a list of four channel names. An example of creating this
      connection is shown below.

      .. code:: python

        ChaseLS = lakeshore.TempControl('/dev/ttyr18', ['A','B','C1','C2'])

      TempControl provides a few functions for connecting with the Lakeshore340
      box. These functions are listed below.

      - set_PID_temp: sets the temperature of the heater for the UC Head

        - Parameters: loop (1), temperature (float, in Kelvin)

        - Returns: None

      - set_heater_range: sets the heater range, which controls power to the PID

        - Parameters: heater range (integer 0-5)

        -Returns: None

      - get_temps: reads out the temperatures directly from the Lakeshore340

        - Parameters: None

        - Returns: dictionary of channel names and corresponding temperatures

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
