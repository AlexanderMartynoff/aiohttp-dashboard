<template>
    <div class="container-fluid my-3">
        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow" header="Requests">
                    <datepicker-modal name="datepicker-datestart"/>
                    <datepicker-modal name="datepicker-datestop"/>

                    <b-form class="mb-3">
                        <b-row>
                            <b-col md="5">
                                <b-input-group>
                                    <div class="input-group-prepend">
                                        <button class="btn btn-primary" type="button">
                                            <i class="far fa-calendar-alt"></i>
                                        </button>
                                    </div>
                                    <datepicker-modal-input name="datestart"
                                                            datepicker-modal="datepicker-datestart"
                                                            v-model="filter.timestart"/>
                                    <datepicker-modal-input name="datestop"
                                                            datepicker-modal="datepicker-datestop"
                                                            v-model="filter.timestop"/>
                                </b-input-group>
                            </b-col>
                            <b-col md="3" class="mt-3 mt-md-0">
                                <b-input-group>
                                    <b-form-input v-model="filter.code" placeholder="Status ..."/>
                                    <template #append>
                                        <b-dropdown text="Code" variant="primary">
                                            <b-dropdown-item v-for="httpStatus in httpStatuses"
                                                             @click="filter.code = httpStatus.value">
                                                {{httpStatus.title}}
                                            </b-dropdown-item>
                                        </b-dropdown>
                                    </template>
                                </b-input-group>
                            </b-col>
                            <b-col md="3" class="mt-3 mt-md-0">
                                <b-form-select v-model="filter.method">
                                    <option :value="null">All methods</option>
                                    <option value="GET">Get</option>
                                    <option value="POST">Post</option>
                                    <option value="HEAD">Head</option>
                                    <option value="DELETE">Delete</option>
                                    <option value="PUT">Put</option>
                                </b-form-select>
                            </b-col>
                            <b-col md="1" class="mt-3 mt-md-0">
                                <b-button variant="primary" class="justify-btn" @click="loadRequests">
                                    <i class="fas fa-search"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                    </b-form>
                    <b-table @row-clicked="(item, index) => details(item.id, index)" 
                             :responsive="true"
                             :hover="true"
                             :items="requests"
                             :fields="fields"
                             :selectable="true"
                             :show-empty="true"
                             empty-html="Records not found"
                             class="table-pointer"
                             striped>

                    <template slot="status" slot-scope="record">
                        <span class="badge" :class="getStatusClassByCode(record.value)">
                            {{record.value}}
                        </span>
                    </template>

                    </b-table>
                </b-card>
            </div>
        </div>
    </div>
</template>


<script type="text/javascript">
    import _ from 'lodash'
    import {EventService} from '@/websocket'
    import {router} from '@/router'
    import {formatDateTime} from '@/misc'
    import {
        differenceInMilliseconds,
        startOfDay,
        addDays,
    } from 'date-fns'

    export default {
        data: () => {
            const timestart = startOfDay(new Date())
            const timestop = addDays(timestart, 1)
            
            return {
                filter: {
                    timestart,
                    timestop,
                    method: null,
                    code: null,
                },
                httpStatuses: [
                    {title: 'All status', value: null},
                    {title: 'Server errors (5xx)', value: '5.*'},
                    {title: 'Client errors (4xx)', value: '4.*'},
                    {title: 'Redirection (3xx)', value: '3.*'},
                    {title: 'Success (2xx)', value: '2.*'},
                    {title: 'Informational (1xx)', value: '1.*'},
                ],
                fields: [
                    {
                        key: 'timestart',
                        label: 'Time',
                        formatter: value => formatDateTime(value),
                    },
                    {
                        key: 'status',
                        label: 'Status',
                    },
                    {
                        key: 'path',
                        label: 'Path',
                    },
                    {
                        key: 'method',
                        label: 'Method',
                    },
                    {
                        key: 'duration',
                        label: 'Duration',
                        formatter: (value, key, item) => (differenceInMilliseconds(
                            new Date(item.timestop),
                            new Date(item.timestart)
                        ) + ' ms'),
                    },
                ],

                requests: [],
            }

        },
        methods: {
            details: function(id) {
                router.push({path: `/request/detail/${id}`})
            },

            getStatusClassByCode(code) {
                if (_.startsWith(code, 4)) {
                    return 'badge-warning'
                } else if (_.startsWith(code, 5)) {
                    return 'badge-danger'
                } else {
                    return 'badge-success'
                }
            },

            loadRequests() {
                return this.$axios.get('/api/request', {
                    params: {
                        timestart: this.filter.timestart.getTime(),
                        timestop: this.filter.timestop.getTime(),
                        method: this.filter.method || null,
                        statuscode: this.filter.code || null,
                    },
                }).then(requests => {
                    this.requests = requests.records
                }) 
            }
        },

        created: function() {
            this.$event = EventService.create()

            this.$event.on('http', message => {
                this.loadRequests()
            });
        },
        
        destroyed: function() {
            this.$event.off()
        }
    }
</script>

