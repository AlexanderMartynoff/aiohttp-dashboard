<template type="text/html">
    <b-modal ref="settingsWindow" title="Settings" size="md" hide-footer>
        <span class="setting-window-item">
            <b-form-group horizontal
                          :label-cols="6"
                          breakpoint="md"
                          label="Websocket page update delay"
                          label-for="ws_page_update_delay">
                <b-form-input id="ws_page_update_delay" v-model="wsPageUpdateDelay"></b-form-input>
            </b-form-group>
        </span>

        <hr/>

        <span class="setting-window-item">
            <b-form-checkbox v-model="showWsLastPage">
                follow for the last page on websocket messages
            </b-form-checkbox>
        </span>
        
    </b-modal>
</template>


<script type="text/javascript">
    import {WebSocketService} from '@/websocket';

    export default {
        data: () => ({
            record: {},
            configuration: {},
            showWsLastPage: false,
            wsPageUpdateDelay: 2
        }),
        methods: {
            emitSettingsChange: function() {
            },
            show: function() {
                this.$refs.settingsWindow.show();
            },
            onConfigurationChange: function() {
                return this.emitSettingsChange();
            }
        },
    }
</script>