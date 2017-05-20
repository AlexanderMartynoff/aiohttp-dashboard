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
    import {eventBus} from '@/utils';

    export default {
        data: () => ({
            record: {},
            configuration: {},
            showWsLastPage: false,
            wsPageUpdateDelay: 2
        }),
        mixins: [WebSocketService.mixin],
        watch: {
            showWsLastPage: function() {
                this.emitSettingsChange();
            },
            wsPageUpdateDelay: function() {
                this.emitSettingsChange();
            },
        },
        methods: {
            emitSettingsChange: function() {
                return eventBus.$emit('settings:change', {
                    showWsLastPage: this.showWsLastPage,
                    wsPageUpdateDelay: this.wsPageUpdateDelay
                });
            },
            show: function() {
                this.$refs.settingsWindow.show();
            },
            onConfigurationChange: function() {
                return this.emitSettingsChange();
            }
        },
        created: function(){
            eventBus.$on('settings:fire', event => this.emitSettingsChange())
        }
    }
</script>


<style lang="stylus">
    .setting-window-item
        margin 5px 0
</style>