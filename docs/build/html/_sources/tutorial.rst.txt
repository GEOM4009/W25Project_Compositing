Tutorial
========

Here is how you should run this code.  

First start by editing the config file.  

Under the [Names] category, put your name as the user:

.. code-block:: ini
	
	user = Derek

Put the names of the contestants in too, for example: 

.. code-block:: ini

	contestants = 
	    Derek
	    Muhammad
	    Alana
	    Adriana
	    Christian
	    Hao
	    Alex
	    Leo
	    Caitlin
	    Benjamin
	    Zack
	    Anna

Then under the [Logging] category put the basename of the log file you want: 

.. code-block:: ini

	logfile = rps.log

And choose the level of logging you need (debug, info, warning, error)

.. code-block:: ini

	level = info

Under [Settings] you can decide to output the names in all caps

.. code-block:: ini

	uppercase = True

Then run the script at the command line using the following syntax: 

.. code-block:: bash

	python rps.py <config.cfg>

where the file ``<config.cfg>`` is the path to your config file. 


The script will then prompt you to enter winners of each match until a winner is declared. 


I hope you have a great game!  
