<template type="text/html">
    <b-modal ref="settingsWindow" title="Settings" size="md" hide-footer>
        <span class="setting-window-item">
            <b-form-fieldset
                label="websocket page update delay"
                state="default"
                :horizontal="true"
                :label-size="9">
                <b-form-input v-model="wsPageUpdateDelay"></b-form-input>
            </b-form-fieldset>
        </span>

        <span class="setting-window-item">
            <b-form-fieldset
                label="websocket message queue size"
                state="default"
                :horizontal="true"
                :label-size="9">
                <b-form-input v-model="wsQueueSize"></b-form-input>
            </b-form-fieldset>
        </span>

        <span class="setting-window-item">
            <b-form-fieldset
                label="http requests queue size"
                state="default"
                :horizontal="true"
                :label-size="9">
                <b-form-input v-model="httpQueueSize"></b-form-input>
            </b-form-fieldset>
        </span>

        <hr/>

        <span class="setting-window-item">
            <b-form-checkbox v-model="showWsLastPage" @change="onShowWsLastPageChange">
                follow for the last page on websocket messages
            </b-form-checkbox>
        </span>
        
    </b-modal>
</template>


<script type="text/javascript">
    import {WebSocketService} from '@/websocket';
    import {eventBus} from '@/utils';

    export default {
        data: () => ({
            record: {},
            showWsLastPage: false,
            wsPageUpdateDelay: 2,
            wsQueueSize: 50000,
            httpQueueSize: 50000
        }),
        mixins: [WebSocketService.mixin],
        methods: {
            show: function() {
                this.$refs.settingsWindow.show();
            },
            onShowWsLastPageChange: function() {
                eventBus.$emit('onShowWsLastPageChange', this.showWsLastPage);
            }
        }
    }
</script>


<style lang="stylus">
    .setting-window-item
        margin 5px 0
</style>