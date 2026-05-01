/**
 * Utils for type-based live message
 * by qwiglydee@gmail.com
 *
 * Best used with _stuff/live.py
 */

(function (ot) {
    if (window.ot === undefined) throw Error("otree-front-live requires otree-front");
    if (window.liveSocket === undefined) throw Error("otree-front-live requires live page");

    /**
     * Send a live message with a specified type and possible payload.
     *
     * @example
     *   sendLive("foo");
     *   sendLive("bar", { ... } );
     *
     * @param {string} type type of the message
     * @param {object} [data] message payload
     */
    function sendLive(type, data) {
        if (data) liveSend({ type, ...data });
        else liveSend({ type });
    }

    /**
     * Install handler for a live message .
     *
     * @example
     *  onLive('some_type', liveSomething);
     *
     *  function liveSomething(data) {
     *    // handle data
     *  }
     */
    function onLive(name, handler) {
        ot.onEvent("live", name, (e) => handler(e.detail.data));
    }

    window.liveSocket.onmessage = function (e) {
        // console.debug("live:", e.data);
        try {
            let data = JSON.parse(e.data);
            if (data.otree_success === false) throw Error("Server error");
            data = data.live_method_payload;
            if (!ot.isObject(data) || !data.type) throw Error("Bogus data received");
            ot.emitEvent("live", { name: data.type, data });
        } catch (e) {
            console.error(e);
            window.alert("Application error occured. The page terminates.");
            ot.submitPage();
        }
    };

    window.ot = Object.assign({}, window.ot, {
        onLive,
        sendLive,
    });
})(window.ot);
