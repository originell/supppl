======================
supplierplan.at reader
======================

This is a cli script for fetching your *Supplierungen* (don't know the correct english term) from a website which many schools in Austria seem to use.

------------
Requirements
------------

* python_ >= 2.4
* BeautifulSoup_

.. _python: http://www.python.org/
.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/

Usage
-----

Usage: supppl.py -s YOURSCHOOLID -c YOURCLASS -u USERNAME -p PASSWORD

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SCHOOL, --schoolid=SCHOOL  your school's ID
  -c CL, --class=CL             your class
  -u USR, --user=USR            your school's username
  -p PW, --password=PW          your school's password
