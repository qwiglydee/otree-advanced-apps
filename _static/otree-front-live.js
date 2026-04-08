/**
 * Utils for type-based live message
 * by qwiglydee@gmail.com
 */

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
    console.debug("live received:", e.data);
    try {
        let data = JSON.parse(e.data);
        if (data.otree_success === false) throw Error("Error occurred on the server. See server logs for details.");
        data = data.live_method_payload;
        if (!ot.isObject(data) || !data.type) throw Error("Invalid data received. Not compatible with otree-front-live");
        ot.emitEvent("live", { name: data.type, data });
    } catch (e) {
        console.error(e);
        window.alert("Communication error occured. The page terminates.");
        ot.submitPage();
    }
};
