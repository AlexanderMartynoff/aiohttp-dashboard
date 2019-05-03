<template>
    <b-card class="shadow traceback h-100" title="Stacktrace">
        <code>
            <pre>{{format(exception)}}</pre>
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