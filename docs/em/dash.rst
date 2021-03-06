..
    Atlas of Information Management
    Copyright (C) 2020  Riverside Healthcare, Kankakee, IL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

****
Dash
****

EM2's dashboard is designed to give an admin a quick overview of the upcoming run schedule, listing of any failed jobs, and also recent run history.

Tables
######

EM2 is full of tables. These tables load through Ajax and run sql queries on the server. This enables us to load tables for millions of rows with minimal delay.

Tables can be sorted "globally" using the dropdown selector, or the 10 rows displayed on the screen can also be sorted by clicking on the headers.

Table can by "auto reloaded", refreshed, copied, or downloaded.

.. image:: ../images/em2-table.png
  :alt: Demo Image
