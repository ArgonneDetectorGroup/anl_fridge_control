===============
README
===============
Lauren Saunders
ljsaunders@uchicago.edu

Original: February 20, 2017
Revised: June 8, 2017

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
========
Room Temperature Hardware
-------------------------
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

Cold Hardware
-------------
It is important to check all of the hardware that will go inside of the cryostat
before you close up, as it will be impossible to fix any problems once you are
cold.

First, check your on-wafer hardware. Ensure that the connections between
LC boards and the connectors that will plug into the SQUID boards are not damaged
by checking them with a multimeter. Additionally, make sure that the flex cables
connecting your LC boards to either resistors or detectors are oriented correctly.
The flex cables should sit flat in the zif connectors, and should be oriented so
that left handed cables go to the left-most zif, and right-handed cables go to the
right-most zif. You should also make sure that all screws and washers are secured.

The next step is installation in the cryostat. Once you connect the wafer holder
to the stage and are satisfied with the direction that the cables are coming out
of the stage, you should carefully connect the connectors to the SQUID boards and
tighten the screws. You should then make sure that the cables do not come in contact
with any part of the milliKelvin stage or the 4K stage.

Before closing up you should also take a moment to check your thermometry. Ensure
that the resistor heater that is thermally connected to the ultracold stage is
properly connected and that the wires are not broken.

Cooling Down
============
Once the cryostat is closed and flipped over, you can connect the pulse tube and
then begin pumping down to vacuum. Plug the power cord into the pressure gauge,
and connect the hose of the vacuum pump to the valve at the top of the cryostat.
You should begin with the valve closed, and just pump down the hose with the
roughing pump. Once that is done, you can slowly open the valve, keeping the
pressure reading on the pump around 100 mTorr. You should not open the valve quickly
or begin pumping with the valve open because this may cause damage to the wafer.
Eventually, the valve will be open completely, which will be evident by a lack of
quick change in the pressure reading on the pump when you turn the valve.

After you have pumped down to _? mTorr, you can turn on the _? pump and allow the
pressure to come down to 1e-4 mTorr on the cryostat's pressure gauge. Once you
are done pumping down, you can close the cryostat's valve and turn off the vacuum
pumps, allowing the fans to slowly spin down. Once this is done, you can remove
the vacuum pump. To turn on the pulse tube, go into the inner hallway and turn
on the water. Then, you can power on the pulse tube (in that hallway) and turn
on the linear driver (a switch on the power strip in the cabinet with the
IceBoards). You should hear the pulse tube start pumping.

At this point, you should start logging the temperature. To learn how to start the
fridge logger, see the Fridge Logging section of this file. Once the main plate
temperature reading is below 3.5 K, you can start the first_cycle script, which
will cool the stages down to base temperature (see the Cryostat Control section
for more information).

Remote Sessions
===============
It is frequently useful to run certain codes in detachable windows, so that if
you are running something remotely, it will not crash should you lose your internet
connection. This is sometimes done with tmux sessions.

To open a tmux session, type into a terminal

.. code

  tmux new -s session_name

where session_name is the name of your new session (i.e. fridge_logger, measurement, etc.)
You will automatically attach to your session. To detach, type Ctrl+B, then D. To
re-attach, you can type

.. code

  tmux attach -t session_name

The tmux session usually prevents you from scrolling up to see earlier things in
the terminal. If you wish to do this, you can type Ctrl+B, then [. You can then
scroll up and down with your arrow keys, but cannot type anything. To get back to
the current line and begin typing again, you can type Ctrl+B, Q, Esc.

You can also use screen or a non-detachable terminal to run tests, but should be
sure that if anyone else might be running something in the cryostat remotely, they
know not to run anything simultaneously with you.

Fridge Logging
==============
The fridge_logger_anl.py code
(https://github.com/adamanderson/he10_fridge_control/blob/master/logger/fridge_logger_anl.py)
reads in data from Lakeshore340 and Lakeshore218 boxes. It then outputs data to
a .h5 file and a _read.h5 file, which are used to create plots and current
temperature readings on the website.

The fridge logger, as well as the web server that services it, are usually run in
detachable sessions. To start the logger, attach to your detachable session
(screen or tmux). Before you begin the logger, make sure that any computer
that might be attached your session has a connection with X windows available
(either ssh -X, or from the desktop in the lab). Then, in the terminal, type

.. code

  python /home/spt3g/he10_fridge_control/logger/fridge_logger_anl.py

You will then be prompted for a filename, which should be inputted as

.. code

  /home/spt3g/he10_logs/filename.h5

Once you have started the logger, you can create the webserver so that you can
monitor the temperatures. To do so, open another detachable session (screen or
tmux) and type in the terminal

.. code

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

Cryostat Control
================
This section will go through the files contained in the control directory, as well
as some specific directions on how to perform certain tasks.

Driver files
------------

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

.. code

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

PowerSupply class
-----------------
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

  import anl_fridge_control.control.powersupply as PS

  # set He4p as the connection dictated by driver file He4p.txt
  He4p = PS.PowerSupply('He4p.txt')

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

  # ask the power supply what voltage the output is set to
  He4p.serial_connex.write('APPL?\r\n')
  # read back the response from the power supply
  He4p.serial_connex.readline()

The PowerSupply class is intended to be general enough to be used with
any power supply, so long as it is provided a driver file that includes
all of the correct statements for your power supply. At present, the class
can only be used with a serial connection; however, it can be amended to
include other types of connections, such as IEEE-488 or ethernet.

TempControl class
-----------------
The TempControl class, which is contained in lakeshore.py, also uses
a serial connection to communicate with the Lakeshore340 Temperature
Controller. It does not require a driver file, and does not attempt to be
general to all temperature controllers. It does, however, require a serial
address and a list of four channel names. An example of creating this
connection is shown below.

.. code:: python

  import anl_fridge_control.control.lakeshore as LS

  ChaseLS = LS.TempControl('/dev/ttyr18', ['A','B','C1','C2'])

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
you can do so with the connex function. Once you look up the necessary commands
from the manual, you can send a message with the connex.write() function and
can read back a message with the connex.readline() function. An example is
shown below.

.. code:: python

  # ask the Lakeshore340 what the Celsius temperature of Channel A is
  ChaseLS.connex.write('CRDG? A\r\n')
  # read back the message from the Lakeshore340
  ChaseLS.connex.readline()

Serial connections
------------------
While the TempControl and PowerSupply classes are made to work with any number
of power supplies and Lakeshore340 boxes, our present setup only has 3 power
supplies and 1 Lakeshore340. Because these same connections need to be called
in order to make any temperature adjustment, the connections can all be set
up by importing serial_connections.py. This short python code establishes
connections and configures the Lakeshore340. If you wish to modify the
connections by adding or removing temperature controllers or power supplies,
you should ensure that you modify serial_connections.py in order to match
the setup you want. Many other scripts also import this one and use the
connections to change temperatures, so it is important to ensure that this
script is accurate to your setup. The current setup and definitions are listed
below.

- He4p: Helium-4 pump

- He4s: Helium-4 switch

- He3ICp: Helium-3 Interstage pump

- He3ICs: Helium-3 Interstage switch

- He3UCp: Helium-3 Ultracold pump

- He3UCs: Helium-3 Ultracold switch

- ChaseLS: Lakeshore340, with PID channel set to A (UC Stage)

Basic temperature control
-------------------------
Once you have imported serial_connections, it is relatively easy to change
the UC and IC stage temperatures. Some basic guidelines to changing temperature
are provided here; however, if you need more specific help, you should ask
Gensheng, who is very well-versed in the operation of this cryostat.

Generally, the temperature that is most relevant to our measurements is that
of the UC Stage. Currently, this is read by Channel A on the Lakeshore340, and
can usually be seen by looking at the display on this box. However, because
of the structure of the stage, a change in temperature of the UC Stage is also
influenced by a change in temperature of the IC Stage. Although the IC Stage
will usually be warmer than the UC Stage, it is important that when you change
the temperature of the UC Stage, you also similarly change that of the IC
Stage.

The first, and most easily-explained, way of changing the UC Stage temperature
is by setting temperatures on the PID heater, which is done through the
connection with the Lakeshore340. When you set the PID heater to a certain
temperature, you run a current through a resistor heater that is mounted in
thermal contact with the UC Stage. The heater can help you to settle at and
hold a particular temperature stably. In order to do this, you need to set both
the temperature that you want the UC Stage to reach, as well as a power level
for the heater (an integer between 0 and 5, inclusive). It is generally advisable
to leave at least one second between sending the commands for setting these
levels, as simultaneous signals to the Lakeshore340 are not always interpreted
well. To set a temperature with the PID heater, you can use the set_PID_temp()
function of TempControl, and to set a power level, you can use set_heater_range().
Keep in mind that set_PID_temp requires two inputs: the loop (almost always 1)
and the temperature in Kelvin (not milliKelvin). An example is shown below.

.. code:: python

  import anl_fridge_control.control.serial_connections as sc

  # set the heater temperature for the UC Stage to 500 mK
  sc.ChaseLS.set_PID_temp(1, 0.500)
  # set the heater power level to 2 (1.5 mW)
  sc.ChaseLS.set_heater_range(2)

When choosing a heater range, you should check the percentage of the heater's
power range that is being used. It is generally not a good idea to run the
heater at 100%, and when you are trying to heat the UC Stage, you should start
by heating the pumps (see next paragraph) so that the entire power burden is
not on the PID heater.

The heater is not the only way to change the temperature of the stage, and is
not always the best option (for example, while this is being written, the PID
heater is not currently functional due to a disconnection inside of the
cryostat). The other method of changing the temperature relies on the pumps
and switches, which refer to circuitry in the He-10 fridge itself. When you
change the voltage on the pumps, you are sending current through a resistor
that will heat up the charcoal inside of the corresponding refrigerator "head".
This ultimately causes the stage to heat. When you change the voltage on the
switches, you are sending a current through a gas-gap switch, which ultimately
causes the stage to cool. Keep in mind that you are not directly heating or
cooling the stage -- you are heating an element of the fridge, which causes
a change in temperature on the stage because of the thermal connection between
the fridge head and the stage. Because of this, it can take a few minutes for
a change in voltage to a pump or switch to cause a change in stage temperature
(usually, your pump will need to heat above 18 K to cause the stage to heat,
and a switch will need to heat above 13 K to start cooling the stage).

The pumps and switches are controlled by the three power supplies. Currently,
the pumps are Output 1 or the 25V output of each power supply, and the switches
are Output 2 or the 6V output of each power supply. Each power supply output
has a maximum voltage, which is established in the driver file, and most of
the current power supplies do not allow negative voltages. While you have
the IceBoard mezzanines turned on, it is not advisable to set a power supply
voltage greater than 4.00 V.

Because of the relationship between the pumps and switches, you should never
set a voltage for both a pump and a switch on the same head of the fridge.
Doing so will cause you to lose the ability to condense the liquid helium in
the head, and you will no longer be able to control the temperature. Always
ensure that the pump voltage is off before you turn on a switch voltage, and
ensure that the switch temperature is below 5.00 K and the switch voltage is
set to 0 before turning on a pump voltage.

For normal testing, you should usually leave the He-4 switch set to 4.00 V.
This helps the stages to stay cool enough to bring temperatures back down to
base if you need to. Other than that, it is usually advisable to use the He-3
Ultracold and Interstage pumps and switches together. An example of how to
set a voltage is shown below.

.. code:: python

  import anl_fridge_control.control.serial_connections as sc

  # set the He-3 Ultracold pump to 2.00 V
  sc.He3UCp.set_voltage(2.00)
  # set the He-3 Interstage pump to 2.00 V
  sc.He3ICp.set_voltage(2.00)

Usually, turning on a voltage to the pumps will raise the stage temperature,
and turning on a voltage to the switches will lower the stage temperature.

Automated cycling
-----------------
One of the most frequently useful control scripts is autocycle.py. This code
runs an automatic cycle of the fridge, which allows the liquid helium to
recondense and bring the stages back down to base temperature.

You should always make sure that the IceBoard mezzanines are powered off
before you run a cycle! It is generally a good idea to run a cycle at least
every other day, and every day that you are changing temperatures or using
the pumps and switches frequently. The cycle takes between 8 and 9 hours, so
it should be started at the end of a work day and left to run overnight. If
you have been using another connection via the MOXA box, you should make sure
that all of your MOXA cables are connected to the correct power supplies and
Lakeshore boxes, or the cycle will not run properly.

To run the automated cycle, you can type from the command line:

.. code

  python /home/spt3g/anl_fridge_control/control/autocycle.py

or, from an interactive Python session:

.. code:: python

  execfile('/home/spt3g/anl_fridge_control/control/autocycle.py')

The script will then prompt you with a raw_input to give the file name for the
fridge log (see the Fridge logging section). It will automatically fill in
the initial part of the file location (/home/spt3g/he10_logs/), and you should
type only the file name. Should you want to change the location of a log file,
you will need to edit this part of the script. Once you give the log file,
the script will automatically turn all switches, pumps, the PID heater, and
heater power setting to 0. After the cycle runs, it will return the stages to
base temperature, and the switches will be turned on (He4 switch to 4.00 V,
He3 IC switch to 4.00 V, and He3 UC switch to 3.00 V).

First cycle
-----------
While you will normally use autocycle.py to run a cycle, the first cycle of
a cooldown is slightly different (and takes longer). Therefore, there is a
separate code which runs an automated cycle at the beginning of the cooldown.
Like autocycle, first_cycle.py can be called from either the command line or
an interactive Python sessions, and asks you for a log file location, which you
should type in at the start of the cycle. For more information about cooldown
procedures, see the Cooldown Procedures section.

basic_functions.py
------------------
The last code in the control directory that is meant for temperature control
is basic_functions.py. This code contains a few functions that are either
called by other scripts or that are useful for day-to-day endeavors. These
functions are outlined below.

- zero_everything: This is usually a safety function, which turns off all of
the pumps, switches, and the PID heater, and sets the heater power to 0. It
is often called by other scripts in the case of a failure that would otherwise
allow the fridge to overheat, and is also called by autocycle at the beginning
of the script.

- finish_cycle: This function is run at the end of autocycle and first_cycle,
and waits for the heat exchanger temperature to rise slightly above its
minimum before turning off pumps and turning on switches. It is generally not
useful for calling on its own.

- start_of_day: This function is meant to run the first few procedural tasks
that need to be done at the beginning of a day, before other measurements are
made. It heats the UC Stage temperature to 650 mK, initializes the IceBoard,
heats and tunes squids, and takes a rawdump (see Testing Procedures). The
function is intended to help save time while you are waiting for all of these
things to happen, so that you can do other things. You need to specify whether
you will use the PID heater or only the pumps to heat the stage. You also should
ensure that the hardware map you are using in pydfmux/spt3g/northern_tuning_params
is correct.

Testing
=======
This section will go through different types of measurements for which there is
code in this directory. It is not an exhaustive list of all of the tests you
could possibly perform. These are simply tests that have previously been set up
for detector characterization and magnetic field testing.

First Steps
-----------
Before you begin doing any testing, you will need an accurate hardware map. A
hardware map is a group of files that specifies the frequency schedule of the
channels read out by each LC board, the mappings of channel numbers and LC boards
to mezzanines and modules on the IceBoard, and the list of hardware objects that
should be recognized by the computer. Hardware maps are contained in the
hardware_maps directory, and must be remade every time you cool down, especially
if you changed anything about your setup between cooldowns.

To make a hardware map, you need to start by heating and tuning SQUIDs and taking
a network analysis at low temperature (300 mK). Counterintuitively, you will need
to reference an existing hardware map in order to do these things; however, the
hardware map that you are referencing only needs to list the correct IceBoard(s),
mezzanines, SQUID Controllers, and SQUIDs, so you can either generate this by
hand or simply use an old hardware map that has these elements listed correctly.

Once you have your reference hardware map, you should edit the parameter file to
list this hardware map. To do so, open pydfmux/spt3g/northern_tuning_params.yaml
in a text editor, and specify your reference map as hwm_location at the beginning
of the document. You can also specify in this document whether you want to run a
mesh netanal. A mesh netanal takes a quick network analysis, then takes more data
points around the peaks in order to determine the exact frequencies of the peaks.
If you do not run a mesh network analysis, you will need to run a separate
algorithm to fit a function to the peaks.

After you have set your reference hardware map, you can open an interactive Python
session (it is usually preferable to do so in a detachable session) and run your
tests. To do so, type

.. code:: python

  # import the script
  import pydfmux.spt3g.northern_tuning_script as nts

  # heat squids
  nts.run_heat_squids()
  # wait for this to run (about 30 minutes)

  # tune squids
  nts.run_tune_squids()
  # wait for this to run (about 5 minutes)

  # take a rawdump to get a sense of noise
  nts.run_take_rawdump()
  # wait for this to run (about 1 minute)

  # run the network analysis
  nts.run_take_netanal()
  # wait for this to run (30-90 minutes)

After you have run the network analysis, you can make your hardware map. This can
be done by hand, by using the peaks outputted from the network analysis as the
channel frequencies, but doing so is arduous. You can more easily make the hardware
map using a premade code.

To make the hardware map using the code, you will first need to create a directory
for your hardware map, and then write a metaHWM.csv file. This lists the aspects
of the hardware map elements for each LC board. You will need to include the year,
wafer, iceboard, squid_board, squid, lc_chip, side, and flex_cable (a pair). You
will then need to make a build directory in the hardware map directory, and include
a make_hwm_anl_template file (you can find a sample file in pydfmux/spt3g). Once
you execute functions to make the hardware map, you will be able to see the hardware
map .yaml file, along with directories lcboards, mappings, and wafer.

The lcboards directory contains a .csv file for each LC board that you provided
in the hardware map. Each of these files contains a list of channel numbers and
a frequency for each channel number. These frequencies are the same as the peak
frequencies outputted by the network analysis.

The wafers directory contains a .csv file for each wafer you have provided in your
hardware map (frequently only one, but multiple can be present in the directory
if you have a need for that). If you have generated the hardware map using the
code procedure, then the wafer file has, for each channel, a physical_name
(pixel.band.polarization), name (year.side.flex_pair.squid.frequency),
observing_band (90, 150, or 220), overbias (True or False), pixel, pol_xy
(polarization), and tune (True or False).

The mappings directory contains at least one .csv file, which can contain mappings
for any or all channels in the wafer file. For each channel, the file lists the
lc_path (LC name as in the file name in lcboards/channel number in that
file), bolometer (wafer name/physical_name from the wafer file), and channel (in
the form iceboard/mezzanine/module/channel).

Once you have your hardware map, you should be able to perform whatever tasks you
need for testing. Note that you may need to set the overbias and tune settings  in
the wafer file to false for particular channels if they prevent the other channels
from overbiasing or dropping into the transition, as is sometimes the case.

Resistance vs. Temperature Measurement
--------------------------------------
One of the primary tests that we run to characterize detectors is one of resistance
vs. temperature, or R(T). The purpose of this test is to measure normal and
parasitic resistances, and to get an idea of what the detectors' critical temperature
is. The steps for taking this measurement are fairly simple.

1. With the UC Stage at 650 mK, overbias channels with a small amplitude (usually
amp=0.0002).

2. Start taking timestreamed data and record the time that you started.

3. Lower the temperature slowly from 650 mK to 350 mK.

4. End your data-taking and record the end time.

5. Begin taking data again, and record your start time.

6. Raise the temperature back up to 650 mK.

7. End your data-taking and record the end time.

Unfortunately, this process does take a few hours, so you should be prepared to
run it for that long. However, in order to make it easier to run this test at a
rate slow enough to make the temperature readings as close to accurate to the
temperatures of the detectors, there is a script that allows you to run downward
and upward temperature sweeps while recording data and the start and end times.
This script is measure_RofT.py, and is contained in the measurement directory.

The measure_RofT script allows you to start the R(T) measurement protocol from
any temperature below 650 mK. Before you begin, you should change the overbias
amplitude in northern_tuning_params.yaml to 0.0002. Then, you should be able to
start running the script. The script first turns off switches, in case they were
on, then heats the stage up to 650 mK using both the pumps and the PID heater,
overbiases the bolometers, and starts running ledgerman. It then steps down the
temperature until it reaches 400 mK, waits for the UC Stage to reach 400 mK, then
saves the start and end times for the downward sweep and terminates ledgerman.
It then restarts ledgerman with a new file name, and raises the temperature slowly
until it reaches 650 mK, waits for the UC Stage to reach this temperature, records
the start and end times for this sweep, and terminates ledgerman again.

!!four files
!!settings

In addition to measure_RofT, another similar script, take_rt_mini.py, can also
be used for this measurement. take_rt_mini is useful for R(T) measurements that
require more manual changes, such as measurements that use multiple IceBoards and
measurements that do not use the PID heater to change the temperature.

Resistance vs. Temperature Analysis
-----------------------------------
After you've taken the R(T) data, you will need to go through a few more steps
to produce plots and important data. A group of functions for this are contained
in analysis/rt_data_reader.py.

Before you start working with rt_data_reader, you should make a correct
flex_to_mezzmods dictionary. The structure of the dictionary is

.. code:: python

  flex_to_mezzmods = {'iceboard':{'lc_1':'mezzmod1', 'lc_2':'mezzmod2', ...}}

where mezzmod1 and mezzmod2 are the mezzanine and module numbers, combined into
one string (i.e. '11', '12', '13', '14', '21', '22', '23', '24'). This dictionary
is used in a couple of the the other functions to cycle through all of the
overbias files, so it is important to ensure that it is correct.

The first function in rt_data_reader is make_cfp_dict, which makes a dictionary
of conversion factors for each overbiased bolometer. The one input necessary is
the overbias directory, which was produced just before you started taking the
timestream. The function returns a dictionary mapping bolometer names to the
correct conversion factor.

Once you have the dictionary of conversion factors, you can run read_netcdf_fast,
which reads in the ledgerman output file. The required variables for this function
are the name of the file produced by ledgerman that you want to look at, and the
dictionary of conversion factors. This function returns three components: data_i,
which is a dictionary of the timestreamed I data indexed by bolometer name; data_q,
which is a dictionary of the timestreamed Q data indexed by bolometer name' and
time_sec, which is simply the time values recorded at every moment of datataking.

The ledgerman data, however, does not record the UC Stage temperature. For that,
you will need to reference the fridge logger file. Start by using the load_times
function in rt_data_reader, which takes an input of the pkl file for the times
outputted by measure_RofT, and returns the start and end times. Using these start
and end times, you can use the read_temps function to return corresponding lists
of temperature and time values. The inputs for that function are the temperature
log file, the start time, and the end time.

Unfortunately, the times in the temperature log file do not match up exactly with
those in the ledgerman data: ledgerman takes data at a much faster rate. The
model_temps function attempts to help with this discrepancy by making a fit of
the temperature and time data. The function requires you to input the temperature
values and time values from read_temps, and returns a function labeled tempfit.
Next, you can use downsample_data to return ds_temps, which uses tempfit to
interpolate temperatures based on time_sec, and ds_data, which is a dictionary
indexed by bolometer of the I data and Q data for each bolometer added in
quadrature. While it is very easy to modify downsample_data to only return a
portion of the data, it currently does not downsample in that way. However, this
data is still in units of current: it does not yet give us all of the information
that we are looking for. The final step for data conversion is convert_i2r, which
takes the I data (ds_data), IceBoard number, and overbias directory, divides the
voltage supplied in the overbias file by each datapoint in ds_data, and returns
data_r, a dictionary indexed by bolometer of the resistance data at each point.

A function called pickle_data, which takes ds_temps, data_r, and a new file name,
exists to help if you want to pickle the data that you have already interpreted,
in the event that you want to save it at that point. The purpose of this function
is to provide some consistency in producing these pickle files; it is not a strictly
necessary step in the analysis.

Once you have gotten arrays of resistance data that match with the temperature
values, you are ready to start making plots and finding detector characteristics.
make_data_dict is the first function for this purpose. make_data_dict takes data_r
and returns a dictionary of bolometers, which are matched to empty dictionaries.
To start filling the dictionary, you can go through the next two functions,
find_r_total and find_r_parasitic. The first of these requires inputs of data_r,
ds_temps, a minimum temperature, and the original data dictionary. It returns
a dictionary with a total resistance listed for each bolometer. Similarly,
find_r_parasitic requires inputs of data_r, ds_temps, a range of temperature values
to look at, and the data dictionary. It returns the same dictionary, this time
adding a parasitic resistance for each bolometer.

!!code snippets

Of course, this program is not perfect in its ability to catch bolometers that
do not behave as they should. The function plot_each_bolo allows you to make a
plot of the resistance data for each bolometer individually, and also plots with
this the total and parasitic resistances. Should you find a bolometer that does
not transition, it should be added to the list bad_bolos. Once you have examined
each bolometer, you can move on to finding the transition temperature.

You can find transition temperatures by running find_tc, which requires inputs of
data_r, ds_temps, a range in temperature over which to look for a transition, and
the data dictionary with parasitic and total resistance for each bolometer. It
will then attempt to find the transition temperature by searching in the temperature
range given. If the function is unable to find a transition temperature, it will
set the transition temperature in the dictionary to None. You can then plot the
resistance data, parasitic resistance line, total resistance line, and, if it is
not None, a line for the transition temperature for each bolometer individually
to ensure that the function has found a real transition. You now have a dictionary
of the information you needed to find to describe the characteristics of the
detectors that are evident from R(T). You will also need some of this information
(particularly the parasitic resistances) for future reference (i.e. when looking
at G(T)).

G(T) Measurement
----------------
A second test that is usually used in characerizing detectors involves dropping
the bolometers into the transition at different temperatures. Using this measurement,
we can look at the relationships between saturation power and temperature as well
as mathematically find what the critical temperature should be. The steps for
taking this measurement are:

1. Overbias bolometers at 650 mK

2. Lower the UC stage temperature to a desired temperature (usually below where
you expect the critical temperature to be)

3. Drop the bolometers into the transition

4. Zero combs

5. Raise the temperature back up to 650 mK

6. Repeat this process until you have dropped bolometers into the transition at
every desired temperature

This process is obviously tedious and time-consuming, which is why the measure_GofT
script is designed to run the entire process for you. measure_GofT can be found
in the measurement directory of anl_fridge_control.

The measure_GofT script is intended to be run only with a working PID heater. If
this part of you system is not functional, then the program will not run properly.
Also keep in mind that measure_GofT takes several hours to run, and can very easily
be the only test that you are able to run in a day.

The measure_GofT script starts out with a few user parameters that you should
check before running the program. They are:

- logfile: this is the path to the temperature log file

- setpoints: this is the array of temperatures at which you will be dropping bolometers
into the transition. The script uses a numpy linspace to set up this array, so the
first number should be the lowest temperature, the second number the highest temperature,
and the third number the number of points you want between these extrema (inclusive).

- wafertemps_filename: this is the full path to the pickle file that will be written
to record the temperatures at which the bolometers are put in the transition. You
will need to change this every time you run the script.

Once you have run the program, you will have a pickle file for the temperatures,
as well as several overbias_and_null and drop_bolos directories within the day's
output directory.

G(T) Analysis
-------------
Once you have taken 

Magnetic Field Testing
----------------------
It is sometimes useful to run tests that look at the behavior of detectors in
the presence of an outside magnetic field. In order to do this, you will need a
little more hardware than is usually present.

First, you will need wire coils. A pair of coils with 14 turns each and radii of
34 cm are already in the lab. You can use these individually if you do not necessarily
need a uniform field, or together as a pair. Second, you will need another power
supply to generate a current in the coil(s), and any electronics equipment that
might be necessary to safely connect the power supply and coils. Finally, you will
need a power resistor, which normally resides in the electronics drawer in the lab.
To hang your coil(s) close to the cryostat, it is usually easiest to use either
velcro or duct tape.

!! warnings

Once you have installed the coil(s) and connected your circuit, you will need to
connect the power supply to the MOXA box. You can do this with an extra MOXA cable,
or, if one does not exist, you can use the MOXA cable from the He-4 power supply.
If you decide to do this, be sure not to change any of the settings on the He-4
power supply and keep in mind that you can no longer remotely control that power
supply. You will need to reconnect it before you run a cycle.

The driver file for the power supply used in this setup is Helmholtz.txt, which
can be found in the control directory of anl_fridge_control. Make sure that you
edit this file to match your power supply and MOXA connection before you start
testing.

The functions that are useful for controlling the power supply to the coils can
be found in sinusoidal.py, which is in the control directory of anl_fridge_control.
This Python script contains two functions:

- sinuvolt: sets current and voltage of the power supply that vary sinusoidally.

  - Parameters:

    - driverfile: the driver file ('Helmholtz.txt')

    - A: the amplitude, or maximum voltage, that you want to reach

    - tint: the time interval that the code will wait before setting a new voltage
    and current

    - tf: the final time, at which the power supply will be reset to 0.0 V and 0.0 A

    - R: the resistance of the power resistor, used to calculate the correct current

    - freq: the frequency in radians/sec of the oscillation. Preset to 0.01

    - y: the offset of the initial voltage value from 0. Preset to 0

    - t0: the wait time at the beginning of the code before the voltage starts
    varying. Preset to 0

  - Returns: None

- helmholtz_test: collects a timestream while the voltage is varying. Parameters
match those of sinuvolt.

TODO: save what is output from power supply

Before running helmholtz_test, you should ensure that the correct hardware map(s)
and output filenames are listed at the beginning of the script. As a note, if you
are using two or more IceBoards, you should have a separate hardware map and
ledgerman process running for each IceBoard. This is because the IceBoard clocks
are not synced, and therefore trying to run ledgerman with multiple IceBoards causes
an error. Both functions in this script should be run from an interactive Python
session.

G(T)
----
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
