class WebSocketService {
    constructor(url) {
        this._ws = null;
        this._state = null;
        this._url = url;
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
            const msg = JSON.parse(rawMsg.data);
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

        this._ws.onerror = response => {};
        this._ws.onclose = response => {};

        return this;
    }

    _reciveMsg(resMsg, callbackObject) {
        switch (resMsg.type) {
            case "fetch": null; break;
            case "sibscribe": null; break;
            case "fire": null; break;
            case "undefined": null; break;
            default: null; break;
        }
    }

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

    _getUid(postfix=(new Date()).getTime()) {
      const makeUid = length => Math.floor((1 + Math.random()) * Math.pow(10, length)).toString(16);
      return [8, 8, 8, 8].map(makeUid).concat([postfix]).join(':');
    };

    _prepareMsg(reqMsg) {
        reqMsg.uid = this._getUid();
        return reqMsg;
    }

    send(reqMsg, callback, persistent=false) {
        const preparedReqMsg = this._prepareMsg(reqMsg);
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
        return this.send({
            endpoint: endpoint,
            data: data
        }, callback, true);
    }

    unsibscribe(uid, onComplete) {
        return this.send({
            endpoint: "unsibscribe",
            data: {id: uid}
        }, onComplete, false);
    }
}

export {WebSocketService}