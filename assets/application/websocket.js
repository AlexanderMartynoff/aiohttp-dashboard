import {port} from '@/utils';
import config from '@/config';


class WebSocketService {
    constructor(url) {
        this._ws = null;
        this._state = null;
        this._url = url;
        this._onOpenWaiters = [];
        this._responseHandlres = {};
        this._subscribeHistory = [];
    }

    _resetState() {
        this._ws = null;
        this._onOpenWaiters = [];
        this._responseHandlres = {};
    }

    _getState() {
        return (this._ws || {}).readyState;
    }

    _open(success) {
        if (this._ws) {
            success(this._ws);
            return this;
        }
        
        this._onOpenWaiters.push(success);

        this._ws = new WebSocket(this._url);
        
        this._ws.onopen = response => {
            this._onOpenWaiters.forEach(waiter => waiter(this._ws));
        };
        
        this._ws.onmessage = rawMsg => {
            let msg;
            try {
                msg = JSON.parse(rawMsg.data);
            } catch (error) {
                console.log(`error while parse msg ${error.toString()}`);
                return;
            }

            const callbackObject = this._responseHandlres[msg.uid];

            if (!callbackObject) {
                console.log(`not found callbackObject by ${msg.uid}`);
                return;
            }

            if (callbackObject.callback) {
                callbackObject.callback(msg);
            } else {
                console.log(`not defined callback in callbackObject by ${msg.uid}`);
            }

            if (!callbackObject.persistent) {
                delete this._responseHandlres[msg.uid];
            }
        };

        this._ws.onerror = response => {
            console.log(response);
        };

        this._ws.onclose = response => {
            this._tryReconnect(2000);
        };

        return this;
    }

    _tryReconnect(delay) {
        this._resetState();
        setTimeout(() => this._restoreSubscribe(), delay);
    };

    _do(success, fail=() => {}) {
        switch(this._getState()) {
            case WebSocket.CONNECTING: this._onOpenWaiters.push(success); break;
            case WebSocket.OPEN: success(this._ws); break;
            default: this._open(success);
        }
    }

    _sendToWs(json) {
        this._ws.send(JSON.stringify(json));
    };

    _getUid(prefix=(new Date()).getTime()) {
        const makeUid = length => Math.floor((1 + Math.random()) * Math.pow(10, length)).toString(16);
        return [prefix].concat([10].map(makeUid)).join('.');
    };

    _prepareMsg(reqMsg) {
        reqMsg.uid = this._getUid();
        return reqMsg;
    }
    
    send(reqMsgOrEndpoint, callback, persistent=false) {
        const preparedReqMsg = this._prepareMsg(typeof reqMsgOrEndpoint === 'string' ?
            {endpoint: reqMsgOrEndpoint} : reqMsgOrEndpoint);

        this._do(() => {
            this._responseHandlres[preparedReqMsg.uid] = {
                callback,
                persistent
            };
            this._sendToWs(preparedReqMsg);
        });
        return preparedReqMsg.uid;
    }

    subscribe(endpoint, callback, data) {
        this._subscribeHistory.push({endpoint, callback, data});
        return this._doSubscribe(endpoint, callback, data);
    }

    unsibscribe(uid, onComplete) {
        return this.send({
            endpoint: "unsibscribe",
            data: {id: uid}
        }, onComplete, false);

        delete this._responseHandlres[uid];
    }

    _doSubscribe(endpoint, callback, data) {
        return this.send({
            endpoint: endpoint,
            data: data
        }, callback, true);
    }

    _restoreSubscribe() {
        this._subscribeHistory.forEach(record => this._doSubscribe(
            record.endpoint, record.callback, record.data));
    }
}

const instance = WebSocketService.instance = new WebSocketService(config.wsApiEndpoint);

WebSocketService.mixin = {
    methods: {
        send: (...args) => instance.send.apply(instance, args),
        subscribe: (...args) => instance.subscribe.apply(instance, args),
        unsibscribe: (...args) => instance.unsibscribe.apply(instance, args)
    }
};

export {WebSocketService}