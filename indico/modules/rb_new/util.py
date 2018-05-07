# This file is part of Indico.
# Copyright (C) 2002 - 2018 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from indico.core.db import db
from indico.modules.rb import rb_settings
from indico.modules.rb.models.rooms import Room


def search_for_rooms(filters, only_available=False):
    query = Room.query.filter(Room.is_active)

    if 'capacity' in filters:
        query = query.filter(db.or_(Room.capacity >= (filters['capacity'] * 0.8), Room.capacity.is_(None)))

    if 'room_name' in filters:
        query = query.filter(Room.name.ilike('%{}%'.format(filters['room_name'])))

    if only_available:
        start_dt, end_dt = filters['start_dt'], filters['end_dt']
        repeatability = (filters['repeat_frequency'], filters['repeat_interval'])
        query = query.filter(Room.is_active,
                             Room.filter_available(start_dt, end_dt, repeatability, include_pre_bookings=True,
                                                   include_pending_blockings=True))
        selected_period_days = (filters['end_dt'] - filters['start_dt']).days

        rooms = []
        for room in query:
            booking_limit_days = room.booking_limit_days or rb_settings.get('booking_limit')
            if booking_limit_days is not None and selected_period_days > booking_limit_days:
                continue
            if not room.check_bookable_hours(start_dt.time(), end_dt.time(), quiet=True):
                continue
            rooms.append(room)
    else:
        rooms = query.all()
    return rooms
