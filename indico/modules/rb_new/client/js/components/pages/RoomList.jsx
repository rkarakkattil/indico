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

/* eslint "react/forbid-component-props": "off" */

import propTypes from 'prop-types';
import React from 'react';
import {Card, Grid, Icon, Image} from 'semantic-ui-react';

import {Param, Plural, PluralTranslate, Singular} from 'indico/react/i18n';
import roomListFiltersFactory from '../../containers/RoomListFilters';

import './RoomList.module.scss';


const RoomListFilters = roomListFiltersFactory('roomList');

export default class RoomList extends React.Component {
    componentDidMount() {
        const {fetchRooms} = this.props;
        fetchRooms();
    }

    render() {
        const {rooms: {list}, fetchRooms} = this.props;
        return (
            <Grid columns={2}>
                <Grid.Column width={10}>
                    <div className="ui" styleName="room-list">
                        <RoomListFilters onConfirm={() => fetchRooms('roomList')} />
                        <div styleName="results-count">
                            <PluralTranslate count={list.length}>
                                <Singular>
                                    <Param name="count" value={list.length} /> result found
                                </Singular>
                                <Plural>
                                    <Param name="count" value={list.length} /> results found
                                </Plural>
                            </PluralTranslate>
                        </div>
                        <Grid columns={5} stackable>
                            {list.map((room) => (
                                <Grid.Column key={room.id}>
                                    <Room room={room} />
                                </Grid.Column>
                            ))}
                        </Grid>
                    </div>
                </Grid.Column>
            </Grid>
        );
    }
}


RoomList.propTypes = {
    rooms: propTypes.shape({
        list: propTypes.array,
        isFetching: propTypes.bool
    }).isRequired,
    fetchRooms: propTypes.func.isRequired
};


export function Room({room}) {
    return (
        <Card styleName="room-card">
            <Image src={room.small_photo_url} />
            <Card.Content>
                <Card.Description styleName="room-description">
                    {room.full_name}
                </Card.Description>
            </Card.Content>
            <Card.Content styleName="room-content" extra>
                <Icon name="user" /> {room.capacity}
                <span styleName="room-details">
                    {room.has_webcast_recording && <Icon name="video camera" />}
                    {!room.is_public && <Icon name="lock" />}
                </span>
            </Card.Content>
        </Card>
    );
}

Room.propTypes = {
    room: propTypes.object.isRequired
};
