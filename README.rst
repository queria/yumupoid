YumUpoid
========
| *YUM Update Plasmoid*: KDE Plasmoid listing package updates available in yum. 
| Something like ``yum check-update`` does but stays on your KDE desktop/dashboard.

| Developed and tested on Fedora Linux.
| Should also work with other distributions where yum is used (please report).

Installation
============

- Getting sources::

  $ cd ~/
  $ git clone https://github.com/queria/yumupoid.git

- Then you can try running it with::

  $ plasmoidviewer ~/yumupoid

- Or install it using::

  $ cd ~/yumupoid
  $ zip -r ../yumupoid.zip .
  $ plasmapkg -i ../yumupoid.zip

- And maybe later uninstall it::

  $ plasmapkg -r yumupoid



Author
======
Originaly created by Queria Sa-Tas <public@sa-tas.net> at end of 2012.

Some parts of YumUpoid are *inspired by* or *directly taken
from* python sources of yum-cli_ and it should be
highlighted in their comment/docstring.

.. _yum-cli: http://yum.baseurl.org

License
=======
Copyright (c) 2012, Queria Sa-Tas
All rights reserved.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Library General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

See COPYING file for full copy of GNU GPL.

