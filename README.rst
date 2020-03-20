View Spark Timeline
===================

.. image:: https://travis-ci.org/fpoli/view-spark-timeline.svg?branch=master
    :target: https://travis-ci.org/fpoli/view-spark-timeline

Command line application to visualize the timeline of Apache Spark executions, reading Spark's log files.

Can you spot the bottleneck from the following visualization?

.. image:: docs/example-timeline.svg


Image explanation
-----------------

On the vertical axis we have the executor cores (grouped by executor).
On the horizontal axis we have the time, going from left to right.
Each task is a horizontal bar that starts at a certain time on a core of an executor and ends after some time.
The color normally ranges from green, used for shorter tasks, to red, used for longer tasks. Failed tasks are black.
All the white space corresponds to some unused core.

Usually, the greener the image is, the better. If there is a bottleneck in the execution it is easy to spot the guilty task(s).
By opening the SVG in a browser and by moving the mouse over a task there should appear a tooltip with the task ID.
It is then useful to inspect the task using the standard Spark UI.


Installation
------------

This project requires Python 3.

.. code-block:: bash

    pip3 install view-spark-timeline


Example
-------

.. code-block:: bash

    view-spark-timeline -i examples/application_1472176676028_555248_1 -o docs/timeline.svg -u 1000


Output:

.. code-block:: text

    Read events from 'examples/application_1472176676028_555248_1'...
    Total cores: 32
    Total duration: 312.5s
    Number of tasks: 2990
    Min task duration: 0.0s
    Max task duration: 25.9s
    Cluster utilization: 57.70%
    Drawing events...
    Read events from 'examples/application_1472176676028_555248_1'...
    SVG size: 1500 160
    Saving SVG...


Usage
-----

.. code-block:: bash

    view-spark-timeline --help

Output:

.. code-block:: text

    usage: view-spark-timeline [-h] -i INPUT_LOG -o OUTPUT_IMAGE
                           [-t TIME_UNCERTAINTY] [-v]

    Visualize the timeline of a Spark execution from its log file. (v0.2.0)

    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT_LOG, --input-log INPUT_LOG
                            path to the spark's application log
    -o OUTPUT_IMAGE, --output-image OUTPUT_IMAGE
                            path of the output image
    -u TIME_UNCERTAINTY, --time-uncertainty TIME_UNCERTAINTY
                            maximum allowed time uncertainty (in ms) of the
                            timestamps in the log file. An high uncertainty
                            determines a slower, but more robust, execution.
                            (Default: 0)
    -v, --version         print version and exit


License
-------

Copyright (c) 2017-2020, Federico Poli <federpoli@gmail.com>

This project, except for files in the :literal:`lib` and :literal:`examples` folders, is released under the MIT license.
