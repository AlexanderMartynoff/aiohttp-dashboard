<template type="text/html">
    <b-modal ref="aboutWindow" title="About" size="lg" hide-footer>
        <ul class="list-group">
            <li class="list-group-item list-group-item-warning block" v-if="record.platform">
                <div><span>OS: {{record.platform}}</span></div>
                <div><small class="text-muted">Python: {{record.python}}</small></div>
            </li>
            <li class="list-group-item">
                <span class="key-name">aiohttp ver.:</span> <code>{{record.aiohttp}}</code>
            </li>
            <li class="list-group-item">
                <span class="key-name">debugger ver.:</span> <code>{{record.debugger}}</code>
            </li>
        </ul>
    </b-modal>
</template>


<script type="text/javascript">
    import {WebSocketService} from '@/websocket';

    export default {
        data: () => ({
            record: {}
        }),
        mixins: [WebSocketService.mixin],
        methods: {
            show: function() {
                this.$refs.aboutWindow.show();
                this.send('fetch.info', response => this.record = response.data);
            }
        }
    }
</script>