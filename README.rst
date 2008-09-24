==========================
supplierplan.at reader lib
==========================

This is a python library for fetching infos from supplierplan.at

------------
Requirements
------------

* python_ >= 2.4
* BeautifulSoup_

.. _python: http://www.python.org/
.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/

Documentation
=============
::

    from supppl import Supplierplan

    sp = Supplierplan(school=SCHOOLID, usr=USRNAME, pw=PASS, cl=CLASS)
    if sp.check_supps():
        plan = sp.proc_html()
        print plan
