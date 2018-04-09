/* This file is part of Indico.
 * Copyright (C) 2002 - 2018 European Organization for Nuclear Research (CERN).
 *
 * Indico is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * Indico is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Indico; if not, see <http://www.gnu.org/licenses/>.
 */

import moment from 'moment';
import 'antd/lib/avatar/style/css';
import 'antd/lib/grid/style/css';
import 'antd/lib/layout/style/css';
import 'antd/lib/menu/style/css';
import '../styles/main.scss';

import setupUserActions from './components/UserActions.jsx';

document.addEventListener("DOMContentLoaded", () => {
    moment.locale(Indico.User.language);
    setupUserActions(document.getElementById('rb-user-actions-container'), {
        isAdmin: true
    });
});
