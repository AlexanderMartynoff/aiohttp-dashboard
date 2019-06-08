import { Axios } from 'axios'
import axios from 'axios'
import _ from 'lodash'


export default class AxiosPlugin extends Axios {
    constructor({scope, event, interceptor, transform, ...options}) {
        super(_.merge(options, {
            transformRequest: _.concat(axios.defaults.transformRequest, transform.request),
            transformResponse: _.concat(axios.defaults.transformResponse, transform.response),
        }))

        this._scope = scope
        this._event = event
        this._interceptor = interceptor

        this.interceptors.request.use(options => {
            this._event.request.call(this._scope, {})
            return this._interceptor.request.call(this._scope, options)
        }, error => {
            this._event.error.call(this._scope, error)
            throw error
        })

        this.interceptors.response.use(response => {
            this._event.response.call(this._scope, {})
            return this._interceptor.response.call(this._scope, response)
        }, error => {
            this._event.error.call(this._scope, error)
            throw error
        })

    }

    static defaultsOptions(options) {

        return _.defaultsDeep(options, {

            event: {
                request() {},
                response() {},
                error() {},
            },

            interceptor: {
                request(options) {
                    return options
                },

                response(response) {
                    return response
                },
            },

            transform: {
                request: [
                    (data, headers) => {
                        return data
                    }
                ],

                response: [
                    (data) => {
                        return data
                    }
                ],
            }
        })
    }

    static install(Vue, options) {
        Vue.mixin({
            beforeCreate() {
                if (_.isEqual(this, this.$root)) {
                    Vue.prototype.$axios = new AxiosPlugin(AxiosPlugin.defaultsOptions({
                        scope: this,
                        ...this.$options.axios,
                    }))
                }
            }
        })
    }
}
