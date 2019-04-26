<template>
    <b-card class="shadow traceback" title="Stacktrace">
        <code>
            <pre><span class="traceback-line" v-for="line in exception.traceback"><span class="traceback-line-code">{{line}}</span><br/></span></pre>
        </code>
        <code>
            <pre>{{exception.class}}: {{exception.message}}</pre>
        </code>
    </b-card>
</template>

<script>
export default {
    props: {
        exception: Object
    },

    methods: {
        format: function (exception) {
            if (exception && exception.traceback) {
                return exception.traceback.join('\r\n')
            }
        },
    }
}
</script>