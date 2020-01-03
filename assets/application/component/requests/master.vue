<template>
    <div class="container-fluid my-3">
        <div class="row mt-3 mb-3">
            <div class="col-md-12">
                <b-card class="shadow" header="Requests">
                    <datepicker-modal name="datepicker-datestart"></datepicker-modal>
                    <datepicker-modal name="datepicker-datestop"></datepicker-modal>


                    <b-form class="mb-3">
                        <b-row>
                            <b-col md="6">
                                <b-input-group>
                                    <div class="input-group-prepend">
                                        <button class="btn btn-primary" type="button">
                                            <i class="far fa-calendar-alt"></i>
                                        </button>
                                    </div>
                                    <datepicker-modal-input name="datestart"
                                                            datepicker-modal="datepicker-datestart"
                                                            v-model="filter.datestart">
                                    </datepicker-modal-input>
                                    <datepicker-modal-input name="datestop"
                                                            datepicker-modal="datepicker-datestop"
                                                            v-model="filter.datestop">
                                    </datepicker-modal-input>
                                </b-input-group>
                            </b-col>
                            <b-col md="3" class="mt-3 mt-md-0">
                                <b-input-group>
                                    <b-form-input v-model="filter.code" placeholder="HTTP code"/>
                                    <template #append>
                                        <b-dropdown text="Code" variant="success">
                                            <b-dropdown-item>404</b-dropdown-item>
                                            <b-dropdown-item>50*</b-dropdown-item>
                                        </b-dropdown>
                                    </template>
                                </b-input-group>
                            </b-col>
                            <b-col md="3" class="mt-3 mt-md-0">
                                <b-form-select v-model="filter.method">
                                    <option :value="null"></option>
                                    <option value="get">GET</option>
                                    <option value="post">POST</option>
                                    <option value="post">HEAD</option>
                                    <option value="post">DELETE</option>
                                    <option value="post">PUT</option>
                                </b-form-select>
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

    export default {
        data: () => ({
            filter: {
                datestart: new Date(),
                datestop: new Date(),
                method: null,
                code: null,
            },
            fields: [
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
                    key: 'time_start',
                    label: 'Begin time',
                    formatter: value => formatDateTime(value),
                },
                {
                    key: 'time_stop',
                    label: 'End time',
                    formatter: value => formatDateTime(value),
                },
            ],

            requests: [],
        }),
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
                        limit: 25,
                        skip: 0,
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

